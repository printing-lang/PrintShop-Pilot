from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                               QWidget)
from PySide6.QtCore import Qt, Signal, QSize
from ui.assets import get_icon
from models import Task, TaskStatus, Priority
from datetime import date

class TaskCardWidget(QFrame):
    clicked = Signal(object)
    edit_clicked = Signal(object)

    def __init__(self, task):
        super().__init__()
        self.task = task
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
        
        # Traffic light circle (based on due date)
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
        
        # Task Title
        title = QLabel(task.title)
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        title.setWordWrap(True)
        title.setMaximumHeight(40)
        left_layout.addWidget(title)
        
        # Description preview
        if task.description:
            desc = QLabel(task.description[:50] + "..." if len(task.description) > 50 else task.description)
            desc.setStyleSheet("color: #546E7A; font-size: 10px;")
            desc.setWordWrap(True)
            desc.setMaximumHeight(30)
            left_layout.addWidget(desc)
        
        left_layout.addStretch()
        
        # Due Date
        if task.due_date:
            date_text = task.due_date.strftime("%b %d, %Y")
            date_label = QLabel(f"DUE: {date_text}")
        else:
            date_label = QLabel("NO DUE DATE")
        date_label.setStyleSheet(f"color: {traffic_color}; font-size: 10px; font-weight: bold;")
        left_layout.addWidget(date_label)
        
        # Assigned To
        if task.assigned_to:
            assigned_label = QLabel(f"ASSIGNED: {task.assigned_to}")
            assigned_label.setStyleSheet("color: #546E7A; font-size: 10px;")
            left_layout.addWidget(assigned_label)
        
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
        
        left_layout.addLayout(buttons_row)
        
        main_layout.addLayout(left_layout)
        
        # RIGHT COLUMN
        right_layout = QVBoxLayout()
        right_layout.setSpacing(6)
        right_layout.setAlignment(Qt.AlignTop)
        
        # Priority badge
        priority_badge = QLabel(task.priority.upper())
        priority_bg, priority_text = self._get_priority_colors(task.priority)
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
        status_badge = QLabel(task.status.upper())
        status_bg, status_text = self._get_status_colors(task.status)
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
        self.clicked.emit(self.task)
    
    def _on_edit_clicked(self):
        self.edit_clicked.emit(self.task)
    
    def _get_traffic_light_color(self):
        """Get color for traffic light based on due date"""
        if not self.task.due_date:
            return "#3498db"  # Blue if no due date
        
        if self.task.status == TaskStatus.COMPLETED:
            return "#2ecc71"  # Green if completed
        
        today = date.today()
        due_date = self.task.due_date
        
        if due_date < today:
            return "#e74c3c"  # Red - Overdue
        elif due_date == today:
            return "#f39c12"  # Orange - Due Today
        else:
            return "#2ecc71"  # Green - On Time
    
    def _get_priority_colors(self, priority):
        """Get background and text colors for priority badge"""
        priority_lower = priority.lower()
        if "miracle" in priority_lower:
            return "#FF0000", "#FFFFFF"  # Bright Red
        elif "express" in priority_lower:
            return "#FF8C00", "#FFFFFF"  # Dark Orange
        else:  # Normal
            return "#00FF00", "#FFFFFF"  # Bright Green
    
    def _get_status_colors(self, status):
        """Get background and text colors for status badge"""
        status_lower = status.lower()
        if "to do" in status_lower or "todo" in status_lower:
            return "#95a5a6", "#FFFFFF"  # Grey
        elif "in progress" in status_lower:
            return "#3498db", "#FFFFFF"  # Blue
        elif "completed" in status_lower:
            return "#27ae60", "#FFFFFF"  # Green
        elif "cancelled" in status_lower:
            return "#e74c3c", "#FFFFFF"  # Red
        else:
            return "#95a5a6", "#FFFFFF"  # Default grey
