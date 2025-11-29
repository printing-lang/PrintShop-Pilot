from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                               QWidget, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPainter, QColor, QPen
from ui.assets import get_icon
from models import Job

class JobCardWidget(QFrame):
    clicked = Signal(object) # Emits the job object for viewing
    edit_clicked = Signal(object) # Emits the job object for editing
    print_clicked = Signal(object) # Emits the job object for printing

    def __init__(self, job):
        super().__init__()
        self.job = job
        self.setFixedWidth(280)
        self.setFixedHeight(200)
        
        # Card background - light blue/cyan like mockup
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
        
        # Traffic light circle
        traffic_color = self._get_traffic_light_color()
        circle_widget = QWidget()
        circle_widget.setFixedSize(35, 35)
        circle_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {traffic_color};
                border-radius: 17px;
                border: none;
            }}
        """)
        left_layout.addWidget(circle_widget)
        
        # Customer name
        customer = QLabel(job.customer_name)
        customer.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        customer.setWordWrap(True)
        left_layout.addWidget(customer)
        
        # Order type
        type_label = QLabel(job.order_type)
        type_label.setStyleSheet("color: #546E7A; font-size: 11px;")
        type_label.setWordWrap(True)
        left_layout.addWidget(type_label)
        
        left_layout.addStretch()
        
        # Due date (colored to match traffic light)
        due_date_text = job.due_date.strftime("%b %d, %Y") if job.due_date else "No Due Date"
        date_label = QLabel(f"DUE DATE\n{due_date_text}")
        date_label.setStyleSheet(f"color: {traffic_color}; font-size: 10px; font-weight: bold; line-height: 1.2;")
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
        
        # PO Count
        try:
            po_count = len(self.job.purchase_orders)
            if po_count > 0:
                po_btn = QPushButton(f" {po_count} PO")
                po_btn.setIcon(get_icon("fa5s.shopping-cart", color="#2c3e50"))
                po_btn.setIconSize(QSize(14, 14))
                po_btn.setCursor(Qt.PointingHandCursor)
                # Optional: Connect to view POs? For now just an indicator.
                # po_btn.clicked.connect(...) 
                buttons_row.addWidget(po_btn)
        except:
            pass # Handle case where relationship might not be loaded or other error
        
        left_layout.addLayout(buttons_row)
        
        main_layout.addLayout(left_layout)
        
        # RIGHT COLUMN
        right_layout = QVBoxLayout()
        right_layout.setSpacing(6)
        right_layout.setAlignment(Qt.AlignTop)
        
        # Priority badge
        priority_badge = QLabel(job.priority.upper())
        priority_bg, priority_text = self._get_priority_colors(job.priority)
        priority_badge.setStyleSheet(f"""
            background-color: {priority_bg};
            color: {priority_text};
            padding: 4px 8px;
            border-radius: 8px;
            font-size: 9px;
            font-weight: bold;
        """)
        priority_badge.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(priority_badge)
        
        # Status badge
        status_badge = QLabel(job.status.upper())
        status_bg, status_text = self._get_status_colors(job.status)
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
        
        # Source
        source_label = QLabel(f"SOURCE\n{job.order_source}")
        source_label.setStyleSheet("color: #546E7A; font-size: 10px; line-height: 1.2;")
        source_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(source_label)
        
        # Shop (using assigned_to field or default)
        shop_text = job.assigned_to if job.assigned_to else "Main"
        shop_label = QLabel(f"SHOP\n{shop_text}")
        shop_label.setStyleSheet("color: #546E7A; font-size: 10px; line-height: 1.2;")
        shop_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(shop_label)
        
        right_layout.addStretch()
        
        main_layout.addLayout(right_layout)
    
    def _on_view_clicked(self):
        """Handle view button click"""
        self.clicked.emit(self.job)
    
    def _on_edit_clicked(self):
        """Handle edit button click"""
        self.edit_clicked.emit(self.job)
    
    def _on_print_clicked(self):
        """Handle print button click"""
        self.print_clicked.emit(self.job)
    
    def _get_traffic_light_color(self):
        """Get color for traffic light based on due date"""
        from datetime import date
        
        if not self.job.due_date:
            return "#2196F3"  # Blue if no due date
        
        today = date.today()
        due_date = self.job.due_date
        
        if due_date < today:
            return "#F44336"  # Red - Overdue
        elif due_date == today:
            return "#FF9800"  # Orange - Due Today
        else:
            return "#4CAF50"  # Green - On Time
    
    def _get_priority_colors(self, priority):
        """Get background and text colors for priority badge"""
        priority_lower = priority.lower()
        if "miracle" in priority_lower:
            return "#FF0000", "#FFFFFF"  # Bright Red, White Writing
        elif "express" in priority_lower:
            return "#FF8C00", "#FFFFFF"  # Dark Orange, White Writing
        else:  # Normal
            return "#00FF00", "#FFFFFF"  # Bright Green, White Writing
    
    def _get_status_colors(self, status):
        """Get background and text colors for status badge"""
        status_lower = status.lower()
        if "job created" in status_lower or "created" in status_lower:
            return "#00BFFF", "#FFFFFF"  # Bright Blue, White Writing
        elif "awaiting stock" in status_lower or "waiting stock" in status_lower:
            return "#9C27B0", "#FFFFFF"  # Bright Purple, White Writing
        elif "in queue" in status_lower:
            return "#00FF00", "#FFFFFF"  # Bright Green, White Writing
        elif "out queue" in status_lower:
            return "#FFD700", "#000000"  # Daisy Yellow, Black Writing
        elif "customer notified" in status_lower or "notified" in status_lower:
            return "#000000", "#FFFFFF"  # Black, White Writing
        elif "complete" in status_lower:
            return "#FFFFFF", "#000000"  # White, Black Writing
        else:
            return "#607D8B", "#FFFFFF"  # Default Blue-gray, White Writing
