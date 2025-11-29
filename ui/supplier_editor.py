from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QLineEdit, QTextEdit, QComboBox, QPushButton, QLabel, QMessageBox, QListWidget)
from PySide6.QtCore import Qt
from ui.assets import play_sound
from database import get_db
from models import Supplier
from settings_manager import get_settings

class SupplierEditorDialog(QDialog):
    def __init__(self, parent=None, supplier=None):
        super().__init__(parent)
        self.supplier = supplier
        self.is_new = supplier is None
        
        self.setWindowTitle("New Supplier" if self.is_new else "Edit Supplier")
        self.setMinimumWidth(500)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Form
        form_layout = QFormLayout()
        
        self.supplier_name_input = QLineEdit()
        self.supplier_name_input.setPlaceholderText("Required")
        form_layout.addRow("Supplier Name:", self.supplier_name_input)
        
        self.contact_name_input = QLineEdit()
        form_layout.addRow("Contact Name:", self.contact_name_input)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("email@example.com")
        form_layout.addRow("Email:", self.email_input)
        
        self.phone_input = QLineEdit()
        form_layout.addRow("Phone:", self.phone_input)
        
        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(80)
        self.address_input.setPlaceholderText("Street Address, City, State, Postcode")
        form_layout.addRow("Address:", self.address_input)
        
        self.services_input = QTextEdit()
        self.services_input.setMaximumHeight(80)
        self.services_input.setPlaceholderText("Products/Services this supplier provides")
        form_layout.addRow("Services/Supplies:", self.services_input)
        
        # Account Type dropdown
        self.account_type_input = QComboBox()
        settings = get_settings()
        self.account_type_input.addItems(settings.get_account_types())
        form_layout.addRow("Account Type:", self.account_type_input)
        
        # Freight Methods (multi-select)
        freight_label = QLabel("Freight Methods:")
        freight_label.setToolTip("Hold Ctrl/Cmd to select multiple")
        self.freight_methods_list = QListWidget()
        self.freight_methods_list.setSelectionMode(QListWidget.MultiSelection)
        self.freight_methods_list.setMaximumHeight(100)
        for method in settings.get_freight_methods():
            self.freight_methods_list.addItem(method)
        form_layout.addRow(freight_label, self.freight_methods_list)
        
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(100)
        self.notes_input.setPlaceholderText("Additional notes about this supplier")
        form_layout.addRow("Notes:", self.notes_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("Save Supplier")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.save_btn.clicked.connect(self.save_supplier)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        
        layout.addLayout(btn_layout)
        
        # Load existing data if editing
        if not self.is_new:
            self.load_supplier_data()
            
    def load_supplier_data(self):
        self.supplier_name_input.setText(self.supplier.supplier_name)
        self.contact_name_input.setText(self.supplier.contact_name or "")
        self.email_input.setText(self.supplier.email or "")
        self.phone_input.setText(self.supplier.phone or "")
        self.address_input.setPlainText(self.supplier.address or "")
        self.services_input.setPlainText(self.supplier.services_supplies or "")
        self.account_type_input.setCurrentText(self.supplier.account_type or "")
        
        # Select multiple freight methods
        if self.supplier.freight_method:
            selected_methods = [m.strip() for m in self.supplier.freight_method.split(",")]
            for i in range(self.freight_methods_list.count()):
                item = self.freight_methods_list.item(i)
                if item.text() in selected_methods:
                    item.setSelected(True)
        
        self.notes_input.setPlainText(self.supplier.notes or "")
        
    def save_supplier(self):
        # Validate
        supplier_name = self.supplier_name_input.text().strip()
        if not supplier_name:
            play_sound("caution")
            QMessageBox.warning(self, "Validation Error", "Supplier Name is required.")
            return
            
        try:
            db = next(get_db())
            
            # Get selected freight methods
            selected_methods = [item.text() for item in self.freight_methods_list.selectedItems()]
            freight_methods_str = ", ".join(selected_methods) if selected_methods else None
            
            if self.is_new:
                supplier = Supplier(
                    supplier_name=supplier_name,
                    contact_name=self.contact_name_input.text().strip() or None,
                    email=self.email_input.text().strip() or None,
                    phone=self.phone_input.text().strip() or None,
                    address=self.address_input.toPlainText().strip() or None,
                    services_supplies=self.services_input.toPlainText().strip() or None,
                    account_type=self.account_type_input.currentText() or None,
                    freight_method=freight_methods_str,
                    notes=self.notes_input.toPlainText().strip() or None
                )
                db.add(supplier)
            else:
                self.supplier.supplier_name = supplier_name
                self.supplier.contact_name = self.contact_name_input.text().strip() or None
                self.supplier.email = self.email_input.text().strip() or None
                self.supplier.phone = self.phone_input.text().strip() or None
                self.supplier.address = self.address_input.toPlainText().strip() or None
                self.supplier.services_supplies = self.services_input.toPlainText().strip() or None
                self.supplier.account_type = self.account_type_input.currentText() or None
                self.supplier.freight_method = freight_methods_str
                self.supplier.notes = self.notes_input.toPlainText().strip() or None
                
            db.commit()
            play_sound("celebration")
            self.accept()
            
        except Exception as e:
            play_sound("caution")
            QMessageBox.critical(self, "Error", f"Failed to save supplier:\\n{str(e)}")
