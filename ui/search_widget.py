from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLineEdit, QScrollArea, QFrame, QGridLayout, QLabel, QButtonGroup)
from PySide6.QtCore import Qt, QSize
from ui.assets import get_icon
from database import get_db
from models import Job, Quote, Task, PurchaseOrder, Customer, Supplier
from ui.job_card import JobCardWidget
from ui.quote_card import QuoteCardWidget
from ui.task_card import TaskCardWidget
from ui.po_card import POCardWidget
from ui.customer_card import CustomerCardWidget
from ui.supplier_card import SupplierCardWidget

class FlowLayout(QFrame):
    """Simple flow layout for cards"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("QFrame { background-color: transparent; border: none; }")
        
        self.grid = QGridLayout(self)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.grid.setContentsMargins(10, 10, 10, 10)
        self.grid.setSpacing(20)

    def clear(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def add_widget(self, widget, index, cols=4):
        row = index // cols
        col = index % cols
        self.grid.addWidget(widget, row, col)

class SearchWidget(QWidget):
    def __init__(self, mode="active"):
        super().__init__()
        self.mode = mode
        self.setStyleSheet("QWidget { background-color: #F0F0F0; }")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Title
        title_container = QHBoxLayout()
        icon_name = "pageview" if mode == "active" else "fa5s.archive"
        title_icon = QLabel()
        title_icon.setPixmap(get_icon(icon_name, color="#2c3e50").pixmap(32, 32))
        title_container.addWidget(title_icon)
        
        display_title = "Search" if mode == "active" else "Archive Search"
        title = QLabel(display_title)
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50; background: transparent; margin-left: 8px;")
        title_container.addWidget(title)
        title_container.addStretch()
        header_layout.addLayout(title_container)
        
        layout.addLayout(header_layout)
        
        # Search Bar
        search_container = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(f"Search {display_title}...")
        self.search_input.setFixedHeight(45)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 0 15px;
                font-size: 16px;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        self.search_input.returnPressed.connect(self.perform_search)
        search_container.addWidget(self.search_input)
        
        search_btn = QPushButton("Search")
        search_btn.setFixedSize(100, 45)
        search_btn.setCursor(Qt.PointingHandCursor)
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        search_btn.clicked.connect(self.perform_search)
        search_container.addWidget(search_btn)
        
        layout.addLayout(search_container)
        
        # Filters
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        
        self.filter_group = QButtonGroup(self)
        self.filter_group.setExclusive(True)
        
        # Removed "Archive" from filters as it's now a separate mode
        filters = ["All", "Jobs", "Quotes", "Tasks", "Purchase Orders", "Customers", "Suppliers"]
        
        for i, f_name in enumerate(filters):
            btn = QPushButton(f_name)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(35)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    color: #7f8c8d;
                    border: 1px solid #bdc3c7;
                    border-radius: 17px;
                    padding: 0 15px;
                    font-weight: bold;
                }
                QPushButton:checked {
                    background-color: #2c3e50;
                    color: white;
                    border: none;
                }
                QPushButton:hover:!checked {
                    background-color: #ecf0f1;
                }
            """)
            self.filter_group.addButton(btn, i)
            filter_layout.addWidget(btn)
            
            if f_name == "All":
                btn.setChecked(True)
                
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        self.filter_group.buttonClicked.connect(self.perform_search)
        
        # Results Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.results_container = FlowLayout()
        self.scroll_area.setWidget(self.results_container)
        
        layout.addWidget(self.scroll_area)
        
        # Initial empty state
        self.show_empty_state("Enter a search term to begin")

    def show_empty_state(self, message):
        self.results_container.clear()
        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #95a5a6; font-size: 18px; margin-top: 50px;")
        self.results_container.grid.addWidget(label, 0, 0)

    def perform_search(self):
        query = self.search_input.text().strip()
        if not query:
            self.show_empty_state("Enter a search term to begin")
            return
            
        filter_text = self.filter_group.checkedButton().text()
        
        # Determine if we are searching active or archived items
        search_archived = (self.mode == "archive")
        
        self.results_container.clear()
        
        db = next(get_db())
        results_found = 0
        card_index = 0
        
        try:
            # Helper to add widget
            def add_result(widget):
                nonlocal card_index, results_found
                self.results_container.add_widget(widget, card_index, cols=4)
                card_index += 1
                results_found += 1

            # JOBS
            if filter_text in ["All", "Jobs"]:
                q = db.query(Job).filter(Job.is_archived == search_archived)
                
                if query:
                    search_filter = (
                        Job.job_number.ilike(f"%{query}%") |
                        Job.customer_name.ilike(f"%{query}%") |
                        Job.order_type.ilike(f"%{query}%") |
                        Job.notes.ilike(f"%{query}%")
                    )
                    q = q.filter(search_filter)
                
                for job in q.all():
                    card = JobCardWidget(job)
                    add_result(card)

            # QUOTES
            if filter_text in ["All", "Quotes"]:
                q = db.query(Quote).filter(Quote.is_archived == search_archived)
                
                if query:
                    search_filter = (
                        Quote.quote_number.ilike(f"%{query}%") |
                        Quote.customer_name.ilike(f"%{query}%") |
                        Quote.notes.ilike(f"%{query}%")
                    )
                    q = q.filter(search_filter)
                
                for quote in q.all():
                    card = QuoteCardWidget(quote)
                    add_result(card)

            # TASKS
            if filter_text in ["All", "Tasks"]:
                q = db.query(Task).filter(Task.is_archived == search_archived)
                
                if query:
                    search_filter = (
                        Task.task_number.ilike(f"%{query}%") |
                        Task.title.ilike(f"%{query}%") |
                        Task.description.ilike(f"%{query}%") |
                        Task.assigned_to.ilike(f"%{query}%")
                    )
                    q = q.filter(search_filter)
                
                for task in q.all():
                    card = TaskCardWidget(task)
                    add_result(card)

            # PURCHASE ORDERS
            if filter_text in ["All", "Purchase Orders"]:
                q = db.query(PurchaseOrder).filter(PurchaseOrder.is_archived == search_archived)
                
                if query:
                    search_filter = (
                        PurchaseOrder.po_number.ilike(f"%{query}%") |
                        PurchaseOrder.supplier_name.ilike(f"%{query}%") |
                        PurchaseOrder.notes.ilike(f"%{query}%")
                    )
                    q = q.filter(search_filter)
                
                for po in q.all():
                    card = POCardWidget(po)
                    add_result(card)

            # CUSTOMERS
            if filter_text in ["All", "Customers"]:
                q = db.query(Customer).filter(Customer.is_archived == search_archived)
                
                if query:
                    search_filter = (
                        Customer.customer_number.ilike(f"%{query}%") |
                        Customer.company_name.ilike(f"%{query}%") |
                        Customer.contact_name.ilike(f"%{query}%") |
                        Customer.email.ilike(f"%{query}%")
                    )
                    q = q.filter(search_filter)
                
                for customer in q.all():
                    card = CustomerCardWidget(customer)
                    add_result(card)

            # SUPPLIERS
            if filter_text in ["All", "Suppliers"]:
                q = db.query(Supplier).filter(Supplier.is_archived == search_archived)
                
                if query:
                    search_filter = (
                        Supplier.supplier_name.ilike(f"%{query}%") |
                        Supplier.contact_name.ilike(f"%{query}%") |
                        Supplier.email.ilike(f"%{query}%") |
                        Supplier.services_supplies.ilike(f"%{query}%")
                    )
                    q = q.filter(search_filter)
                
                for supplier in q.all():
                    card = SupplierCardWidget(supplier)
                    add_result(card)

            if results_found == 0:
                self.show_empty_state("No results found matching your criteria.")
                
        finally:
            db.close()
