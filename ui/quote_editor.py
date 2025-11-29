from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QLineEdit, QTextEdit, QComboBox, QPushButton, QLabel, QMessageBox,
                               QDateEdit, QTableWidget, QTableWidgetItem, QSpinBox, QDoubleSpinBox,
                               QHeaderView, QAbstractItemView)
from PySide6.QtCore import Qt, QDate
from ui.assets import play_sound, get_icon
from database import get_db
from models import Quote, QuoteItem, QuoteStatus
from datetime import datetime, timedelta

class QuoteEditorDialog(QDialog):
    def __init__(self, parent=None, quote=None):
        super().__init__(parent)
        self.quote = quote
        self.is_new = quote is None
        
        self.setWindowTitle("New Quote" if self.is_new else f"Edit Quote - {quote.quote_number}")
        self.setMinimumSize(800, 600)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Header Form
        form_layout = QFormLayout()
        
        self.customer_input = QLineEdit()
        self.customer_input.setPlaceholderText("Required")
        form_layout.addRow("Customer Name:", self.customer_input)
        
        self.quote_date_input = QDateEdit()
        self.quote_date_input.setCalendarPopup(True)
        self.quote_date_input.setDate(QDate.currentDate())
        form_layout.addRow("Quote Date:", self.quote_date_input)
        
        self.expiry_date_input = QDateEdit()
        self.expiry_date_input.setCalendarPopup(True)
        self.expiry_date_input.setDate(QDate.currentDate().addDays(30))
        form_layout.addRow("Expiry Date:", self.expiry_date_input)
        
        self.status_input = QComboBox()
        self.status_input.addItems([status.value for status in QuoteStatus])
        form_layout.addRow("Status:", self.status_input)
        
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(60)
        self.notes_input.setPlaceholderText("Quote notes or terms...")
        form_layout.addRow("Notes:", self.notes_input)
        
        layout.addLayout(form_layout)
        
        # Line Items Section
        items_label = QLabel("Line Items")
        items_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(items_label)
        
        # Line Items Table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels(["Description", "Qty", "Unit Price", "Total", ""])
        self.items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.items_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.items_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.items_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.items_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.items_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.items_table.setMinimumHeight(200)
        layout.addWidget(self.items_table)
        
        # Add Line Item Button
        add_item_btn = QPushButton("Add Line Item")
        add_item_btn.setIcon(get_icon("fa5s.plus", color="#27ae60"))
        add_item_btn.clicked.connect(self.add_line_item)
        layout.addWidget(add_item_btn)
        
        # Totals Section
        totals_layout = QHBoxLayout()
        totals_layout.addStretch()
        
        totals_form = QFormLayout()
        self.subtotal_label = QLabel("$0.00")
        self.subtotal_label.setStyleSheet("font-size: 14px;")
        totals_form.addRow("Subtotal:", self.subtotal_label)
        
        self.tax_label = QLabel("$0.00")
        self.tax_label.setStyleSheet("font-size: 14px;")
        totals_form.addRow("Tax (10%):", self.tax_label)
        
        self.total_label = QLabel("$0.00")
        self.total_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        totals_form.addRow("Total:", self.total_label)
        
        totals_layout.addLayout(totals_form)
        layout.addLayout(totals_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("Save Quote")
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
        self.save_btn.clicked.connect(self.save_quote)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        
        layout.addLayout(btn_layout)
        
        # Load existing data if editing
        if not self.is_new:
            self.load_quote_data()
        else:
            # Add one empty line item
            self.add_line_item()
            
    def add_line_item(self):
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)
        
        # Description
        desc = QLineEdit()
        desc.textChanged.connect(self.calculate_totals)
        self.items_table.setCellWidget(row, 0, desc)
        
        # Quantity
        qty = QSpinBox()
        qty.setMinimum(1)
        qty.setMaximum(9999)
        qty.setValue(1)
        qty.valueChanged.connect(lambda: self.update_line_total(row))
        self.items_table.setCellWidget(row, 1, qty)
        
        # Unit Price
        price = QDoubleSpinBox()
        price.setPrefix("$")
        price.setMinimum(0)
        price.setMaximum(999999)
        price.setDecimals(2)
        price.valueChanged.connect(lambda: self.update_line_total(row))
        self.items_table.setCellWidget(row, 2, price)
        
        # Total (read-only)
        total = QTableWidgetItem("$0.00")
        total.setFlags(total.flags() & ~Qt.ItemIsEditable)
        self.items_table.setItem(row, 3, total)
        
        # Delete Button
        delete_btn = QPushButton("Delete")
        delete_btn.setIcon(get_icon("fa5s.trash", color="#e74c3c"))
        delete_btn.clicked.connect(lambda: self.delete_line_item(row))
        self.items_table.setCellWidget(row, 4, delete_btn)
        
    def delete_line_item(self, row):
        self.items_table.removeRow(row)
        self.calculate_totals()
        
    def update_line_total(self, row):
        qty_widget = self.items_table.cellWidget(row, 1)
        price_widget = self.items_table.cellWidget(row, 2)
        
        if qty_widget and price_widget:
            qty = qty_widget.value()
            price = price_widget.value()
            total = qty * price
            
            total_item = self.items_table.item(row, 3)
            if total_item:
                total_item.setText(f"${total:.2f}")
                
        self.calculate_totals()
        
    def calculate_totals(self):
        subtotal = 0
        
        for row in range(self.items_table.rowCount()):
            total_item = self.items_table.item(row, 3)
            if total_item:
                total_text = total_item.text().replace("$", "")
                try:
                    subtotal += float(total_text)
                except:
                    pass
                    
        tax = subtotal * 0.10
        total = subtotal + tax
        
        self.subtotal_label.setText(f"${subtotal:.2f}")
        self.tax_label.setText(f"${tax:.2f}")
        self.total_label.setText(f"${total:.2f}")
        
    def load_quote_data(self):
        self.customer_input.setText(self.quote.customer_name)
        self.quote_date_input.setDate(QDate(self.quote.quote_date))
        if self.quote.expiry_date:
            self.expiry_date_input.setDate(QDate(self.quote.expiry_date))
        self.status_input.setCurrentText(self.quote.status)
        self.notes_input.setPlainText(self.quote.notes or "")
        
        # Load line items
        db = next(get_db())
        items = db.query(QuoteItem).filter(QuoteItem.quote_id == self.quote.id).all()
        
        for item in items:
            row = self.items_table.rowCount()
            self.items_table.insertRow(row)
            
            desc = QLineEdit(item.description)
            desc.textChanged.connect(self.calculate_totals)
            self.items_table.setCellWidget(row, 0, desc)
            
            qty = QSpinBox()
            qty.setValue(item.quantity)
            qty.valueChanged.connect(lambda: self.update_line_total(row))
            self.items_table.setCellWidget(row, 1, qty)
            
            price = QDoubleSpinBox()
            price.setPrefix("$")
            price.setValue(item.unit_price / 100)
            price.setDecimals(2)
            price.valueChanged.connect(lambda: self.update_line_total(row))
            self.items_table.setCellWidget(row, 2, price)
            
            total = QTableWidgetItem(f"${item.total / 100:.2f}")
            total.setFlags(total.flags() & ~Qt.ItemIsEditable)
            self.items_table.setItem(row, 3, total)
            
            delete_btn = QPushButton("Delete")
            delete_btn.setIcon(get_icon("fa5s.trash", color="#e74c3c"))
            delete_btn.clicked.connect(lambda checked, r=row: self.delete_line_item(r))
            self.items_table.setCellWidget(row, 4, delete_btn)
            
        self.calculate_totals()
        
    def save_quote(self):
        # Validate
        customer_name = self.customer_input.text().strip()
        if not customer_name:
            play_sound("caution")
            QMessageBox.warning(self, "Validation Error", "Customer Name is required.")
            return
            
        if self.items_table.rowCount() == 0:
            play_sound("caution")
            QMessageBox.warning(self, "Validation Error", "At least one line item is required.")
            return
            
        try:
            db = next(get_db())
            
            # Convert totals to cents
            subtotal_cents = int(float(self.subtotal_label.text().replace("$", "")) * 100)
            tax_cents = int(float(self.tax_label.text().replace("$", "")) * 100)
            total_cents = int(float(self.total_label.text().replace("$", "")) * 100)
            
            if self.is_new:
                # Generate quote number
                # Find the latest quote number starting with "QN"
                last_quote = db.query(Quote).filter(Quote.quote_number.like("QN%")).order_by(Quote.id.desc()).first()
                
                if last_quote and last_quote.quote_number:
                    try:
                        last_num = int(last_quote.quote_number[2:])
                        new_num = last_num + 1
                    except ValueError:
                        new_num = 1
                else:
                    new_num = 1
                
                quote_number = f"QN{new_num:06d}"
                
                quote = Quote(
                    quote_number=quote_number,
                    customer_name=customer_name,
                    quote_date=self.quote_date_input.date().toPython(),
                    expiry_date=self.expiry_date_input.date().toPython(),
                    status=self.status_input.currentText(),
                    notes=self.notes_input.toPlainText().strip() or None,
                    subtotal=subtotal_cents,
                    tax=tax_cents,
                    total=total_cents
                )
                db.add(quote)
                db.flush()  # Get the ID
                
                # Save line items
                for row in range(self.items_table.rowCount()):
                    desc_widget = self.items_table.cellWidget(row, 0)
                    qty_widget = self.items_table.cellWidget(row, 1)
                    price_widget = self.items_table.cellWidget(row, 2)
                    
                    description = desc_widget.text().strip()
                    if not description:
                        continue
                        
                    quantity = qty_widget.value()
                    unit_price_cents = int(price_widget.value() * 100)
                    total_cents = quantity * unit_price_cents
                    
                    item = QuoteItem(
                        quote_id=quote.id,
                        description=description,
                        quantity=quantity,
                        unit_price=unit_price_cents,
                        total=total_cents
                    )
                    db.add(item)
                    
            else:
                # Update existing quote
                self.quote.customer_name = customer_name
                self.quote.quote_date = self.quote_date_input.date().toPython()
                self.quote.expiry_date = self.expiry_date_input.date().toPython()
                self.quote.status = self.status_input.currentText()
                self.quote.notes = self.notes_input.toPlainText().strip() or None
                self.quote.subtotal = subtotal_cents
                self.quote.tax = tax_cents
                self.quote.total = total_cents
                
                # Delete old items
                db.query(QuoteItem).filter(QuoteItem.quote_id == self.quote.id).delete()
                
                # Save new items
                for row in range(self.items_table.rowCount()):
                    desc_widget = self.items_table.cellWidget(row, 0)
                    qty_widget = self.items_table.cellWidget(row, 1)
                    price_widget = self.items_table.cellWidget(row, 2)
                    
                    description = desc_widget.text().strip()
                    if not description:
                        continue
                        
                    quantity = qty_widget.value()
                    unit_price_cents = int(price_widget.value() * 100)
                    total_cents = quantity * unit_price_cents
                    
                    item = QuoteItem(
                        quote_id=self.quote.id,
                        description=description,
                        quantity=quantity,
                        unit_price=unit_price_cents,
                        total=total_cents
                    )
                    db.add(item)
                    
            db.commit()
            play_sound("celebration")
            self.accept()
            
        except Exception as e:
            play_sound("caution")
            QMessageBox.critical(self, "Error", f"Failed to save quote:\n{str(e)}")
