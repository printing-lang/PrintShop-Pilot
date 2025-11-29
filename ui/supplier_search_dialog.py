from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QTableView, QHeaderView, QLabel, QAbstractItemView, QLineEdit)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from database import get_db
from models import Supplier

class SupplierSearchTableModel(QAbstractTableModel):
    def __init__(self, suppliers=None):
        super().__init__()
        self.suppliers = suppliers or []
        self.headers = ["Supplier Name", "Contact", "Phone", "Email"]
        
    def rowCount(self, parent=QModelIndex()):
        return len(self.suppliers)
        
    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)
        
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
            
        supplier = self.suppliers[index.row()]
        col = index.column()
        
        if role == Qt.DisplayRole:
            if col == 0:
                return supplier.supplier_name
            elif col == 1:
                return supplier.contact_name or ""
            elif col == 2:
                return supplier.phone or ""
            elif col == 3:
                return supplier.email or ""
                
        return None
        
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None
        
    def update_data(self, suppliers):
        self.beginResetModel()
        self.suppliers = suppliers
        self.endResetModel()

class SupplierSearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Find Supplier")
        self.resize(600, 400)
        self.selected_supplier = None
        
        layout = QVBoxLayout(self)
        
        # Search box
        search_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search suppliers...")
        self.search_box.textChanged.connect(self.on_search)
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)
        
        # Table
        self.table = QTableView()
        self.model = SupplierSearchTableModel()
        self.table.setModel(self.model)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self.select_supplier)
        layout.addWidget(self.table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        select_btn = QPushButton("Select Supplier")
        select_btn.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
        select_btn.clicked.connect(self.select_supplier)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(select_btn)
        layout.addLayout(btn_layout)
        
        self.refresh_data()
        
    def on_search(self, text):
        self.refresh_data(search=text)
        
    def refresh_data(self, search=""):
        db = next(get_db())
        query = db.query(Supplier).filter(Supplier.is_archived == False)
        
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (Supplier.supplier_name.like(search_filter)) |
                (Supplier.contact_name.like(search_filter)) |
                (Supplier.email.like(search_filter)) |
                (Supplier.phone.like(search_filter))
            )
        
        suppliers = query.all()
        self.model.update_data(suppliers)
        db.close()
        
    def select_supplier(self):
        indexes = self.table.selectionModel().selectedRows()
        if not indexes:
            return
            
        index = indexes[0]
        self.selected_supplier = self.model.suppliers[index.row()]
        self.accept()
