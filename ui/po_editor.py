
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDateEdit, 
                               QComboBox, QTextEdit, QLabel, QTableWidget, QHeaderView, 
                               QAbstractItemView, QPushButton, QHBoxLayout, QWidget, 
                               QSpinBox, QCheckBox, QDoubleSpinBox, QTableWidgetItem, QMessageBox)
from PySide6.QtCore import Qt, QDate, QUrl
from PySide6.QtGui import QDesktopServices
from models import PurchaseOrder, POStatus, POItem, Job
from database import get_db
from ui.assets import get_icon, play_sound

class POEditorDialog(QDialog):
    def __init__(self, parent=None, po=None, job=None):
        super().__init__(parent)
        self.po = po
        self.job = job  # The job this PO is being created for (if any)
        self.is_new = po is None
        
        self.setWindowTitle("New Purchase Order" if self.is_new else f"Edit PO - {po.po_number}")
        self.setMinimumSize(800, 600)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Header Form
        form_layout = QFormLayout()
        
        self.supplier_input = QLineEdit()
        self.supplier_input.setPlaceholderText("Required")
        form_layout.addRow("Supplier Name:", self.supplier_input)
        
        self.order_date_input = QDateEdit()
        self.order_date_input.setCalendarPopup(True)
        self.order_date_input.setDate(QDate.currentDate())
        form_layout.addRow("Order Date:", self.order_date_input)
        
        self.expected_date_input = QDateEdit()
        self.expected_date_input.setCalendarPopup(True)
        self.expected_date_input.setDate(QDate.currentDate().addDays(7))
        form_layout.addRow("Due Date:", self.expected_date_input)
        
        self.received_date_input = QDateEdit()
        self.received_date_input.setCalendarPopup(True)
        self.received_date_input.setDate(QDate.currentDate())
        self.received_date_input.setEnabled(False)  # Enable when status is Received
        form_layout.addRow("Received Date:", self.received_date_input)
        
        self.status_input = QComboBox()
        self.status_input.addItems([status.value for status in POStatus])
        self.status_input.currentTextChanged.connect(self.on_status_changed)
        form_layout.addRow("Status:", self.status_input)
        
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(60)
        self.notes_input.setPlaceholderText("PO notes or special requirements...")
        self.notes_input.setPlaceholderText("PO notes or special requirements...")
        form_layout.addRow("Notes:", self.notes_input)
        
        # Linked Jobs - Removed
        # self.jobs_list = QListWidget()
        # ...
        
        layout.addLayout(form_layout)
        
        # Line Items Section
        items_label = QLabel("Items to Order")
        items_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(items_label)
        
        # Line Items Table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(7)
        self.items_table.setHorizontalHeaderLabels(["Description", "Qty", "Stock", "Job", "Unit Price", "Total", ""])
        self.items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.items_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.items_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.items_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.items_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.items_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.items_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.items_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.items_table.setMinimumHeight(200)
        layout.addWidget(self.items_table)
        
        # Add Line Item Button
        add_item_btn = QPushButton("Add Item")
        add_item_btn.setIcon(get_icon("fa5s.plus", color="#27ae60"))
        add_item_btn.clicked.connect(self.add_line_item)
        layout.addWidget(add_item_btn)
        
        # Total Section
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        
        total_label_text = QLabel("Total:")
        total_label_text.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.total_label = QLabel("$0.00")
        self.total_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        
        total_layout.addWidget(total_label_text)
        total_layout.addWidget(self.total_label)
        layout.addLayout(total_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
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
        self.send_email_btn.setEnabled(False)  # Will be enabled when supplier has email
        
        self.save_btn = QPushButton("Save PO")
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
        self.save_btn.clicked.connect(self.save_po)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.send_email_btn)
        btn_layout.addWidget(self.save_btn)
        
        layout.addLayout(btn_layout)
        
        # Load jobs for dropdowns
        self.load_jobs()
        
        # Load existing data if editing
        if not self.is_new:
            self.load_po_data()
        else:
            # Add one empty line item
            self.add_line_item()
            
    def load_jobs(self):
        # Helper to get jobs for the comboboxes
        db = next(get_db())
        try:
            self.active_jobs = db.query(Job).filter(Job.is_archived == False).order_by(Job.job_number.desc()).all()
        finally:
            db.close()

    def on_status_changed(self, status):
        # Enable received date only when status is Received
        self.received_date_input.setEnabled(status == POStatus.RECEIVED.value)
        
    def add_line_item(self):
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)
        
        # Description
        desc = QLineEdit()
        desc.textChanged.connect(self.calculate_total)
        self.items_table.setCellWidget(row, 0, desc)
        
        # Quantity
        qty = QSpinBox()
        qty.setMinimum(1)
        qty.setMaximum(9999)
        qty.setValue(1)
        qty.valueChanged.connect(lambda: self.update_line_total(row))
        self.items_table.setCellWidget(row, 1, qty)
        
        # Stock Checkbox
        stock_cb = QCheckBox()
        stock_cb.stateChanged.connect(lambda state, r=row: self.on_stock_changed(state, r))
        # Center the checkbox
        cb_widget = QWidget()
        cb_layout = QHBoxLayout(cb_widget)
        cb_layout.addWidget(stock_cb)
        cb_layout.setAlignment(Qt.AlignCenter)
        cb_layout.setContentsMargins(0, 0, 0, 0)
        self.items_table.setCellWidget(row, 2, cb_widget)
        
        # Job Selector
        job_combo = QComboBox()
        job_combo.addItem("Select Job...", None)
        if not hasattr(self, 'active_jobs'):
            self.load_jobs()
            
        for job in self.active_jobs:
            job_combo.addItem(f"{job.job_number} - {job.customer_name}", job.id)
            
        self.items_table.setCellWidget(row, 3, job_combo)

        # Unit Price
        price = QDoubleSpinBox()
        price.setPrefix("$")
        price.setMinimum(0)
        price.setMaximum(999999)
        price.setDecimals(2)
        price.valueChanged.connect(lambda: self.update_line_total(row))
        self.items_table.setCellWidget(row, 4, price)
        
        # Total (read-only)
        total = QTableWidgetItem("$0.00")
        total.setFlags(total.flags() & ~Qt.ItemIsEditable)
        self.items_table.setItem(row, 5, total)
        
        # Delete Button
        delete_btn = QPushButton("Delete")
        delete_btn.setIcon(get_icon("fa5s.trash", color="#e74c3c"))
        delete_btn.clicked.connect(lambda: self.delete_line_item(row))
        self.items_table.setCellWidget(row, 6, delete_btn)
        
    def on_stock_changed(self, state, row):
        job_combo = self.items_table.cellWidget(row, 3)
        if job_combo:
            job_combo.setEnabled(state != Qt.Checked)
            if state == Qt.Checked:
                job_combo.setCurrentIndex(0) # Reset selection
        
    def delete_line_item(self, row):
        self.items_table.removeRow(row)
        self.calculate_total()
        
    def update_line_total(self, row):
        qty_widget = self.items_table.cellWidget(row, 1)
        price_widget = self.items_table.cellWidget(row, 4)
        
        if qty_widget and price_widget:
            qty = qty_widget.value()
            price = price_widget.value()
            total = qty * price
            
            total_item = self.items_table.item(row, 5)
            if total_item:
                total_item.setText(f"${total:.2f}")
                
        self.calculate_total()
        
    def calculate_total(self):
        total = 0
        
        for row in range(self.items_table.rowCount()):
            total_item = self.items_table.item(row, 5)
            if total_item:
                total_text = total_item.text().replace("$", "")
                try:
                    total += float(total_text)
                except:
                    pass
        
        self.total_label.setText(f"${total:.2f}")
        
    def load_po_data(self):
        self.supplier_input.setText(self.po.supplier_name)
        if self.po.order_date:
            self.order_date_input.setDate(QDate(self.po.order_date))
        if self.po.expected_date:
            self.expected_date_input.setDate(QDate(self.po.expected_date))
        if self.po.received_date:
            self.received_date_input.setDate(QDate(self.po.received_date))
        self.status_input.setCurrentText(self.po.status)
        self.notes_input.setPlainText(self.po.notes or "")
        
        # Load line items
        db = next(get_db())
        items = db.query(POItem).filter(POItem.po_id == self.po.id).all()
        
        for item in items:
            row = self.items_table.rowCount()
            self.items_table.insertRow(row)
            
            desc = QLineEdit(item.description)
            desc.textChanged.connect(self.calculate_total)
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
            
        self.calculate_total()
        
    def save_po(self):
        # Validate
        supplier_name = self.supplier_input.text().strip()
        if not supplier_name:
            play_sound("caution")
            QMessageBox.warning(self, "Validation Error", "Supplier Name is required.")
            return
            
        if self.items_table.rowCount() == 0:
            play_sound("caution")
            QMessageBox.warning(self, "Validation Error", "At least one item is required.")
            return
            
        try:
            db = next(get_db())
            
            # Convert total to cents
            total_cents = int(float(self.total_label.text().replace("$", "")) * 100)
            
            if self.is_new:
                # Generate PO number
                latest = db.query(PurchaseOrder).order_by(PurchaseOrder.id.desc()).first()
                next_num = (latest.id + 1) if latest else 1
                po_number = f"PO{next_num:05d}"
                
                po = PurchaseOrder(
                    po_number=po_number,
                    supplier_name=supplier_name,
                    order_date=self.order_date_input.date().toPython(),
                    expected_date=self.expected_date_input.date().toPython(),
                    received_date=self.received_date_input.date().toPython() if self.status_input.currentText() == POStatus.STOCK_ARRIVED.value else None,
                    status=self.status_input.currentText(),
                    notes=self.notes_input.toPlainText().strip() or None,
                    total=total_cents,
                    is_archived=(self.status_input.currentText() == POStatus.COMPLETE.value)
                )
                
                # Handle Linked Jobs
                selected_job_ids = []
                for i in range(self.jobs_list.count()):
                    item = self.jobs_list.item(i)
                    if item.isSelected():
                        selected_job_ids.append(item.data(Qt.UserRole))
                
                if selected_job_ids:
                    selected_jobs = db.query(Job).filter(Job.id.in_(selected_job_ids)).all()
                    po.jobs = selected_jobs
                    po.job_id = selected_job_ids[0] # Legacy support
                
                db.add(po)
                db.flush()
                
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
                    
                    item = POItem(
                        po_id=po.id,
                        description=description,
                        quantity=quantity,
                        unit_price=unit_price_cents,
                        total=total_cents
                    )
                    db.add(item)
                    
            else:
                # Update existing PO
                self.po.supplier_name = supplier_name
                self.po.order_date = self.order_date_input.date().toPython()
                self.po.expected_date = self.expected_date_input.date().toPython()
                self.po.received_date = self.received_date_input.date().toPython() if self.status_input.currentText() == POStatus.STOCK_ARRIVED.value else None
                self.po.status = self.status_input.currentText()
                self.po.notes = self.notes_input.toPlainText().strip() or None
                self.po.total = total_cents
                
                # Auto-archive if status is Complete
                if self.status_input.currentText() == POStatus.COMPLETE.value:
                    self.po.is_archived = True
                
                # Delete old items
                db.query(POItem).filter(POItem.po_id == self.po.id).delete()
                
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
                    
                    item = POItem(
                        po_id=self.po.id,
                        description=description,
                        quantity=quantity,
                        unit_price=unit_price_cents,
                        total=total_cents
                    )
                    db.add(item)
                    
            db.commit()
            print(f"PO saved successfully. Status: {self.status_input.currentText()}, Archived: {self.po.is_archived if not self.is_new else False}")
            play_sound("celebration")
            self.accept()
            
        except Exception as e:
            print(f"Error saving PO: {e}")
            import traceback
            traceback.print_exc()
            play_sound("caution")
            QMessageBox.critical(self, "Error", f"Failed to save PO:\n{str(e)}")
            db.rollback()
        
    def delete_line_item(self, row):
        self.items_table.removeRow(row)
        self.calculate_total()
        
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
                
        self.calculate_total()
        
    def calculate_total(self):
        total = 0
        
        for row in range(self.items_table.rowCount()):
            total_item = self.items_table.item(row, 3)
            if total_item:
                total_text = total_item.text().replace("$", "")
                try:
                    total += float(total_text)
                except:
                    pass
        
        self.total_label.setText(f"${total:.2f}")
        
    def load_po_data(self):
        self.supplier_input.setText(self.po.supplier_name)
        if self.po.order_date:
            self.order_date_input.setDate(QDate(self.po.order_date))
        if self.po.due_date:
            self.expected_date_input.setDate(QDate(self.po.due_date))
        if self.po.received_date:
            self.received_date_input.setDate(QDate(self.po.received_date))
        self.status_input.setCurrentText(self.po.status)
        self.notes_input.setPlainText(self.po.notes or "")
        
        # Load line items
        db = next(get_db())
        items = db.query(POItem).filter(POItem.po_id == self.po.id).all()
        
        # Ensure active jobs are loaded
        if not hasattr(self, 'active_jobs'):
            self.load_jobs()

        for item in items:
            row = self.items_table.rowCount()
            self.items_table.insertRow(row)
            
            desc = QLineEdit(item.description)
            desc.textChanged.connect(self.calculate_total)
            self.items_table.setCellWidget(row, 0, desc)
            
            qty = QSpinBox()
            qty.setValue(item.quantity)
            qty.valueChanged.connect(lambda: self.update_line_total(row))
            self.items_table.setCellWidget(row, 1, qty)
            
            # Stock Checkbox
            stock_cb = QCheckBox()
            stock_cb.setChecked(item.is_stock)
            stock_cb.stateChanged.connect(lambda state, r=row: self.on_stock_changed(state, r))
            cb_widget = QWidget()
            cb_layout = QHBoxLayout(cb_widget)
            cb_layout.addWidget(stock_cb)
            cb_layout.setAlignment(Qt.AlignCenter)
            cb_layout.setContentsMargins(0, 0, 0, 0)
            self.items_table.setCellWidget(row, 2, cb_widget)

            # Job Selector
            job_combo = QComboBox()
            job_combo.addItem("Select Job...", None)
            for job in self.active_jobs:
                job_combo.addItem(f"{job.job_number} - {job.customer_name}", job.id)
            
            if item.job_id:
                index = job_combo.findData(item.job_id)
                if index >= 0:
                    job_combo.setCurrentIndex(index)
            
            job_combo.setEnabled(not item.is_stock)
            self.items_table.setCellWidget(row, 3, job_combo)

            price = QDoubleSpinBox()
            price.setPrefix("$")
            price.setValue(item.unit_price / 100)
            price.setDecimals(2)
            price.valueChanged.connect(lambda: self.update_line_total(row))
            self.items_table.setCellWidget(row, 4, price)
            
            total = QTableWidgetItem(f"${item.total / 100:.2f}")
            total.setFlags(total.flags() & ~Qt.ItemIsEditable)
            self.items_table.setItem(row, 5, total)
            
            delete_btn = QPushButton("Delete")
            delete_btn.setIcon(get_icon("fa5s.trash", color="#e74c3c"))
            delete_btn.clicked.connect(lambda checked, r=row: self.delete_line_item(r))
            self.items_table.setCellWidget(row, 6, delete_btn)
            
        self.calculate_total()
        
    def send_email(self):
        """Open default email client with supplier email"""
        # Try to get email from supplier record
        supplier_email = None
        db = next(get_db())
        try:
            from models import Supplier
            supplier = db.query(Supplier).filter(Supplier.supplier_name == self.supplier_input.text().strip()).first()
            if supplier and supplier.email:
                supplier_email = supplier.email
        finally:
            db.close()
        
        if supplier_email:
            url = QUrl(f"mailto:{supplier_email}")
            QDesktopServices.openUrl(url)
        else:
            QMessageBox.information(self, "No Email", "No email found for this supplier.")
            
        
    def save_po(self):
        # Validate
        supplier_name = self.supplier_input.text().strip()
        if not supplier_name:
            play_sound("caution")
            QMessageBox.warning(self, "Validation Error", "Supplier Name is required.")
            return
            
        if self.items_table.rowCount() == 0:
            play_sound("caution")
            QMessageBox.warning(self, "Validation Error", "At least one item is required.")
            return
            
        try:
            db = next(get_db())
            
            # Convert total to cents
            total_cents = int(float(self.total_label.text().replace("$", "")) * 100)
            
            if self.is_new:
                # Generate PO number
                latest = db.query(PurchaseOrder).order_by(PurchaseOrder.id.desc()).first()
                next_num = (latest.id + 1) if latest else 1
                po_number = f"PO{next_num:05d}"
                
                po = PurchaseOrder(
                    po_number=po_number,
                    supplier_name=supplier_name,
                    order_date=self.order_date_input.date().toPython(),
                    due_date=self.expected_date_input.date().toPython(),
                    received_date=self.received_date_input.date().toPython() if self.status_input.currentText() == POStatus.RECEIVED.value else None,
                    status=self.status_input.currentText(),
                    notes=self.notes_input.toPlainText().strip() or None,
                    total=total_cents,
                    is_archived=(self.status_input.currentText() == POStatus.COMPLETE.value)
                )
                
                db.add(po)
                db.flush()
                
                # Save line items
                for row in range(self.items_table.rowCount()):
                    desc_widget = self.items_table.cellWidget(row, 0)
                    qty_widget = self.items_table.cellWidget(row, 1)
                    stock_widget = self.items_table.cellWidget(row, 2).findChild(QCheckBox)
                    job_widget = self.items_table.cellWidget(row, 3)
                    price_widget = self.items_table.cellWidget(row, 4)
                    
                    description = desc_widget.text().strip()
                    if not description:
                        continue
                        
                    quantity = qty_widget.value()
                    is_stock = stock_widget.isChecked()
                    job_id = job_widget.currentData() if not is_stock else None
                    unit_price_cents = int(price_widget.value() * 100)
                    total_cents = quantity * unit_price_cents
                    
                    item = POItem(
                        po_id=po.id,
                        description=description,
                        quantity=quantity,
                        unit_price=unit_price_cents,
                        total=total_cents,
                        is_stock=is_stock,
                        job_id=job_id
                    )
                    db.add(item)
                
                # Link PO to job if created from job editor
                if self.job:
                    if self.job not in po.jobs:
                        po.jobs.append(self.job)
                    
            else:
                # Update existing PO
                # Re-query to get attached object
                po = db.query(PurchaseOrder).get(self.po.id)
                
                po.supplier_name = supplier_name
                po.order_date = self.order_date_input.date().toPython()
                po.due_date = self.expected_date_input.date().toPython()
                po.received_date = self.received_date_input.date().toPython() if self.status_input.currentText() == POStatus.RECEIVED.value else None
                po.status = self.status_input.currentText()
                po.notes = self.notes_input.toPlainText().strip() or None

                po.total = total_cents
                
                # Auto-archive if status is Complete
                if self.status_input.currentText() == POStatus.COMPLETE.value:
                    po.is_archived = True
                
                # Delete old items
                db.query(POItem).filter(POItem.po_id == po.id).delete()
                
                # Save new items
                for row in range(self.items_table.rowCount()):
                    desc_widget = self.items_table.cellWidget(row, 0)
                    qty_widget = self.items_table.cellWidget(row, 1)
                    stock_widget = self.items_table.cellWidget(row, 2).findChild(QCheckBox)
                    job_widget = self.items_table.cellWidget(row, 3)
                    price_widget = self.items_table.cellWidget(row, 4)
                    
                    description = desc_widget.text().strip()
                    if not description:
                        continue
                        
                    quantity = qty_widget.value()
                    is_stock = stock_widget.isChecked()
                    job_id = job_widget.currentData() if not is_stock else None
                    unit_price_cents = int(price_widget.value() * 100)
                    total_cents = quantity * unit_price_cents
                    
                    item = POItem(
                        po_id=po.id,
                        description=description,
                        quantity=quantity,
                        unit_price=unit_price_cents,
                        total=total_cents,
                        is_stock=is_stock,
                        job_id=job_id
                    )
                    db.add(item)
                    
            db.commit()
            print(f"PO saved successfully. Status: {self.status_input.currentText()}, Archived: {self.po.is_archived if not self.is_new else False}")
            play_sound("celebration")
            self.accept()
            
        except Exception as e:
            print(f"Error saving PO: {e}")
            import traceback
            traceback.print_exc()
            play_sound("caution")
            QMessageBox.critical(self, "Error", f"Failed to save PO:\n{str(e)}")
            db.rollback()
