from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QPushButton)
from PySide6.QtCore import Qt, Signal, QSize
from database import get_db
from models import Job, Quote, PurchaseOrder, Task, QuoteStatus, POStatus, TaskStatus
from datetime import datetime
from ui.assets import get_icon
from settings_manager import get_settings

class StatCard(QFrame):
    def __init__(self, title, total_count, red_count, orange_count, green_count, blue_count, icon_name, border_color):
        super().__init__()
        self.setStyleSheet(f"""
            StatCard {{
                background-color: #C8E5EB;
                border-radius: 8px;
                border-left: 4px solid {border_color};
            }}
            QLabel {{
                background-color: transparent;
            }}
        """)
        self.setFixedSize(250, 170)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(15, 15, 15, 10)
        
        # Top row: Title and Icon
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        
        title_lbl = QLabel(title.upper())
        title_lbl.setStyleSheet("color: #546e7a; font-size: 11px; font-weight: bold;")
        
        icon_lbl = QLabel()
        icon_lbl.setPixmap(get_icon(icon_name, color="#546e7a").pixmap(24, 24))
        
        top_row.addWidget(title_lbl)
        top_row.addStretch()
        top_row.addWidget(icon_lbl)
        
        layout.addLayout(top_row)
        
        # Big number
        count_lbl = QLabel(str(total_count))
        count_lbl.setStyleSheet("color: #2c3e50; font-size: 42px; font-weight: bold;")
        layout.addWidget(count_lbl)
        
        layout.addSpacing(5)
        
        # Traffic lights row
        lights_row = QHBoxLayout()
        lights_row.setSpacing(12)
        lights_row.setContentsMargins(0, 0, 0, 0)
        
        if blue_count >= 0:
            # Show all 4 colors for POs
            lights_row.addWidget(self.create_dot_with_count("#e74c3c", red_count))
            lights_row.addWidget(self.create_dot_with_count("#f39c12", orange_count))
            lights_row.addWidget(self.create_dot_with_count("#27ae60", green_count))
            lights_row.addWidget(self.create_dot_with_count("#3498db", blue_count))
        else:
            # Standard 3 lights
            lights_row.addWidget(self.create_dot_with_count("#e74c3c", red_count))
            lights_row.addWidget(self.create_dot_with_count("#f39c12", orange_count))
            lights_row.addWidget(self.create_dot_with_count("#27ae60", green_count))
        
        lights_row.addStretch()
        layout.addLayout(lights_row)
        
        layout.addSpacing(3)
        
        # View All link
        view_all = QLabel("View All →")
        view_all.setStyleSheet(f"color: {border_color}; font-size: 11px; font-weight: bold;")
        view_all.setCursor(Qt.PointingHandCursor)
        layout.addWidget(view_all)
    
    def create_dot_with_count(self, color, count):
        widget = QWidget()
        container = QHBoxLayout(widget)
        container.setSpacing(5)
        container.setContentsMargins(0, 0, 0, 0)
        
        # Dot
        dot = QLabel()
        dot.setFixedSize(24, 24)
        dot.setStyleSheet(f"background-color: {color}; border-radius: 12px;")
        
        # Count
        count_lbl = QLabel(str(count))
        count_lbl.setStyleSheet("color: #2c3e50; font-size: 16px; font-weight: bold;")
        
        container.addWidget(dot)
        container.addWidget(count_lbl)
        
        return widget

class DashboardWidget(QWidget):
    # Signals for Quick Actions
    new_job_signal = Signal()
    new_quote_signal = Signal()
    new_task_signal = Signal()
    new_po_signal = Signal()
    new_customer_signal = Signal()

    def __init__(self):
        super().__init__()
        
        self.setStyleSheet("QWidget { background-color: #C8E5EB; }")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Overview Dashboard")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50; margin-bottom: 5px; background: transparent;")
        layout.addWidget(title)
        
        # Welcome Message
        settings = get_settings()
        org_name = settings.get_organization_name()
        self.welcome_label = QLabel(f"Welcome {org_name} to PrintShop Pilot")
        self.welcome_label.setStyleSheet("font-size: 36px; font-weight: bold; color: #34495e; margin: 10px 0; background: transparent;")
        layout.addWidget(self.welcome_label)
        
        # Subtitle
        subtitle = QLabel("🚦 Traffic Light Status System")
        subtitle.setStyleSheet("font-size: 13px; color: #7f8c8d; margin-bottom: 25px; background: transparent;")
        layout.addWidget(subtitle)
        
        # Cards Grid
        self.cards_layout = QGridLayout()
        self.cards_layout.setSpacing(20)
        self.cards_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        layout.addLayout(self.cards_layout)
        
        # ===== QUICK ACTIONS =====
        
        # Container
        qa_container = QWidget()
        qa_container.setStyleSheet("""
            QWidget {
                background-color: #C8E5EB;
                border-radius: 10px;
            }
        """)
        qa_layout = QVBoxLayout(qa_container)
        qa_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        qa_title = QLabel("Quick Actions")
        qa_title.setAlignment(Qt.AlignCenter)
        qa_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px; background: transparent;")
        qa_layout.addWidget(qa_title)
        
        # Buttons Row
        btns_layout = QHBoxLayout()
        btns_layout.setSpacing(15)
        btns_layout.setAlignment(Qt.AlignCenter)
        
        actions = [
            ("New Job", "apparel", self.new_job_signal),
            ("New Quote", "order_approve_inverted", self.new_quote_signal),
            ("New Task", "pending_actions_inverted", self.new_task_signal),
            ("Add PO", "add_business", self.new_po_signal),
            ("Add Customer", "account_circle_inverted", self.new_customer_signal)
        ]
        
        for label, icon, signal in actions:
            btn = QPushButton(f"  {label}")
            btn.setIcon(get_icon(icon, color="white"))
            btn.setIconSize(QSize(18, 18))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(45)
            btn.setMinimumWidth(140)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2c3e50;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 13px;
                    padding: 0 15px;
                }
                QPushButton:hover {
                    background-color: #34495e;
                }
                QPushButton:pressed {
                    background-color: #1abc9c;
                }
            """)
            btn.clicked.connect(signal.emit)
            btns_layout.addWidget(btn)
            
        qa_layout.addLayout(btns_layout)
        
        layout.addSpacing(20)
        layout.addWidget(qa_container)
        
        layout.addStretch()
        
        self.refresh_stats()
    
    def refresh_welcome(self):
        """Update welcome message with current organization name"""
        settings = get_settings()
        org_name = settings.get_organization_name()
        self.welcome_label.setText(f"Welcome {org_name} to PrintShop Pilot")

    def refresh_stats(self):
        # Clear existing
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        db = next(get_db())
        today = datetime.now().date()
        
        # ===== JOBS =====
        all_jobs = db.query(Job).filter(Job.is_archived == False).all()
        jobs_total = len(all_jobs)
        jobs_green = 0
        jobs_orange = 0
        jobs_red = 0
        
        for job in all_jobs:
            if job.due_date:
                days_until_due = (job.due_date - today).days
                if days_until_due < 0:
                    jobs_red += 1
                elif days_until_due <= 3:
                    jobs_orange += 1
                else:
                    jobs_green += 1
            else:
                jobs_green += 1
        
        self.cards_layout.addWidget(
            StatCard("Active Jobs", jobs_total, jobs_red, jobs_orange, jobs_green, -1, "apparel", "#3498db"),
            0, 0
        )
        
        # ===== QUOTES =====
        all_quotes = db.query(Quote).filter(Quote.is_archived == False).all()
        quotes_total = len(all_quotes)
        quotes_green = 0
        quotes_orange = 0
        quotes_red = 0
        
        for quote in all_quotes:
            if quote.status == QuoteStatus.ACCEPTED:
                quotes_green += 1
            elif quote.status == QuoteStatus.REJECTED:
                quotes_red += 1
            elif quote.expiry_date:
                days_until_expiry = (quote.expiry_date - today).days
                if days_until_expiry < 0:
                    quotes_red += 1
                elif days_until_expiry <= 7:
                    quotes_orange += 1
                else:
                    quotes_green += 1
            else:
                quotes_green += 1
        
        self.cards_layout.addWidget(
            StatCard("Pending Quotes", quotes_total, quotes_red, quotes_orange, quotes_green, -1, "order_approve", "#9b59b6"),
            0, 1
        )
        
        # ===== TASKS =====
        all_tasks = db.query(Task).filter(Task.is_archived == False).all()
        tasks_total = len(all_tasks)
        tasks_green = 0
        tasks_orange = 0
        tasks_red = 0
        
        for task in all_tasks:
            if task.status == TaskStatus.COMPLETED:
                tasks_green += 1
            elif task.due_date:
                days_until_due = (task.due_date - today).days
                if days_until_due < 0:
                    tasks_red += 1
                elif days_until_due <= 3:
                    tasks_orange += 1
                else:
                    tasks_green += 1
            else:
                tasks_green += 1
        
        self.cards_layout.addWidget(
            StatCard("Active Tasks", tasks_total, tasks_red, tasks_orange, tasks_green, -1, "pending_actions", "#27ae60"),
            0, 2
        )
        
        # ===== PURCHASE ORDERS =====
        all_pos = db.query(PurchaseOrder).filter(PurchaseOrder.is_archived == False).all()
        po_total = len(all_pos)
        po_blue = 0
        po_green = 0
        po_orange = 0
        po_red = 0
        
        for po in all_pos:
            if po.status == POStatus.TO_ORDER:
                po_blue += 1
            elif po.status == POStatus.RECEIVED:
                po_orange += 1
            elif po.status == POStatus.WAITING_STOCK:
                if po.due_date and po.due_date < today:
                    po_red += 1
                else:
                    po_green += 1
            else:
                po_green += 1
        
        self.cards_layout.addWidget(
            StatCard("Active PO's", po_total, po_red, po_orange, po_green, po_blue, "add_business", "#e67e22"),
            0, 3
        )
