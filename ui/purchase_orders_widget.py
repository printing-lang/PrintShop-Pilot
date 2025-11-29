from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QScrollArea, QFrame, QGridLayout, QMessageBox, QLineEdit)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor
from ui.assets import get_icon, play_sound
from database import get_db
from models import PurchaseOrder, POStatus
from datetime import date
from ui.po_card import POCardWidget

class FlowLayout(QFrame):
    """Simple flow layout for cards"""
    def __init__(self, parent=None):
        super().__init__(parent)
        # Grey background
        self.setStyleSheet("QFrame { background-color: #F0F0F0; border: none; }")
        
        # Use GridLayout for card arrangement
        self.grid = QGridLayout(self)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.grid.setContentsMargins(10, 10, 10, 10)
        self.grid.setSpacing(20)

    def clear(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def add_cards(self, pos, on_view, on_edit, on_print):
        self.clear()
        cols = 5 # Number of columns (5 cards wide)
        for i, po in enumerate(pos):
            card = POCardWidget(po)
            card.clicked.connect(on_view)
            card.edit_clicked.connect(on_edit)
            card.print_clicked.connect(on_print)
            row = i // cols
            col = i % cols
            self.grid.addWidget(card, row, col)

class PurchaseOrdersWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # Set grey background
        self.setStyleSheet("QWidget { background-color: #F0F0F0; }")
        
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Left Column (Title + Stats)
        left_column = QVBoxLayout()
        left_column.setSpacing(15)
        
        # Title with icon
        title_container = QHBoxLayout()
        title_icon = QLabel()
        title_icon.setPixmap(get_icon("add_business_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24").pixmap(32, 32)) # Using add_business as PO icon
        title_container.addWidget(title_icon)
        
        title = QLabel("Purchase Orders")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50; background: transparent; margin-left: 8px;")
        title_container.addWidget(title)
        title_container.addStretch()
        
        left_column.addLayout(title_container)
        
        # Traffic Light Overview
        self.traffic_lights = QHBoxLayout()
        self.traffic_lights.setSpacing(20)
        self.traffic_lights.setAlignment(Qt.AlignLeft)

        def create_light(color, label_text):
            container = QHBoxLayout()
            container.setSpacing(5)
            
            # Pill Badge
            badge = QLabel(label_text)
            badge.setStyleSheet(f"""
                background-color: {color};
                color: white;
                padding: 4px 12px;
                border-radius: 12px;
                font-weight: bold;
                font-size: 12px;
            """)
            
            # Count
            count = QLabel("0")
            count.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 14px;")
            
            container.addWidget(badge)
            container.addWidget(count)
            
            return container, count

        # Blue - To Order
        self.to_order_layout, self.to_order_count = create_light("#3498db", "To Order")
        self.traffic_lights.addLayout(self.to_order_layout)

        # Green - Waiting Stock
        self.waiting_stock_layout, self.waiting_stock_count = create_light("#2ecc71", "Waiting Stock")
        self.traffic_lights.addLayout(self.waiting_stock_layout)

        # Orange - Received
        self.received_layout, self.received_count = create_light("#E67E22", "Received")
        self.traffic_lights.addLayout(self.received_layout)
        
        # Red - Overdue
        self.overdue_layout, self.overdue_count = create_light("#e74c3c", "Overdue")
        self.traffic_lights.addLayout(self.overdue_layout)

        left_column.addLayout(self.traffic_lights)
        
        header_layout.addLayout(left_column)
        header_layout.addStretch()
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search purchase orders...")
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
        
        # Print button (Page)
        self.print_btn = QPushButton()
        self.print_btn.setIcon(get_icon("print_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24 Inverted"))
        self.print_btn.setIconSize(QSize(20, 20))
        self.print_btn.setFixedSize(40, 40)
        self.print_btn.setCursor(Qt.PointingHandCursor)
        self.print_btn.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
        """)
        header_layout.addWidget(self.print_btn)
        header_layout.addSpacing(10)
        
        # New PO Button
        self.new_po_btn = QPushButton(" New PO")
        self.new_po_btn.setIcon(get_icon("fa5s.plus", color="white"))
        self.new_po_btn.setIconSize(QSize(16, 16))
        self.new_po_btn.setCursor(Qt.PointingHandCursor)
        self.new_po_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        header_layout.addWidget(self.new_po_btn)
        
        layout.addLayout(header_layout)
        
        # Card View (Scroll Area)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        self.cards_container = FlowLayout()
        self.scroll_area.setWidget(self.cards_container)
        
        layout.addWidget(self.scroll_area)
        
        self.new_po_btn.clicked.connect(self.open_new_po_dialog)
        self.print_btn.clicked.connect(self.print_pos_page)
        
        self.refresh_data()

    def on_search(self, text):
        self.refresh_data(search=text)

    def open_new_po_dialog(self):
        from ui.po_editor import POEditorDialog
        dialog = POEditorDialog(self)
        if dialog.exec():
            self.refresh_data()

    def edit_po(self, po):
        from ui.po_editor import POEditorDialog
        dialog = POEditorDialog(self, po)
        if dialog.exec():
            self.refresh_data()
            
    def view_po(self, po):
        # For now, view is same as edit but maybe read-only?
        # Reusing edit dialog for simplicity as per current implementation
        # Or we can make a read-only mode later.
        self.edit_po(po)

    def print_po(self, po):
        # Placeholder for single PO print
        QMessageBox.information(self, "Print PO", f"Printing PO {po.po_number} is not yet implemented.")

    def refresh_data(self, search=""):
        db = next(get_db())
        try:
            query = db.query(PurchaseOrder).filter(PurchaseOrder.is_archived == False)
            
            if search:
                search_filter = f"%{search}%"
                query = query.filter(
                    (PurchaseOrder.po_number.like(search_filter)) |
                    (PurchaseOrder.supplier_name.like(search_filter)) |
                    (PurchaseOrder.description.like(search_filter))
                )
            
            pos = query.order_by(PurchaseOrder.created_at.desc()).all()
            
            # Calculate counts
            today = date.today()
            to_order = 0
            waiting_stock = 0
            received = 0
            overdue = 0
            
            for po in pos:
                if po.status == POStatus.TO_ORDER:
                    to_order += 1
                elif po.status == POStatus.RECEIVED:
                    received += 1
                elif po.status == POStatus.WAITING_STOCK:
                    if po.due_date and po.due_date < today:
                        overdue += 1
                    else:
                        waiting_stock += 1
            
            # Update Traffic Light labels
            self.to_order_count.setText(str(to_order))
            self.waiting_stock_count.setText(str(waiting_stock))
            self.received_count.setText(str(received))
            self.overdue_count.setText(str(overdue))
            
            # Update Cards
            self.cards_container.add_cards(pos, self.view_po, self.edit_po, self.print_po)
            
        finally:
            db.close()
            
    def print_pos_page(self):
        """Print the entire PO Management page in landscape"""
        from PySide6.QtPrintSupport import QPrinter, QPrintDialog
        from PySide6.QtGui import QPainter, QPageLayout
        from PySide6.QtCore import QMarginsF
        
        printer = QPrinter(QPrinter.HighResolution)
        # Set landscape orientation
        printer.setPageOrientation(QPageLayout.Landscape)
        # Set margins
        margins = QMarginsF(10, 10, 10, 10)
        printer.setPageMargins(margins, QPageLayout.Millimeter)
        
        dialog = QPrintDialog(printer, self)
        if dialog.exec():
            painter = QPainter(printer)
            
            # Get the scroll area widget (cards container)
            widget_to_print = self.scroll_area.widget()
            
            # Calculate scaling to fit to page
            page_rect = printer.pageRect(QPrinter.DevicePixel)
            widget_rect = widget_to_print.rect()
            
            # Scale to fit width and height
            scale_x = page_rect.width() / widget_rect.width()
            scale_y = page_rect.height() / widget_rect.height()
            scale = min(scale_x, scale_y)
            
            painter.scale(scale, scale)
            
            # Render the widget
            widget_to_print.render(painter)
            
            painter.end()
