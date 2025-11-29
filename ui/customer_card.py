from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton)
from PySide6.QtCore import Qt, Signal, QSize, QUrl
from PySide6.QtGui import QDesktopServices
from ui.assets import get_icon
from models import Customer

class CustomerCardWidget(QFrame):
    clicked = Signal(object)
    edit_clicked = Signal(object)
    email_clicked = Signal(object)

    def __init__(self, customer):
        super().__init__()
        self.customer = customer
        self.setFixedWidth(280)
        self.setFixedHeight(180)
        
        # Card background
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
        
        # Company Name
        company = QLabel(customer.company_name)
        company.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        company.setWordWrap(True)
        left_layout.addWidget(company)
        
        # Contact Name
        if customer.contact_name:
            contact = QLabel(customer.contact_name)
            contact.setStyleSheet("color: #546E7A; font-size: 12px;")
            left_layout.addWidget(contact)
        
        # Email
        if customer.email:
            email = QLabel(customer.email)
            email.setStyleSheet("color: #546E7A; font-size: 10px;")
            email.setWordWrap(True)
            left_layout.addWidget(email)
        
        # Phone
        if customer.phone or customer.mobile:
            phone_text = customer.phone or customer.mobile
            phone = QLabel(f"☎ {phone_text}")
            phone.setStyleSheet("color: #546E7A; font-size: 10px;")
            left_layout.addWidget(phone)
        
        left_layout.addStretch()
        
        # Bottom buttons
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(5)
        
        view_btn = QPushButton(" View")
        view_btn.setIcon(get_icon("folder_eye_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24"))
        view_btn.setIconSize(QSize(14, 14))
        view_btn.setCursor(Qt.PointingHandCursor)
        view_btn.clicked.connect(self._on_view_clicked)
        buttons_row.addWidget(view_btn)
        
        edit_btn = QPushButton(" Edit")
        edit_btn.setIcon(get_icon("fa5s.edit"))
        edit_btn.setIconSize(QSize(14, 14))
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.clicked.connect(self._on_edit_clicked)
        buttons_row.addWidget(edit_btn)
        
        if customer.email:
            email_btn = QPushButton(" Email")
            email_btn.setIcon(get_icon("fa5s.envelope"))
            email_btn.setIconSize(QSize(14, 14))
            email_btn.setCursor(Qt.PointingHandCursor)
            email_btn.clicked.connect(self._on_email_clicked)
            buttons_row.addWidget(email_btn)
        
        left_layout.addLayout(buttons_row)
        main_layout.addLayout(left_layout)
        
        # RIGHT COLUMN
        right_layout = QVBoxLayout()
        right_layout.setSpacing(6)
        right_layout.setAlignment(Qt.AlignTop)
        
        # Status badge
        status_badge = QLabel(customer.status.upper())
        status_bg, status_text = self._get_status_colors(customer.status)
        status_badge.setStyleSheet(f"""
            background-color: {status_bg};
            color: {status_text};
            padding: 4px 8px;
            border-radius: 8px;
            font-size: 9px;
            font-weight: bold;
        """)
        status_badge.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(status_badge)
        right_layout.addStretch()
        
        main_layout.addLayout(right_layout)
    
    def _on_view_clicked(self):
        self.clicked.emit(self.customer)
    
    def _on_edit_clicked(self):
        self.edit_clicked.emit(self.customer)
    
    def _on_email_clicked(self):
        QDesktopServices.openUrl(QUrl(f"mailto:{self.customer.email}"))
    
    def _get_status_colors(self, status):
        if status == "Active":
            return "#27ae60", "#FFFFFF"  # Green
        elif status == "On Hold":
            return "#f39c12", "#FFFFFF"  # Orange
        elif status == "Archived":
            return "#95a5a6", "#FFFFFF"  # Grey
        elif status == "Banned":
            return "#e74c3c", "#FFFFFF"  # Red
        else:
            return "#95a5a6", "#FFFFFF"  # Default grey
