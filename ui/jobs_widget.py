from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QTableView, QHeaderView, QLabel, QAbstractItemView,
                               QScrollArea, QFrame, QButtonGroup, QGridLayout, QDialogButtonBox)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QSize
from PySide6.QtGui import QColor
import qtawesome as qta
from database import get_db
from models import Job, JobStatus
from datetime import date
from ui.assets import get_icon

class JobsTableModel(QAbstractTableModel):
    def __init__(self, jobs=None):
        super().__init__()
        self.jobs = jobs or []
        self.headers = ["Job #", "Customer", "Type", "Due Date", "Status", "Priority"]

    def rowCount(self, parent=QModelIndex()):
        return len(self.jobs)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        job = self.jobs[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            if col == 0: return job.job_number
            if col == 1: return job.customer_name
            if col == 2: return job.order_type
            if col == 3: return job.due_date.strftime("%Y-%m-%d") if job.due_date else ""
            if col == 4: return job.status
            if col == 5: return job.priority
        
        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

    def update_data(self, jobs):
        self.beginResetModel()
        self.jobs = jobs
        self.endResetModel()

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QTableView, QHeaderView, QLabel, QAbstractItemView, 
                               QScrollArea, QFrame, QButtonGroup, QLineEdit)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QSize
from PySide6.QtGui import QColor
import qtawesome as qta
from database import get_db
from models import Job
from ui.job_card import JobCardWidget

# ... (JobsTableModel remains the same, assuming it's above or imported)

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

    def add_cards(self, jobs, on_view, on_edit, on_print):
        self.clear()
        cols = 5 # Number of columns (5 cards wide)
        for i, job in enumerate(jobs):
            card = JobCardWidget(job)
            card.clicked.connect(on_view)
            card.edit_clicked.connect(on_edit)
            card.print_clicked.connect(on_print)
            row = i // cols
            col = i % cols
            self.grid.addWidget(card, row, col)

class JobsWidget(QWidget):
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
        title_icon.setPixmap(get_icon("apparel_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24").pixmap(32, 32))
        title_container.addWidget(title_icon)
        
        title = QLabel("Jobs Management")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50; background: transparent; margin-left: 8px;")
        title_container.addWidget(title)
        title_container.addStretch()
        
        left_column.addLayout(title_container)
        
        # 1. Traffic Light Overview
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

        # Blue - Unassigned (Created)
        self.unassigned_layout, self.unassigned_count = create_light("#3498db", "Unassigned")
        self.traffic_lights.addLayout(self.unassigned_layout)

        # Red - Over Due
        self.overdue_layout, self.overdue_count = create_light("#e74c3c", "Over Due")
        self.traffic_lights.addLayout(self.overdue_layout)

        # Orange - Due Today
        self.due_today_layout, self.due_today_count = create_light("#f39c12", "Due Today")
        self.traffic_lights.addLayout(self.due_today_layout)

        # Green - On Time
        self.on_time_layout, self.on_time_count = create_light("#2ecc71", "On Time")
        self.traffic_lights.addLayout(self.on_time_layout)

        left_column.addLayout(self.traffic_lights)

        # 2. Status Overview
        self.status_overview = QHBoxLayout()
        self.status_overview.setSpacing(15)
        self.status_overview.setAlignment(Qt.AlignLeft)

        def create_status_badge(color, label_text, text_color="#FFFFFF"):
            container = QHBoxLayout()
            container.setSpacing(5)
            
            # Badge (Label with background)
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

        # Job Created (Blue)
        self.status_created_layout, self.status_created_count = create_status_badge("#00BFFF", "Job Created")
        self.status_overview.addLayout(self.status_created_layout)

        # Awaiting Stock (Purple)
        self.status_stock_layout, self.status_stock_count = create_status_badge("#9C27B0", "Awaiting Stock")
        self.status_overview.addLayout(self.status_stock_layout)

        # In Queue (Green)
        self.status_in_queue_layout, self.status_in_queue_count = create_status_badge("#00FF00", "In Queue")
        self.status_overview.addLayout(self.status_in_queue_layout)

        # Out Queue (Yellow) - Black text
        self.status_out_queue_layout, self.status_out_queue_count = create_status_badge("#FFD700", "Out Queue", "#000000")
        self.status_overview.addLayout(self.status_out_queue_layout)

        # Customer Notified (Black)
        self.status_notified_layout, self.status_notified_count = create_status_badge("#000000", "Customer Notified")
        self.status_overview.addLayout(self.status_notified_layout)

        left_column.addLayout(self.status_overview)
        
        header_layout.addLayout(left_column)
        header_layout.addStretch()
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search jobs...")
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
        
        # New Job Button
        self.new_job_btn = QPushButton(" New Job")
        self.new_job_btn.setIcon(qta.icon("fa5s.plus", color="white"))
        self.new_job_btn.setIconSize(QSize(16, 16))
        self.new_job_btn.setCursor(Qt.PointingHandCursor)
        self.new_job_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #66BB6A;
            }
        """)
        header_layout.addWidget(self.new_job_btn)
        
        layout.addLayout(header_layout)
        
        # Stack for views
        self.content_stack = QWidget()
        self.stack_layout = QVBoxLayout(self.content_stack)
        self.stack_layout.setContentsMargins(0, 0, 0, 0)
        
        # Table View
        self.table = QTableView()
        self.model = JobsTableModel()
        self.table.setModel(self.model)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableView {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #ecf0f1;
                padding: 8px;
                border: none;
                font-weight: bold;
                color: #7f8c8d;
            }
        """)
        self.table.doubleClicked.connect(self.on_table_double_click)
        
        # Card View (Scroll Area)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        self.cards_container = FlowLayout()
        self.scroll_area.setWidget(self.cards_container)
        
        # Show card view by default
        self.table.hide()
        
        self.stack_layout.addWidget(self.table)
        self.stack_layout.addWidget(self.scroll_area)
        
        layout.addWidget(self.content_stack)
        
        self.new_job_btn.clicked.connect(self.open_new_job_dialog)
        self.print_btn.clicked.connect(self.print_jobs_page)
        
        self.refresh_data()

    def on_search(self, text):
        self.refresh_data(search=text)

    def open_new_job_dialog(self):
        from ui.job_editor import JobEditorDialog
        dialog = JobEditorDialog(self)
        if dialog.exec():
            self.refresh_data()

    def on_table_double_click(self, index):
        job = self.model.jobs[index.row()]
        self.edit_job(job)

    def edit_job(self, job):
        from ui.job_editor import JobEditorDialog
        dialog = JobEditorDialog(self, job)
        if dialog.exec():
            # Refresh the data to show updated job cards
            self.refresh_data()

    def refresh_data(self, search=""):
        db = next(get_db())
        try:
            query = db.query(Job).filter(Job.is_archived == False)
            
            if search:
                search_filter = f"%{search}%"
                query = query.filter(
                    (Job.job_number.like(search_filter)) |
                    (Job.customer_name.like(search_filter)) |
                    (Job.order_type.like(search_filter)) |
                    (Job.notes.like(search_filter))
                )
            
            jobs = query.all()
            
            # Sort jobs by due date (earliest first, None at the end)
            jobs_sorted = sorted(jobs, key=lambda j: (j.due_date is None, j.due_date))
            
            # Calculate counts
            today = date.today()
            overdue = 0
            due_today = 0
            on_time = 0
            unassigned = 0
            
            # Status counts
            status_counts = {
                JobStatus.CREATED: 0,
                JobStatus.AWAITING_STOCK: 0,
                JobStatus.IN_QUEUE: 0,
                JobStatus.OUT_QUEUE: 0,
                JobStatus.CUSTOMER_NOTIFIED: 0
            }
            
            for job in jobs:
                if job.status == JobStatus.COMPLETE:
                    continue
                
                if job.status == JobStatus.CREATED:
                    unassigned += 1
                
                # Count by status
                if job.status in status_counts:
                    status_counts[job.status] += 1
                
                if job.due_date:
                    if job.due_date < today:
                        overdue += 1
                    elif job.due_date == today:
                        due_today += 1
                    else:
                        on_time += 1
            
            # Update Traffic Light labels
            self.unassigned_count.setText(str(unassigned))
            self.overdue_count.setText(str(overdue))
            self.due_today_count.setText(str(due_today))
            self.on_time_count.setText(str(on_time))
            
            # Update Status Overview labels
            self.status_created_count.setText(str(status_counts[JobStatus.CREATED]))
            self.status_stock_count.setText(str(status_counts[JobStatus.AWAITING_STOCK]))
            self.status_in_queue_count.setText(str(status_counts[JobStatus.IN_QUEUE]))
            self.status_out_queue_count.setText(str(status_counts[JobStatus.OUT_QUEUE]))
            self.status_notified_count.setText(str(status_counts[JobStatus.CUSTOMER_NOTIFIED]))
            
            # Update Table
            self.model.update_data(jobs_sorted)
            
            # Update Cards
            self.cards_container.add_cards(jobs_sorted, self.view_job, self.edit_job, self.print_job)
        finally:
            db.close()
    
    def view_job(self, job):
        """View job in read-only mode"""
        from ui.job_editor import JobEditorDialog
        dialog = JobEditorDialog(self, job)
        # Make all fields read-only
        dialog.customer_name.setReadOnly(True)
        dialog.order_type.setEnabled(False)
        dialog.order_date.setEnabled(False)
        dialog.due_date.setEnabled(False)
        dialog.priority.setEnabled(False)
        dialog.status.setEnabled(False)
        dialog.contact_phone.setReadOnly(True)
        dialog.contact_email.setReadOnly(True)
        dialog.notes.setReadOnly(True)
        dialog.production_notes.setReadOnly(True)
        dialog.shipping.setEnabled(False)
        dialog.assigned_to.setEnabled(False)
        dialog.order_source.setEnabled(False)
        dialog.shop.setEnabled(False)
        dialog.created_by.setEnabled(False)
        
        dialog.buttons.button(QDialogButtonBox.Save).setEnabled(False)
        dialog.setWindowTitle(f"View Job - {job.job_number}")
        dialog.exec()
    
    def print_job(self, job):
        """Handle printing a single job card"""
        try:
            from PySide6.QtPrintSupport import QPrinter, QPrintDialog
            from PySide6.QtGui import QPainter, QFont, QPageLayout
            from PySide6.QtCore import QRect, QMarginsF
            from PySide6.QtWidgets import QMessageBox
            
            printer = QPrinter(QPrinter.HighResolution)
            # Set margins using QMarginsF
            margins = QMarginsF(15, 15, 15, 15)
            printer.setPageMargins(margins, QPageLayout.Millimeter)
            
            dialog = QPrintDialog(printer, self)
            if dialog.exec():
                painter = QPainter(printer)
                font = QFont("Arial", 12)
                painter.setFont(font)
                
                y = 100
                line_height = 50
                
                # Print job details
                painter.drawText(100, y, f"Job Number: {job.job_number}")
                y += line_height
                painter.drawText(100, y, f"Customer: {job.customer_name}")
                y += line_height
                painter.drawText(100, y, f"Order Type: {job.order_type}")
                y += line_height
                painter.drawText(100, y, f"Due Date: {job.due_date.strftime('%b %d, %Y') if job.due_date else 'N/A'}")
                y += line_height
                painter.drawText(100, y, f"Priority: {job.priority}")
                y += line_height
                painter.drawText(100, y, f"Status: {job.status}")
                y += line_height
                painter.drawText(100, y, f"Source: {job.order_source}")
                y += line_height
                
                if job.notes:
                    painter.drawText(100, y, f"Notes: {job.notes}")
                
                painter.end()
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Print Error", f"Error printing job: {str(e)}")
    
    def print_jobs_page(self):
        """Print the entire Jobs Management page in landscape"""
        from PySide6.QtPrintSupport import QPrinter, QPrintDialog
        from PySide6.QtGui import QPainter, QPageLayout, QPageSize
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
