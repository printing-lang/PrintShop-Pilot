from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QTableView, QHeaderView, QLabel, QAbstractItemView, QLineEdit, QMessageBox)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QColor
from database import get_db
from models import Customer

class CustomerSearchTableModel(QAbstractTableModel):
    def __init__(self, customers=None):
        super().__init__()
        self.customers = customers or []
        self.headers = ["Contact", "Company", "Phone", "Email"]
        
    def rowCount(self, parent=QModelIndex()):
        return len(self.customers)
        
    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)
        
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
            
        customer = self.customers[index.row()]
        col = index.column()
        
        if role == Qt.DisplayRole:
            if col == 0:
                return customer.contact_name or ""
            elif col == 1:
                return customer.company_name
            elif col == 2:
                return customer.phone or ""
            elif col == 3:
                return customer.email or ""
                
        return None
        
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None
        
    def update_data(self, customers):
        self.beginResetModel()
        self.customers = customers
        self.endResetModel()

class CustomerSearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Find Customer")
        self.resize(600, 400)
        self.selected_customer = None
        
        layout = QVBoxLayout(self)
        
        # Search box
        search_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search customers...")
        self.search_box.textChanged.connect(self.on_search)
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)
        
        # Table
        self.table = QTableView()
        self.model = CustomerSearchTableModel()
        self.table.setModel(self.model)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self.select_customer)
        layout.addWidget(self.table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        select_btn = QPushButton("Select Customer")
        select_btn.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
        select_btn.clicked.connect(self.select_customer)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(select_btn)
        layout.addLayout(btn_layout)
        
        self.refresh_data()
        
    def on_search(self, text):
        self.refresh_data(search=text)
        
    def refresh_data(self, search=""):
        db = next(get_db())
        query = db.query(Customer).filter(Customer.is_archived == False)
        
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (Customer.company_name.like(search_filter)) |
                (Customer.contact_name.like(search_filter)) |
                (Customer.email.like(search_filter)) |
                (Customer.phone.like(search_filter))
            )
        
        customers = query.all()
        self.model.update_data(customers)
        db.close()
        
    def select_customer(self):
        indexes = self.table.selectionModel().selectedRows()
        if not indexes:
            return
            
        index = indexes[0]
        self.selected_customer = self.model.customers[index.row()]
        self.accept()
