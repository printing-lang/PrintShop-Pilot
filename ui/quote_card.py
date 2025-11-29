from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                               QWidget)
from PySide6.QtCore import Qt, Signal, QSize
from ui.assets import get_icon
from models import Quote, QuoteStatus
from datetime import date

class QuoteCardWidget(QFrame):
    clicked = Signal(object)
    edit_clicked = Signal(object)
    print_clicked = Signal(object)

    def __init__(self, quote):
        super().__init__()
        self.quote = quote
        self.setFixedWidth(280)
        self.setFixedHeight(180)
        
        # Card background - light blue/cyan like JobCard and POCard
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #D5EEF2;
                border: 1px solid #B8D8DD;
                border-radius: 8px;
            }}
            QLabel {{ border: none; background: transparent; }}
            QPushButton {{
                border: none;
                background: transparent;
                color: #2c3e50;
                font-size: 11px;
                padding: 4px 8px;
            }}
            QPushButton:hover {{
                background-color: rgba(0, 0, 0, 0.05);
                border-radius: 4px;
            }}
        """)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)
        
        # LEFT COLUMN
        left_layout = QVBoxLayout()
        left_layout.setSpacing(4)
        
        # Quote Number
        quote_num = QLabel(quote.quote_number)
        quote_num.setStyleSheet("font-weight: bold; font-size: 14px; color: #546E7A;")
        left_layout.addWidget(quote_num)
        
        # Customer Name
        customer = QLabel(quote.customer_name)
        customer.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        customer.setWordWrap(True)
        left_layout.addWidget(customer)
        
        # Total
        total_label = QLabel(f"${quote.total / 100:.2f}")
        total_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #27ae60;")
        left_layout.addWidget(total_label)
        
        left_layout.addStretch()
        
        # Quote / Expiry Date
        date_text = quote.quote_date.strftime("%b %d, %Y") if quote.quote_date else "No Date"
        if quote.expiry_date:
            date_label = QLabel(f"QUOTE: {date_text}\nEXPIRES: {quote.expiry_date.strftime('%b %d, %Y')}")
        else:
            date_label = QLabel(f"QUOTE: {date_text}")
        date_label.setStyleSheet("color: #546E7A; font-size: 10px; font-weight: bold; line-height: 1.2;")
        left_layout.addWidget(date_label)
        
        # Bottom buttons row
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(5)
        
        # View button
        view_btn = QPushButton(" View")
        view_btn.setIcon(get_icon("folder_eye_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24"))
        view_btn.setIconSize(QSize(14, 14))
        view_btn.setCursor(Qt.PointingHandCursor)
        view_btn.clicked.connect(self._on_view_clicked)
        buttons_row.addWidget(view_btn)
        
        # Edit button
        edit_btn = QPushButton(" Edit")
        edit_btn.setIcon(get_icon("fa5s.edit"))
        edit_btn.setIconSize(QSize(14, 14))
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.clicked.connect(self._on_edit_clicked)
        buttons_row.addWidget(edit_btn)
        
        # Print button
        print_btn = QPushButton(" Print")
        print_btn.setIcon(get_icon("print_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24"))
        print_btn.setIconSize(QSize(16, 16))
        print_btn.setCursor(Qt.PointingHandCursor)
        print_btn.clicked.connect(self._on_print_clicked)
        buttons_row.addWidget(print_btn)
        
        left_layout.addLayout(buttons_row)
        
        main_layout.addLayout(left_layout)
        
        # RIGHT COLUMN
        right_layout = QVBoxLayout()
        right_layout.setSpacing(6)
        right_layout.setAlignment(Qt.AlignTop)
        
        # Status badge
        status_badge = QLabel(quote.status.upper())
        status_bg, status_text = self._get_status_colors(quote.status)
        status_badge.setStyleSheet(f"""
            background-color: {status_bg};
            color: {status_text};
            padding: 4px 8px;
            border-radius: 8px;
            font-size: 9px;
            font-weight: bold;
        """)
        status_badge.setAlignment(Qt.AlignCenter)
        status_badge.setWordWrap(True)
        right_layout.addWidget(status_badge)
        
        right_layout.addStretch()
        
        main_layout.addLayout(right_layout)
    
    def _on_view_clicked(self):
        self.clicked.emit(self.quote)
    
    def _on_edit_clicked(self):
        self.edit_clicked.emit(self.quote)
    
    def _on_print_clicked(self):
        self.print_clicked.emit(self.quote)
    
    def _get_status_colors(self, status):
        """Get background and text colors for status badge"""
        if status == QuoteStatus.DRAFT:
            return "#95a5a6", "#FFFFFF"  # Grey
        elif status == QuoteStatus.SENT:
            return "#3498db", "#FFFFFF"  # Blue
        elif status == QuoteStatus.ACCEPTED:
            return "#27ae60", "#FFFFFF"  # Green
        elif status == QuoteStatus.REJECTED:
            return "#e74c3c", "#FFFFFF"  # Red
        elif status == QuoteStatus.EXPIRED:
            return "#f39c12", "#FFFFFF"  # Orange
        else:
            return "#95a5a6", "#FFFFFF"  # Default grey
