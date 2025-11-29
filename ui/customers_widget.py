from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QScrollArea, QFrame, QGridLayout, QLineEdit, QMessageBox)
from PySide6.QtCore import Qt, QSize
from ui.assets import get_icon, play_sound
from database import get_db
from models import Customer
from ui.customer_card import CustomerCardWidget

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

    def add_cards(self, customers, on_view, on_edit):
        self.clear()
        cols = 5
        for i, customer in enumerate(customers):
            card = CustomerCardWidget(customer)
            card.clicked.connect(on_view)
            card.edit_clicked.connect(on_edit)
            row = i // cols
            col = i % cols
            self.grid.addWidget(card, row, col)

class CustomersWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QWidget { background-color: #F0F0F0; }")
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        left_column = QVBoxLayout()
        left_column.setSpacing(15)
        
        # Title with icon
        title_container = QHBoxLayout()
        title_icon = QLabel()
        title_icon.setPixmap(get_icon("person_add").pixmap(32, 32))
        title_container.addWidget(title_icon)
        
        title = QLabel("Customer Management")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50; background: transparent; margin-left: 8px;")
        title_container.addWidget(title)
        title_container.addStretch()
        left_column.addLayout(title_container)
        
        # Status Overview
        self.status_overview = QHBoxLayout()
        self.status_overview.setSpacing(15)
        self.status_overview.setAlignment(Qt.AlignLeft)

        def create_status_badge(color, label_text, text_color="#FFFFFF"):
            container = QHBoxLayout()
            container.setSpacing(5)
            badge = QLabel(label_text)
            badge.setStyleSheet(f"""
                background-color: {color};
                color: {text_color};
                padding: 4px 8px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 11px;
            """)
            count = QLabel("0")
            count.setStyleSheet("font-weight: bold; color: #2c3e50;")
            container.addWidget(badge)
            container.addWidget(count)
            return container, count

        self.status_active_layout, self.status_active_count = create_status_badge("#27ae60", "Active")
        self.status_overview.addLayout(self.status_active_layout)

        self.status_hold_layout, self.status_hold_count = create_status_badge("#f39c12", "On Hold")
        self.status_overview.addLayout(self.status_hold_layout)

        self.status_banned_layout, self.status_banned_count = create_status_badge("#e74c3c", "Banned")
        self.status_overview.addLayout(self.status_banned_layout)

        left_column.addLayout(self.status_overview)
        header_layout.addLayout(left_column)
        header_layout.addStretch()
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search customers...")
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
        
        # New Customer Button
        self.new_customer_btn = QPushButton(" New Customer")
        self.new_customer_btn.setIcon(get_icon("fa5s.plus", color="white"))
        self.new_customer_btn.setIconSize(QSize(16, 16))
        self.new_customer_btn.setCursor(Qt.PointingHandCursor)
        self.new_customer_btn.setStyleSheet("""
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
        header_layout.addWidget(self.new_customer_btn)
        
        layout.addLayout(header_layout)
        
        # Card View
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        self.cards_container = FlowLayout()
        self.scroll_area.setWidget(self.cards_container)
        layout.addWidget(self.scroll_area)
        
        self.new_customer_btn.clicked.connect(self.open_new_customer_dialog)
        self.refresh_data()

    def on_search(self, text):
        self.refresh_data(search=text)

    def open_new_customer_dialog(self):
        from ui.customer_editor import CustomerEditorDialog
        dialog = CustomerEditorDialog(self)
        if dialog.exec():
            self.refresh_data()

    def edit_customer(self, customer):
        from ui.customer_editor import CustomerEditorDialog
        dialog = CustomerEditorDialog(self, customer)
        if dialog.exec():
            self.refresh_data()
            
    def view_customer(self, customer):
        self.edit_customer(customer)

    def refresh_data(self, search=""):
        db = next(get_db())
        try:
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
            
            # Calculate status counts
            status_counts = {
                "Active": 0,
                "On Hold": 0,
                "Banned": 0
            }
            
            for customer in customers:
                if customer.status in status_counts:
                    status_counts[customer.status] += 1
            
            self.status_active_count.setText(str(status_counts["Active"]))
            self.status_hold_count.setText(str(status_counts["On Hold"]))
            self.status_banned_count.setText(str(status_counts["Banned"]))
            
            self.cards_container.add_cards(customers, self.view_customer, self.edit_customer)
            
        finally:
            db.close()
