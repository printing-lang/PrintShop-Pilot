from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
                               QDateEdit, QComboBox, QDialogButtonBox, QTextEdit, QMessageBox, 
                               QLabel, QPushButton, QGroupBox, QFrame, QTableWidget, QTableWidgetItem,
                               QHeaderView, QAbstractItemView)
from PySide6.QtCore import Qt, QDate, QUrl
from PySide6.QtGui import QDesktopServices
from models import Job, Priority, JobStatus
from database import get_db
from settings_manager import get_settings
from ui.customer_editor import CustomerEditorDialog
from ui.customer_search_dialog import CustomerSearchDialog
from ui.assets import get_icon
import datetime

class JobEditorDialog(QDialog):
    def __init__(self, parent=None, job=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Job" if not job else "Edit Job")
        self.resize(900, 700)
        self.job = job
        
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Create New Job" if not job else "Edit Job")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        
        # Customer Buttons
        self.add_customer_btn = QPushButton("Add Customer")
        self.add_customer_btn.setIcon(get_icon("person_add"))
        self.add_customer_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.add_customer_btn.clicked.connect(self.add_customer)
        
        self.find_customer_btn = QPushButton("Find Customer")
        self.find_customer_btn.setIcon(get_icon("person_search"))
        self.find_customer_btn.setStyleSheet("""
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
        self.find_customer_btn.clicked.connect(self.find_customer)
        
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
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.send_email_btn)
        header_layout.addWidget(self.add_customer_btn)
        header_layout.addWidget(self.find_customer_btn)
        
        layout.addLayout(header_layout)
        layout.addSpacing(20)
        
        # Main Form Layout (2 Columns)
        main_form_layout = QHBoxLayout()
        
        # Left Column
        left_layout = QVBoxLayout()
        
        self.customer_name = QLineEdit()
        self.customer_name.setPlaceholderText("Customer Name")
        left_layout.addWidget(QLabel("Customer Name"))
        left_layout.addWidget(self.customer_name)
        
        self.contact_email = QLineEdit()
        self.contact_email.setPlaceholderText("email@example.com")
        self.contact_email.textChanged.connect(self.update_send_email_button)
        left_layout.addWidget(QLabel("Email"))
        left_layout.addWidget(self.contact_email)
        
        # Address (Full width in left column logic, but visually spanning)
        # The user wanted Address below email.
        self.address = QLineEdit() # Using LineEdit for single line address as per image, or TextEdit? Image shows single line-ish box but wide.
        # Let's use LineEdit for address to match the "graphical" look which seems to be compact.
        left_layout.addWidget(QLabel("Address"))
        left_layout.addWidget(self.address)
        
        # Order Date
        self.order_date = QDateEdit(QDate.currentDate())
        self.order_date.setCalendarPopup(True)
        self.order_date.setDisplayFormat("dd/MM/yyyy")
        left_layout.addWidget(QLabel("Order Date"))
        left_layout.addWidget(self.order_date)
        
        # Priority
        self.priority = QComboBox()
        self.priority.addItems([p.value for p in Priority])
        left_layout.addWidget(QLabel("Priority"))
        left_layout.addWidget(self.priority)
        
        # Status
        self.status = QComboBox()
        self.status.addItems([s.value for s in JobStatus])
        left_layout.addWidget(QLabel("Status"))
        left_layout.addWidget(self.status)
        
        # Created By
        self.created_by = QComboBox()
        # Populate from settings
        settings = get_settings()
        self.created_by.addItems(settings.get_personnel())
        left_layout.addWidget(QLabel("Created By"))
        left_layout.addWidget(self.created_by)
        
        main_form_layout.addLayout(left_layout)
        main_form_layout.addSpacing(20)
        
        # Right Column
        right_layout = QVBoxLayout()
        
        # Order Type
        self.order_type = QComboBox()
        self.order_type.addItems(["Custom T Shirts", "DTF Printing", "DTG Printing", "Screen Printing", "Embroidery", "Dye Sublimation", "Speciality Print", "HTV", "Blank"])
        right_layout.addWidget(QLabel("Order Type"))
        right_layout.addWidget(self.order_type)
        
        # Phone
        self.contact_phone = QLineEdit()
        self.contact_phone.setPlaceholderText("0433 333 333")
        right_layout.addWidget(QLabel("Phone"))
        right_layout.addWidget(self.contact_phone)
        
        # Spacer to align with Address? 
        # The image shows Address spanning full width? No, it's under Email.
        # Wait, looking at the image:
        # Left Col: Customer Name, Email.
        # Right Col: Order Type, Phone.
        # Full Width: Address.
        # Then 2 Cols again:
        # Left: Order Date, Priority, Status, Created By.
        # Right: Due Date, Order Source, Shop, Assigned To.
        
        # Let's restructure to match the image exactly.
        
        # Top Row: Left (Name, Email), Right (Type, Phone)
        # Middle: Address (Full Width)
        # Bottom: Left (Dates, etc), Right (Dates, etc)
        
        # RE-DO LAYOUT
        
        # Row 1
        row1 = QHBoxLayout()
        col1 = QVBoxLayout()
        col1.addWidget(QLabel("Customer Name"))
        col1.addWidget(self.customer_name)
        col1.addWidget(QLabel("Email"))
        col1.addWidget(self.contact_email)
        
        col2 = QVBoxLayout()
        col2.addWidget(QLabel("Order Type"))
        col2.addWidget(self.order_type)
        col2.addWidget(QLabel("Phone"))
        col2.addWidget(self.contact_phone)
        
        row1.addLayout(col1)
        row1.addSpacing(20)
        row1.addLayout(col2)
        
        layout.addLayout(row1)
        
        # Address
        layout.addWidget(QLabel("Address"))
        layout.addWidget(self.address)
        
        # Row 2 (The grid of 4x2)
        row2 = QHBoxLayout()
        
        r2_col1 = QVBoxLayout()
        # Order Date
        r2_col1.addWidget(QLabel("Order Date"))
        r2_col1.addWidget(self.order_date)
        # Priority
        r2_col1.addWidget(QLabel("Priority"))
        r2_col1.addWidget(self.priority)
        # Status
        r2_col1.addWidget(QLabel("Status"))
        r2_col1.addWidget(self.status)
        # Created By
        r2_col1.addWidget(QLabel("Created By"))
        r2_col1.addWidget(self.created_by)
        
        # PO Buttons
        po_buttons_layout = QHBoxLayout()
        po_buttons_layout.setSpacing(10)
        
        # Add New PO Button
        self.add_po_btn = QPushButton("Add New PO")
        self.add_po_btn.setIcon(get_icon("fa5s.shopping-cart"))
        self.add_po_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.add_po_btn.clicked.connect(self.add_purchase_order)
        po_buttons_layout.addWidget(self.add_po_btn)
        
        # Edit PO Button
        self.edit_po_btn = QPushButton("Edit PO")
        self.edit_po_btn.setIcon(get_icon("fa5s.edit"))
        self.edit_po_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.edit_po_btn.clicked.connect(self.edit_purchase_order)
        po_buttons_layout.addWidget(self.edit_po_btn)
        
        r2_col1.addLayout(po_buttons_layout)
        
        r2_col2 = QVBoxLayout()
        # Due Date
        self.due_date = QDateEdit(QDate.currentDate().addDays(7))
        self.due_date.setCalendarPopup(True)
        self.due_date.setDisplayFormat("dd/MM/yyyy")
        r2_col2.addWidget(QLabel("Due Date"))
        r2_col2.addWidget(self.due_date)
        
        # Order Source
        self.order_source = QComboBox()
        self.order_source.addItems(["In Store", "Web", "Email", "Phone"])
        r2_col2.addWidget(QLabel("Order Source"))
        r2_col2.addWidget(self.order_source)
        
        # Shop
        self.shop = QComboBox()
        self.shop.addItems(settings.get_shops())
        r2_col2.addWidget(QLabel("Shop"))
        r2_col2.addWidget(self.shop)
        
        # Assigned To
        self.assigned_to = QComboBox()
        self.assigned_to.addItems(settings.get_personnel())
        r2_col2.addWidget(QLabel("Assigned To"))
        r2_col2.addWidget(self.assigned_to)
        
        # Shipping
        self.shipping = QComboBox()
        self.shipping.addItems(settings.get_shipping_options())
        r2_col2.addWidget(QLabel("Shipping"))
        r2_col2.addWidget(self.shipping)
        
        row2.addLayout(r2_col1)
        row2.addSpacing(20)
        row2.addLayout(r2_col2)
        
        layout.addLayout(row2)
        
        
        # Overview (read-only when editing)
        layout.addWidget(QLabel("Overview"))
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(80)
        layout.addWidget(self.notes)
        
        # Production Notes
        layout.addWidget(QLabel("Production Notes"))
        self.production_notes = QTextEdit()
        self.production_notes.setMaximumHeight(100)

        layout.addWidget(self.production_notes)
        
        # Linked Purchase Orders
        layout.addWidget(QLabel("Linked Purchase Orders"))
        self.po_table = QTableWidget()
        self.po_table.setColumnCount(4)
        self.po_table.setHorizontalHeaderLabels(["PO #", "Supplier", "Status", "Total"])
        self.po_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.po_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.po_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.po_table.setMaximumHeight(120)
        self.po_table.doubleClicked.connect(self.open_po)
        layout.addWidget(self.po_table)
        
        # Buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.save_job)
        self.buttons.rejected.connect(self.reject)
        
        # Style the Save button
        save_btn = self.buttons.button(QDialogButtonBox.Save)
        save_btn.setText("Create Job" if not job else "Save Job")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0d6efd;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
        """)
        
        layout.addWidget(self.buttons)
        
        if job:
            self.load_job_data()

    def load_job_data(self):
        self.customer_name.setText(self.job.customer_name)
        self.order_type.setCurrentText(self.job.order_type)
        self.order_date.setDate(self.job.order_date)
        self.due_date.setDate(self.job.due_date)
        self.priority.setCurrentText(self.job.priority)
        self.status.setCurrentText(self.job.status)
        self.contact_phone.setText(self.job.contact_phone or "")
        self.contact_email.setText(self.job.contact_email or "")
        self.notes.setPlainText(self.job.notes or "")
        self.notes.setReadOnly(True)  # Make notes read-only when editing
        self.production_notes.setPlainText(self.job.production_notes or "")
        self.order_source.setCurrentText(self.job.order_source or "In Store")
        self.created_by.setCurrentText(self.job.created_by or "")
        self.assigned_to.setCurrentText(self.job.assigned_to or "")
        self.shipping.setCurrentText(self.job.shipping or "")
        # Address is not on Job model currently, but we can load it if we had it. 
        # For now, we just leave it empty or maybe we should add it to Job model?
        # The user said "Customer Name, Email, Phone and Address in form should auto populate from the CRM customer file"
        # It doesn't explicitly say it needs to be saved to the Job, but it's implied if it's editable.
        # However, looking at models.py, Job doesn't have address. 
        # I will not add it to the model for now to avoid migration issues, unless requested. 
        # It might just be for display/reference from the customer.
        
        # Load POs
        db = next(get_db())
        try:
            # Re-query job to ensure relationships
            current_job = db.query(Job).get(self.job.id)
            if current_job:
                pos = current_job.purchase_orders
                self.po_table.setRowCount(len(pos))
                for i, po in enumerate(pos):
                    self.po_table.setItem(i, 0, QTableWidgetItem(po.po_number))
                    self.po_table.setItem(i, 1, QTableWidgetItem(po.supplier_name))
                    self.po_table.setItem(i, 2, QTableWidgetItem(po.status))
                    self.po_table.setItem(i, 3, QTableWidgetItem(f"${po.total/100:.2f}"))
                    # Store PO ID
                    self.po_table.item(i, 0).setData(Qt.UserRole, po.id)
        finally:
            db.close()

    def open_po(self, index):
        po_id = self.po_table.item(index.row(), 0).data(Qt.UserRole)
        # Open PO Editor
        from ui.po_editor import POEditorDialog
        from models import PurchaseOrder
        
        db = next(get_db())
        try:
            po = db.query(PurchaseOrder).get(po_id)
            if po:
                dialog = POEditorDialog(self, po)
                dialog.exec()
                # Refresh
                self.load_job_data()
        finally:
            db.close()

    def add_customer(self):
        dialog = CustomerEditorDialog(self)
        if dialog.exec():
            # Get the new customer (it's the last one added, or we could modify CustomerEditor to return it)
            # For now, let's just find the latest customer
            db = next(get_db())
            customer = db.query(Job).order_by(Job.id.desc()).first() # Wait, this is Job.
            # We need Customer.
            # Actually, let's just use the search dialog logic or ask the user to find it.
            # Better: Modify CustomerEditorDialog to return the created customer? 
            # Or just query the latest customer.
            from models import Customer
            customer = db.query(Customer).order_by(Customer.id.desc()).first()
            if customer:
                self.populate_customer(customer)
            db.close()

    def find_customer(self):
        dialog = CustomerSearchDialog(self)
        if dialog.exec():
            if dialog.selected_customer:
                self.populate_customer(dialog.selected_customer)

    def populate_customer(self, customer):
        self.customer_name.setText(customer.contact_name or customer.company_name)
        self.contact_email.setText(customer.email or "")
        self.contact_phone.setText(customer.phone or "")
        self.address.setText(customer.address or "")
    
    def send_email(self):
        """Open default email client with contact email"""
        email = self.contact_email.text().strip()
        if email:
            url = QUrl(f"mailto:{email}")
            QDesktopServices.openUrl(url)
        else:
            QMessageBox.information(self, "No Email", "Please enter an email address first.")
    
    def update_send_email_button(self):
        """Enable/disable send email button based on email field"""
        email = self.contact_email.text().strip()
        self.send_email_btn.setEnabled(bool(email))
    
    def add_purchase_order(self):
        """Create a new Purchase Order linked to this job"""
        if not self.job:
            QMessageBox.warning(self, "Cannot Create PO", "Please save the job first before creating a Purchase Order.")
            return
        
        from ui.po_editor import POEditorDialog
        dialog = POEditorDialog(self, job=self.job)
        if dialog.exec():
            # Refresh PO table
            self.load_job_data()
    
    def edit_purchase_order(self):
        """Edit an existing Purchase Order from the table"""
        selected_rows = self.po_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "No PO Selected", "Please select a Purchase Order from the table to edit.")
            return
        
        # Get the first selected row
        index = selected_rows[0]
        self.open_po(index)


    def save_job(self):
        if not self.customer_name.text():
            QMessageBox.warning(self, "Validation Error", "Customer Name is required.")
            return

        db = next(get_db())
        try:
            data = {
                "customer_name": self.customer_name.text(),
                "order_type": self.order_type.currentText(),
                "order_date": self.order_date.date().toPython(),
                "due_date": self.due_date.date().toPython(),
                "priority": self.priority.currentText(),
                "status": self.status.currentText(),
                "contact_phone": self.contact_phone.text() or None,
                "contact_email": self.contact_email.text() or None,
                "notes": self.notes.toPlainText() or None,
                "production_notes": self.production_notes.toPlainText() or None,
                "order_source": self.order_source.currentText(),
                "created_by": self.created_by.currentText() or None,
                "assigned_to": self.assigned_to.currentText() or None,
                "shipping": self.shipping.currentText() or None
            }
            
            if self.job:
                # Update existing
                for key, value in data.items():
                    setattr(self.job, key, value)
                
                # Auto-archive if status is Complete
                if data["status"] == "Complete":
                    self.job.is_archived = True
                
                db.commit()
            else:
                # Create new
                # Generate Job Number
                # Find the latest job number starting with "JN"
                last_job = db.query(Job).filter(Job.job_number.like("JN%")).order_by(Job.id.desc()).first()
                
                if last_job and last_job.job_number:
                    try:
                        # Extract number part
                        last_num = int(last_job.job_number[2:])
                        new_num = last_num + 1
                    except ValueError:
                        # Fallback if parsing fails
                        new_num = 1
                else:
                    new_num = 1
                
                data["job_number"] = f"JN{new_num:06d}"
                
                new_job = Job(**data)
                db.add(new_job)
                db.commit()
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        finally:
            db.close()
