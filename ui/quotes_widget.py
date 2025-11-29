from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QScrollArea, QFrame, QGridLayout, QMessageBox, QLineEdit)
from PySide6.QtCore import Qt, QSize
from ui.assets import get_icon, play_sound
from database import get_db
from models import Quote, QuoteStatus
from ui.quote_card import QuoteCardWidget

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

    def add_cards(self, quotes, on_view, on_edit, on_print):
        self.clear()
        cols = 5 # Number of columns (5 cards wide)
        for i, quote in enumerate(quotes):
            card = QuoteCardWidget(quote)
            card.clicked.connect(on_view)
            card.edit_clicked.connect(on_edit)
            card.print_clicked.connect(on_print)
            row = i // cols
            col = i % cols
            self.grid.addWidget(card, row, col)

class QuotesWidget(QWidget):
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
        title_icon.setPixmap(get_icon("order_approve", color="#2c3e50").pixmap(32, 32))
        title_container.addWidget(title_icon)
        
        title = QLabel("Quotes Management")
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
            
            # Badge
            badge = QLabel(label_text)
            badge.setStyleSheet(f"""
                background-color: {color};
                color: {text_color};
                padding: 4px 8px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 11px;
            """)
            
            # Count
            count = QLabel("0")
            count.setStyleSheet("font-weight: bold; color: #2c3e50;")
            
            container.addWidget(badge)
            container.addWidget(count)
            
            return container, count

        # Draft (Grey)
        self.status_draft_layout, self.status_draft_count = create_status_badge("#95a5a6", "Draft")
        self.status_overview.addLayout(self.status_draft_layout)

        # Sent (Blue)
        self.status_sent_layout, self.status_sent_count = create_status_badge("#3498db", "Sent")
        self.status_overview.addLayout(self.status_sent_layout)

        # Accepted (Green)
        self.status_accepted_layout, self.status_accepted_count = create_status_badge("#27ae60", "Accepted")
        self.status_overview.addLayout(self.status_accepted_layout)

        # Rejected (Red)
        self.status_rejected_layout, self.status_rejected_count = create_status_badge("#e74c3c", "Rejected")
        self.status_overview.addLayout(self.status_rejected_layout)

        # Expired (Orange)
        self.status_expired_layout, self.status_expired_count = create_status_badge("#f39c12", "Expired")
        self.status_overview.addLayout(self.status_expired_layout)

        left_column.addLayout(self.status_overview)
        
        header_layout.addLayout(left_column)
        header_layout.addStretch()
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search quotes...")
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
        
        # Print button
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
        
        # New Quote Button
        self.new_quote_btn = QPushButton(" New Quote")
        self.new_quote_btn.setIcon(get_icon("fa5s.plus", color="white"))
        self.new_quote_btn.setIconSize(QSize(16, 16))
        self.new_quote_btn.setCursor(Qt.PointingHandCursor)
        self.new_quote_btn.setStyleSheet("""
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
        header_layout.addWidget(self.new_quote_btn)
        
        layout.addLayout(header_layout)
        
        # Card View (Scroll Area)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        self.cards_container = FlowLayout()
        self.scroll_area.setWidget(self.cards_container)
        
        layout.addWidget(self.scroll_area)
        
        self.new_quote_btn.clicked.connect(self.open_new_quote_dialog)
        self.print_btn.clicked.connect(self.print_quotes_page)
        
        self.refresh_data()

    def on_search(self, text):
        self.refresh_data(search=text)

    def open_new_quote_dialog(self):
        from ui.quote_editor import QuoteEditorDialog
        dialog = QuoteEditorDialog(self)
        if dialog.exec():
            self.refresh_data()

    def edit_quote(self, quote):
        from ui.quote_editor import QuoteEditorDialog
        dialog = QuoteEditorDialog(self, quote)
        if dialog.exec():
            self.refresh_data()
            
    def view_quote(self, quote):
        # For now, view is same as edit
        self.edit_quote(quote)

    def print_quote(self, quote):
        # Placeholder for single quote print
        QMessageBox.information(self, "Print Quote", f"Printing Quote {quote.quote_number} is not yet implemented.")

    def refresh_data(self, search=""):
        db = next(get_db())
        try:
            query = db.query(Quote).filter(Quote.is_archived == False)
            
            if search:
                search_filter = f"%{search}%"
                query = query.filter(
                    (Quote.quote_number.like(search_filter)) |
                    (Quote.customer_name.like(search_filter)) |
                    (Quote.description.like(search_filter))
                )
            
            quotes = query.order_by(Quote.quote_date.desc()).all()
            
            # Calculate status counts
            status_counts = {
                QuoteStatus.DRAFT: 0,
                QuoteStatus.SENT: 0,
                QuoteStatus.ACCEPTED: 0,
                QuoteStatus.REJECTED: 0,
                QuoteStatus.EXPIRED: 0
            }
            
            for quote in quotes:
                if quote.status in status_counts:
                    status_counts[quote.status] += 1
            
            # Update Status labels
            self.status_draft_count.setText(str(status_counts[QuoteStatus.DRAFT]))
            self.status_sent_count.setText(str(status_counts[QuoteStatus.SENT]))
            self.status_accepted_count.setText(str(status_counts[QuoteStatus.ACCEPTED]))
            self.status_rejected_count.setText(str(status_counts[QuoteStatus.REJECTED]))
            self.status_expired_count.setText(str(status_counts[QuoteStatus.EXPIRED]))
            
            # Update Cards
            self.cards_container.add_cards(quotes, self.view_quote, self.edit_quote, self.print_quote)
            
        finally:
            db.close()
            
    def print_quotes_page(self):
        """Print the entire Quotes page in landscape"""
        from PySide6.QtPrintSupport import QPrinter, QPrintDialog
        from PySide6.QtGui import QPainter, QPageLayout
        from PySide6.QtCore import QMarginsF
        
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageOrientation(QPageLayout.Landscape)
        margins = QMarginsF(10, 10, 10, 10)
        printer.setPageMargins(margins, QPageLayout.Millimeter)
        
        dialog = QPrintDialog(printer, self)
        if dialog.exec():
            painter = QPainter(printer)
            widget_to_print = self.scroll_area.widget()
            page_rect = printer.pageRect(QPrinter.DevicePixel)
            widget_rect = widget_to_print.rect()
            scale_x = page_rect.width() / widget_rect.width()
            scale_y = page_rect.height() / widget_rect.height()
            scale = min(scale_x, scale_y)
            painter.scale(scale, scale)
            widget_to_print.render(painter)
            painter.end()
