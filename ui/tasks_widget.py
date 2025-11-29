from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QScrollArea, QFrame, QGridLayout, QMessageBox, QLineEdit)
from PySide6.QtCore import Qt, QSize
from ui.assets import get_icon, play_sound
from database import get_db
from models import Task, TaskStatus
from ui.task_card import TaskCardWidget
from datetime import date

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

    def add_cards(self, tasks, on_view, on_edit):
        self.clear()
        cols = 5
        for i, task in enumerate(tasks):
            card = TaskCardWidget(task)
            card.clicked.connect(on_view)
            card.edit_clicked.connect(on_edit)
            row = i // cols
            col = i % cols
            self.grid.addWidget(card, row, col)

class TasksWidget(QWidget):
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
        title_icon.setPixmap(get_icon("pending_actions").pixmap(32, 32))
        title_container.addWidget(title_icon)
        
        title = QLabel("Tasks Management")
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

        self.overdue_layout, self.overdue_count = create_light("#e74c3c", "Overdue")
        self.traffic_lights.addLayout(self.overdue_layout)
        
        self.due_today_layout, self.due_today_count = create_light("#f39c12", "Due Today")
        self.traffic_lights.addLayout(self.due_today_layout)
        
        self.on_time_layout, self.on_time_count = create_light("#2ecc71", "On Time")
        self.traffic_lights.addLayout(self.on_time_layout)

        left_column.addLayout(self.traffic_lights)
        
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

        self.status_todo_layout, self.status_todo_count = create_status_badge("#95a5a6", "To Do")
        self.status_overview.addLayout(self.status_todo_layout)

        self.status_progress_layout, self.status_progress_count = create_status_badge("#3498db", "In Progress")
        self.status_overview.addLayout(self.status_progress_layout)

        self.status_completed_layout, self.status_completed_count = create_status_badge("#27ae60", "Completed")
        self.status_overview.addLayout(self.status_completed_layout)

        left_column.addLayout(self.status_overview)
        
        header_layout.addLayout(left_column)
        header_layout.addStretch()
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search tasks...")
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
            QPushButton { background-color: #2c3e50; border-radius: 4px; }
            QPushButton:hover { background-color: #34495e; }
        """)
        header_layout.addWidget(self.print_btn)
        header_layout.addSpacing(10)
        
        # New Task Button
        self.new_task_btn = QPushButton(" New Task")
        self.new_task_btn.setIcon(get_icon("fa5s.plus", color="white"))
        self.new_task_btn.setIconSize(QSize(16, 16))
        self.new_task_btn.setCursor(Qt.PointingHandCursor)
        self.new_task_btn.setStyleSheet("""
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
        header_layout.addWidget(self.new_task_btn)
        
        layout.addLayout(header_layout)
        
        # Card View
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        self.cards_container = FlowLayout()
        self.scroll_area.setWidget(self.cards_container)
        layout.addWidget(self.scroll_area)
        
        self.new_task_btn.clicked.connect(self.open_new_task_dialog)
        self.print_btn.clicked.connect(self.print_tasks_page)
        self.refresh_data()

    def on_search(self, text):
        self.refresh_data(search=text)

    def open_new_task_dialog(self):
        from ui.task_editor import TaskEditorDialog
        dialog = TaskEditorDialog(self)
        if dialog.exec():
            self.refresh_data()

    def edit_task(self, task):
        from ui.task_editor import TaskEditorDialog
        dialog = TaskEditorDialog(self, task)
        if dialog.exec():
            self.refresh_data()
            
    def view_task(self, task):
        self.edit_task(task)

    def refresh_data(self, search=""):
        db = next(get_db())
        try:
            query = db.query(Task).filter(Task.is_archived == False)
            
            if search:
                search_filter = f"%{search}%"
                query = query.filter(
                    (Task.title.like(search_filter)) |
                    (Task.description.like(search_filter)) |
                    (Task.assigned_to.like(search_filter))
                )
            
            tasks = query.order_by(Task.due_date).all()
            
            # Calculate counts
            today = date.today()
            overdue = 0
            due_today = 0
            on_time = 0
            
            status_counts = {
                TaskStatus.TODO: 0,
                TaskStatus.IN_PROGRESS: 0,
                TaskStatus.COMPLETED: 0
            }
            
            for task in tasks:
                if task.status in status_counts:
                    status_counts[task.status] += 1
                
                if task.due_date and task.status != TaskStatus.COMPLETED:
                    if task.due_date < today:
                        overdue += 1
                    elif task.due_date == today:
                        due_today += 1
                    else:
                        on_time += 1
            
            self.overdue_count.setText(str(overdue))
            self.due_today_count.setText(str(due_today))
            self.on_time_count.setText(str(on_time))
            
            self.status_todo_count.setText(str(status_counts[TaskStatus.TODO]))
            self.status_progress_count.setText(str(status_counts[TaskStatus.IN_PROGRESS]))
            self.status_completed_count.setText(str(status_counts[TaskStatus.COMPLETED]))
            
            self.cards_container.add_cards(tasks, self.view_task, self.edit_task)
            
        finally:
            db.close()
            
    def print_tasks_page(self):
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
            scale = min(page_rect.width() / widget_rect.width(), page_rect.height() / widget_rect.height())
            painter.scale(scale, scale)
            widget_to_print.render(painter)
            painter.end()
