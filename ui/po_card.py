from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                               QWidget, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPainter, QColor, QPen
from ui.assets import get_icon
from models import PurchaseOrder, POStatus
from datetime import date

class POCardWidget(QFrame):
    clicked = Signal(object) # Emits the po object for viewing
    edit_clicked = Signal(object) # Emits the po object for editing
    print_clicked = Signal(object) # Emits the po object for printing

    def __init__(self, po):
        super().__init__()
        self.po = po
        self.setFixedWidth(280)
        self.setFixedHeight(180)
        
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
        
        # PO Number
        po_num = QLabel(po.po_number)
        po_num.setStyleSheet("font-weight: bold; font-size: 14px; color: #546E7A;")
        left_layout.addWidget(po_num)
        
        # Supplier Name
        supplier = QLabel(po.supplier_name)
        supplier.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        supplier.setWordWrap(True)
        left_layout.addWidget(supplier)
        
        left_layout.addStretch()
        
        # Due date / Received Date
        if po.status == POStatus.RECEIVED and po.received_date:
            date_text = po.received_date.strftime("%b %d, %Y")
            date_label = QLabel(f"RECEIVED\n{date_text}")
            date_label.setStyleSheet(f"color: #E67E22; font-size: 10px; font-weight: bold; line-height: 1.2;")
        else:
            date_text = po.due_date.strftime("%b %d, %Y") if po.due_date else "No Due Date"
            date_label = QLabel(f"DUE DATE\n{date_text}")
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
        
        left_layout.addLayout(buttons_row)
        
        main_layout.addLayout(left_layout)
        
        # RIGHT COLUMN
        right_layout = QVBoxLayout()
        right_layout.setSpacing(6)
        right_layout.setAlignment(Qt.AlignTop)
        
        # Linked Jobs Header
        linked_jobs_label = QLabel("Linked Jobs")
        linked_jobs_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        linked_jobs_label.setAlignment(Qt.AlignRight)
        right_layout.addWidget(linked_jobs_label)
        
        # Linked Jobs List
        # We need to aggregate jobs from items
        linked_jobs = set()
        if po.items:
            for item in po.items:
                if item.job_id:
                     # We might need to fetch the job details if not eager loaded, 
                     # but for now let's assume we can get basic info or just ID
                     # Ideally the relationship is set up. 
                     # If item.job is not available, we might just show IDs.
                     # Let's try to access item.job if available, else just ID
                     if hasattr(item, 'job') and item.job:
                         linked_jobs.add(f"{item.job.job_number} - {item.job.customer_name}")
                     else:
                         linked_jobs.add(f"Job #{item.job_id}")

        if linked_jobs:
            for job_str in list(linked_jobs)[:3]: # Show max 3
                job_lbl = QLabel(job_str)
                job_lbl.setStyleSheet("color: #546E7A; font-size: 10px;")
                job_lbl.setAlignment(Qt.AlignRight)
                right_layout.addWidget(job_lbl)
            
            if len(linked_jobs) > 3:
                more_lbl = QLabel(f"+ {len(linked_jobs) - 3} more")
                more_lbl.setStyleSheet("color: #7f8c8d; font-size: 10px; font-style: italic;")
                more_lbl.setAlignment(Qt.AlignRight)
                right_layout.addWidget(more_lbl)
        else:
            no_jobs = QLabel("Stock")
            no_jobs.setStyleSheet("color: #95a5a6; font-size: 10px; font-style: italic;")
            no_jobs.setAlignment(Qt.AlignRight)
            right_layout.addWidget(no_jobs)

        right_layout.addStretch()
        
        main_layout.addLayout(right_layout)
    
    def _on_view_clicked(self):
        self.clicked.emit(self.po)
    
    def _on_edit_clicked(self):
        self.edit_clicked.emit(self.po)
    
    def _on_print_clicked(self):
        self.print_clicked.emit(self.po)
    
    def _get_traffic_light_color(self):
        if self.po.status == POStatus.TO_ORDER:
            return "#3498db" # Blue
        elif self.po.status == POStatus.RECEIVED:
            return "#E67E22" # Orange
        elif self.po.status == POStatus.WAITING_STOCK:
            if self.po.due_date and self.po.due_date < date.today():
                return "#e74c3c" # Red - Overdue
            else:
                return "#2ecc71" # Green
        return "#95a5a6" # Grey default
