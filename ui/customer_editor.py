from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QLineEdit, QTextEdit, QComboBox, QPushButton, QLabel, QMessageBox)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from ui.assets import play_sound, get_icon
from database import get_db
from models import Customer

class CustomerEditorDialog(QDialog):
    def __init__(self, parent=None, customer=None):
        super().__init__(parent)
        self.customer = customer
        self.is_new = customer is None
        
        self.setWindowTitle("New Customer" if self.is_new else "Edit Customer")
        self.setMinimumWidth(500)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Form
        form_layout = QFormLayout()
        
        self.contact_input = QLineEdit()
        self.contact_input.setPlaceholderText("Required")
        form_layout.addRow("Contact Name:", self.contact_input)
        
        self.company_input = QLineEdit()
        self.company_input.setPlaceholderText("Optional")
        form_layout.addRow("Company Name:", self.company_input)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("email@example.com")
        self.email_input.textChanged.connect(self.update_send_email_button)
        form_layout.addRow("Email:", self.email_input)
        
        self.phone_input = QLineEdit()
        form_layout.addRow("Phone:", self.phone_input)
        
        self.mobile_input = QLineEdit()
        form_layout.addRow("Mobile:", self.mobile_input)
        
        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(80)
        self.address_input.setPlaceholderText("Street Address, City, State, Postcode")
        form_layout.addRow("Address:", self.address_input)
        
        self.status_input = QComboBox()
        self.status_input.addItems(["Active", "On Hold", "Archived", "Banned"])
        form_layout.addRow("Status:", self.status_input)
        
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(100)
        self.notes_input.setPlaceholderText("Customer preferences, special requirements, etc.")
        form_layout.addRow("Notes:", self.notes_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("Save Customer")
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
        self.save_btn.clicked.connect(self.save_customer)
        
        # Send Email Button
        self.send_email_btn = QPushButton("Send Email")
        self.send_email_btn.setIcon(get_icon("fa5s.envelope", color="white"))
        self.send_email_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.send_email_btn.clicked.connect(self.send_email)
        self.send_email_btn.setEnabled(False)  # Will be enabled when email is entered
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.send_email_btn)
        btn_layout.addWidget(self.save_btn)
        
        layout.addLayout(btn_layout)
        
        # Load existing data if editing
        if not self.is_new:
            self.load_customer_data()
            
    def load_customer_data(self):
        self.company_input.setText(self.customer.company_name)
        self.contact_input.setText(self.customer.contact_name or "")
        self.email_input.setText(self.customer.email or "")
        self.phone_input.setText(self.customer.phone or "")
        self.mobile_input.setText(self.customer.mobile or "")
        self.address_input.setPlainText(self.customer.address or "")
        self.status_input.setCurrentText(self.customer.status)
        self.notes_input.setPlainText(self.customer.notes or "")
    
    def send_email(self):
        """Open default email client with customer email"""
        email = self.email_input.text().strip()
        if email:
            url = QUrl(f"mailto:{email}")
            QDesktopServices.openUrl(url)
        else:
            QMessageBox.information(self, "No Email", "Please enter an email address first.")
    
    def update_send_email_button(self):
        """Enable/disable send email button based on email field"""
        email = self.email_input.text().strip()
        self.send_email_btn.setEnabled(bool(email))
        
    def save_customer(self):
        # Validate
        contact_name = self.contact_input.text().strip()
        if not contact_name:
            play_sound("caution")
            QMessageBox.warning(self, "Validation Error", "Contact Name is required.")
            return

        company_name = self.company_input.text().strip()
        if not company_name:
            # If company name is empty, use contact name (since DB requires company_name)
            company_name = contact_name
            
        try:
            db = next(get_db())
            
            if self.is_new:
                # Generate Customer Number
                last_customer = db.query(Customer).filter(Customer.customer_number.like("CN%")).order_by(Customer.id.desc()).first()
                
                if last_customer and last_customer.customer_number:
                    try:
                        last_num = int(last_customer.customer_number[2:])
                        new_num = last_num + 1
                    except ValueError:
                        new_num = 1
                else:
                    new_num = 1
                
                customer_number = f"CN{new_num:06d}"

                customer = Customer(
                    customer_number=customer_number,
                    company_name=company_name,
                    contact_name=self.contact_input.text().strip() or None,
                    email=self.email_input.text().strip() or None,
                    phone=self.phone_input.text().strip() or None,
                    mobile=self.mobile_input.text().strip() or None,
                    address=self.address_input.toPlainText().strip() or None,
                    status=self.status_input.currentText(),
                    notes=self.notes_input.toPlainText().strip() or None
                )
                db.add(customer)
            else:
                self.customer.company_name = company_name
                self.customer.contact_name = self.contact_input.text().strip() or None
                self.customer.email = self.email_input.text().strip() or None
                self.customer.phone = self.phone_input.text().strip() or None
                self.customer.mobile = self.mobile_input.text().strip() or None
                self.customer.address = self.address_input.toPlainText().strip() or None
                self.customer.status = self.status_input.currentText()
                self.customer.notes = self.notes_input.toPlainText().strip() or None
                
            db.commit()
            play_sound("celebration")
            self.accept()
            
        except Exception as e:
            play_sound("caution")
            QMessageBox.critical(self, "Error", f"Failed to save customer:\n{str(e)}")
