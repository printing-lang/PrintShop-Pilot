from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QStackedWidget, QLabel, QFrame, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, QSize
from ui.dashboard_widget import DashboardWidget
from ui.jobs_widget import JobsWidget
from ui.quotes_widget import QuotesWidget
from ui.purchase_orders_widget import PurchaseOrdersWidget
from ui.tasks_widget import TasksWidget
from ui.customers_widget import CustomersWidget
from ui.suppliers_widget import SuppliersWidget
from ui.settings_widget import SettingsWidget
from ui.search_widget import SearchWidget
from ui.help_widget import HelpWidget
from ui.about_widget import AboutWidget
from ui.assets import get_icon, play_sound

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PrintShop Pilot")
        self.resize(1200, 800)
        
        # Main Layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(250)
        self.sidebar.setStyleSheet("background-color: #2c3e50; color: white;")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # App Title / Logo area
        title_container = QWidget()
        title_container.setFixedHeight(80)
        title_layout = QVBoxLayout(title_container)
        title_layout.setAlignment(Qt.AlignCenter)
        title_layout.setContentsMargins(10, 10, 10, 10)
        
        # Logo
        from PySide6.QtGui import QPixmap
        logo_label = QLabel()
        logo_path = r"C:\Users\PC\Downloads\Antigravity\Assets\PrintShop Piolet\PrintShop Pilot LOGO Light.png"
        pixmap = QPixmap(logo_path)
        # Scale the logo to fit nicely in the sidebar
        scaled_pixmap = pixmap.scaled(220, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(logo_label)
        sidebar_layout.addWidget(title_container)
        
        # Navigation Buttons
        self.nav_buttons = []
        
        # Define nav items: (Label, Icon Name, Widget Class)
        nav_items = [
            ("Overview", "fa5s.chart-line", DashboardWidget),
            ("Jobs", "apparel", JobsWidget),
            ("Quotes", "order_approve_inverted", QuotesWidget),
            ("Tasks", "pending_actions_inverted", TasksWidget),
            ("Purchase Orders", "add_business", PurchaseOrdersWidget),
            ("Customers", "account_circle_inverted", CustomersWidget),
            ("Suppliers", "fa5s.truck", SuppliersWidget),
            ("Search", "pageview", lambda: SearchWidget(mode="active")),
            ("Archive", "fa5s.archive", lambda: SearchWidget(mode="archive")),
            ("Settings", "fa5s.cog", SettingsWidget),
            ("Help", "contact_support", HelpWidget),
            ("About", "verified_inverted", AboutWidget),
        ]
        
        self.stack = QStackedWidget()
        
        self.widgets = {}
        
        for label, icon_name, widget_factory in nav_items:
            btn = QPushButton(f"  {label}")
            # Use our new asset helper
            btn.setIcon(get_icon(icon_name, color="white"))
            btn.setIconSize(QSize(20, 20))
            btn.setFixedHeight(50)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding-left: 20px;
                    border: none;
                    color: #ecf0f1;
                    font-size: 14px;
                    background-color: transparent;
                }
                QPushButton:hover {
                    background-color: #34495e;
                }
                QPushButton:checked {
                    background-color: #3498db;
                    border-left: 4px solid white;
                    font-weight: bold;
                }
            """)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, b=btn: self.handle_nav_click(b))
            
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)
            
            # Instantiate widget
            if widget_factory:
                # Check if it's a class or a lambda/function
                if isinstance(widget_factory, type):
                    widget_instance = widget_factory()
                else:
                    widget_instance = widget_factory()
                    
                self.stack.addWidget(widget_instance)
                self.widgets[label] = widget_instance
            else:
                self.stack.addWidget(QWidget()) # Empty placeholder
                
        sidebar_layout.addStretch()
        
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stack)
        
        # Connect Dashboard Signals
        if "Overview" in self.widgets:
            dashboard = self.widgets["Overview"]
            
            if "Jobs" in self.widgets:
                dashboard.new_job_signal.connect(self.widgets["Jobs"].open_new_job_dialog)
            
            if "Quotes" in self.widgets:
                dashboard.new_quote_signal.connect(self.widgets["Quotes"].open_new_quote_dialog)
                
            if "Tasks" in self.widgets:
                dashboard.new_task_signal.connect(self.widgets["Tasks"].open_new_task_dialog)
                
            if "Purchase Orders" in self.widgets:
                dashboard.new_po_signal.connect(self.widgets["Purchase Orders"].open_new_po_dialog)
                
            if "Customers" in self.widgets:
                dashboard.new_customer_signal.connect(self.widgets["Customers"].open_new_customer_dialog)
        
        # Connect Settings signal to dashboard
        if "Settings" in self.widgets and "Overview" in self.widgets:
            self.widgets["Settings"].settings_changed.connect(self.widgets["Overview"].refresh_welcome)
        
        # Set initial page (Dashboard)
        if self.nav_buttons:
            self.nav_buttons[0].click()

    def handle_nav_click(self, clicked_btn):
        # Play sound
        self.sound_effect = play_sound("select") # Keep ref to prevent GC
        
        # Uncheck all others
        for i, btn in enumerate(self.nav_buttons):
            if btn == clicked_btn:
                btn.setChecked(True)
                self.stack.setCurrentIndex(i)
            else:
                btn.setChecked(False)
