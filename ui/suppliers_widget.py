from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QScrollArea, QFrame, QGridLayout, QLineEdit)
from PySide6.QtCore import Qt, QSize
from ui.assets import get_icon, play_sound
from database import get_db
from models import Supplier
from ui.supplier_card import SupplierCardWidget

class FlowLayout(QFrame):
    """Simple flow layout for cards"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("QFrame { background-color: #F0F0F0; border: none; }")
        self.grid = QGridLayout(self)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.grid.setContentsMargins(10, 10, 10, 10)
        self.grid.setSpacing(20)

    def clear(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def add_cards(self, suppliers, on_view, on_edit):
        self.clear()
        cols = 5
        for i, supplier in enumerate(suppliers):
            card = SupplierCardWidget(supplier)
            card.clicked.connect(on_view)
            card.edit_clicked.connect(on_edit)
            row = i // cols
            col = i % cols
            self.grid.addWidget(card, row, col)

class SuppliersWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QWidget { background-color: #F0F0F0; }")
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Title with icon
        title_container = QHBoxLayout()
        title_icon = QLabel()
        title_icon.setPixmap(get_icon("fa5s.truck", color="#2c3e50").pixmap(32, 32))
        title_container.addWidget(title_icon)
        
        title = QLabel("Suppliers")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50; background: transparent; margin-left: 8px;")
        title_container.addWidget(title)
        title_container.addStretch()
        
        header_layout.addLayout(title_container)
        header_layout.addStretch()
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search suppliers...")
        self.search_box.setFixedWidth(300)
        self.search_box.textChanged.connect(self.on_search)
        self.search_box.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background: white;
            }
        """)
        header_layout.addWidget(self.search_box)
        header_layout.addSpacing(10)
        
        # New Supplier Button
        self.new_supplier_btn = QPushButton(" New Supplier")
        self.new_supplier_btn.setIcon(get_icon("fa5s.plus", color="white"))
        self.new_supplier_btn.setIconSize(QSize(16, 16))
        self.new_supplier_btn.setCursor(Qt.PointingHandCursor)
        self.new_supplier_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        header_layout.addWidget(self.new_supplier_btn)
        
        layout.addLayout(header_layout)
        
        # Card View
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        self.cards_container = FlowLayout()
        self.scroll_area.setWidget(self.cards_container)
        layout.addWidget(self.scroll_area)
        
        self.new_supplier_btn.clicked.connect(self.open_new_supplier_dialog)
        self.refresh_data()

    def on_search(self, text):
        self.refresh_data(search=text)

    def open_new_supplier_dialog(self):
        from ui.supplier_editor import SupplierEditorDialog
        dialog = SupplierEditorDialog(self)
        if dialog.exec():
            self.refresh_data()

    def edit_supplier(self, supplier):
        from ui.supplier_editor import SupplierEditorDialog
        dialog = SupplierEditorDialog(self, supplier)
        if dialog.exec():
            self.refresh_data()
            
    def view_supplier(self, supplier):
        self.edit_supplier(supplier)

    def refresh_data(self, search=""):
        db = next(get_db())
        try:
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
            self.cards_container.add_cards(suppliers, self.view_supplier, self.edit_supplier)
            
        finally:
            db.close()
