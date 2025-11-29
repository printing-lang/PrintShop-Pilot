from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QScrollArea, QFrame, QTextBrowser)
from PySide6.QtCore import Qt
from ui.assets import get_icon

class HelpWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QWidget { background-color: #F0F0F0; }")
        
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Title with icon
        title_container = QHBoxLayout()
        title_icon = QLabel()
        title_icon.setPixmap(get_icon("contact_support", color="#2c3e50").pixmap(32, 32))
        title_container.addWidget(title_icon)
        
        title = QLabel("Help & Documentation")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50; background: transparent; margin-left: 8px;")
        title_container.addWidget(title)
        title_container.addStretch()
        
        header_layout.addLayout(title_container)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Scroll Area for Help Content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        # Content Widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Help Content using QTextBrowser for rich text
        help_browser = QTextBrowser()
        help_browser.setOpenExternalLinks(True)
        help_browser.setStyleSheet("""
            QTextBrowser {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                padding: 20px;
                font-size: 13px;
                line-height: 1.6;
            }
        """)
        
        help_content = """
        <style>
            h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
            h2 { color: #34495e; margin-top: 25px; }
            h3 { color: #7f8c8d; margin-top: 15px; }
            .section { margin-bottom: 30px; }
            .feature { background-color: #ecf0f1; padding: 10px; border-radius: 5px; margin: 10px 0; }
            .tip { background-color: #d5f4e6; padding: 10px; border-left: 4px solid #27ae60; margin: 10px 0; }
            .warning { background-color: #fadbd8; padding: 10px; border-left: 4px solid #e74c3c; margin: 10px 0; }
            kbd { background-color: #34495e; color: white; padding: 2px 6px; border-radius: 3px; font-family: monospace; }
            code { background-color: #ecf0f1; padding: 2px 4px; border-radius: 3px; font-family: monospace; }
        </style>
        
        <h1>📚 PrintShop Pilot User Guide</h1>
        
        <div class="section">
            <h2>🚀 Getting Started</h2>
            <p>Welcome to PrintShop Pilot! This application helps you manage your print shop operations including jobs, quotes, tasks, purchase orders, customers, and suppliers.</p>
            
            <div class="tip">
                <strong>💡 First Time Setup:</strong> Navigate to <strong>Settings</strong> to configure your organization name, business details, shops, personnel, and other preferences before creating your first job.
            </div>
        </div>
        
        <div class="section">
            <h2>📋 Core Features</h2>
            
            <h3>Overview Dashboard</h3>
            <div class="feature">
                <p>The <strong>Overview</strong> page provides a quick snapshot of your business:</p>
                <ul>
                    <li><strong>Traffic Lights:</strong> Visual indicators for job and PO statuses (Red = Overdue, Orange = Due Today, Green = On Time, Blue = Unassigned/To Order)</li>
                    <li><strong>Quick Actions:</strong> Rapidly create new jobs, quotes, tasks, purchase orders, and customers</li>
                    <li><strong>Recent Activity:</strong> View your most recent jobs and purchase orders</li>
                </ul>
            </div>
            
            <h3>Jobs Management</h3>
            <div class="feature">
                <p>Create and track print jobs from order to completion:</p>
                <ul>
                    <li><strong>Create Jobs:</strong> Click "New Job" to add a new print job</li>
                    <li><strong>Job Statuses:</strong> Job Created → Awaiting Stock → In Queue → Out Queue → Customer Notified → Complete</li>
                    <li><strong>Search:</strong> Use the search box to find jobs by job number, customer name, order type, or notes</li>
                    <li><strong>Print:</strong> Print individual job cards or the entire jobs page</li>
                    <li><strong>Archive:</strong> Completed jobs are automatically archived</li>
                </ul>
            </div>
            
            <h3>Quotes Management</h3>
            <div class="feature">
                <p>Manage customer quotes and convert them to jobs:</p>
                <ul>
                    <li><strong>Quote Statuses:</strong> Draft → Sent → Accepted/Rejected/Expired</li>
                    <li><strong>Search:</strong> Find quotes by quote number, customer name, or description</li>
                    <li><strong>Expiry Tracking:</strong> Monitor quote expiration dates</li>
                </ul>
            </div>
            
            <h3>Tasks Management</h3>
            <div class="feature">
                <p>Track internal tasks and assignments:</p>
                <ul>
                    <li><strong>Task Statuses:</strong> To Do → In Progress → Completed</li>
                    <li><strong>Due Date Tracking:</strong> Monitor overdue, due today, and upcoming tasks</li>
                    <li><strong>Search:</strong> Find tasks by title, description, or assigned person</li>
                </ul>
            </div>
            
            <h3>Purchase Orders</h3>
            <div class="feature">
                <p>Manage supplier purchase orders and link them to jobs:</p>
                <ul>
                    <li><strong>PO Statuses:</strong> To Order → Waiting Stock → Received</li>
                    <li><strong>Job Linking:</strong> Associate POs with multiple jobs</li>
                    <li><strong>Supplier Management:</strong> Track supplier details and order history</li>
                    <li><strong>Search:</strong> Find POs by PO number, supplier name, or description</li>
                </ul>
            </div>
            
            <h3>Customers & Suppliers</h3>
            <div class="feature">
                <p>Maintain your customer and supplier databases:</p>
                <ul>
                    <li><strong>Customer Statuses:</strong> Active, On Hold, Banned</li>
                    <li><strong>Contact Information:</strong> Store company names, contacts, emails, phones, and addresses</li>
                    <li><strong>Account Types:</strong> Assign payment terms (e.g., 30 Days, 60 Days, COD)</li>
                    <li><strong>Search:</strong> Quickly find customers or suppliers by any field</li>
                </ul>
            </div>
        </div>
        
        <div class="section">
            <h2>🔍 Search & Archive</h2>
            
            <h3>Search Functionality</h3>
            <p>Every management page includes a search box that filters results in real-time as you type. Search works across multiple fields relevant to each section.</p>
            
            <h3>Global Search</h3>
            <div class="feature">
                <p>The <strong>Search</strong> page allows you to search across all active items (jobs, quotes, tasks, POs, customers, suppliers) from one location.</p>
            </div>
            
            <h3>Archive</h3>
            <div class="feature">
                <p>The <strong>Archive</strong> page lets you search through all archived items. Completed jobs and other finished items are automatically moved here to keep your active views clean.</p>
            </div>
        </div>
        
        <div class="section">
            <h2>⚙️ Settings & Configuration</h2>
            
            <h3>Organization Settings</h3>
            <ul>
                <li><strong>Organization Name:</strong> Your business name (appears on the Overview page)</li>
                <li><strong>Business Details:</strong> Tax type, tax number, phone, email, and address</li>
            </ul>
            
            <h3>Custom Lists</h3>
            <p>Configure dropdown options used throughout the application:</p>
            <ul>
                <li><strong>Shops:</strong> Your different shop locations</li>
                <li><strong>Personnel:</strong> Staff members who can be assigned to jobs/tasks</li>
                <li><strong>Shipping Options:</strong> Available delivery methods</li>
                <li><strong>Account Types:</strong> Payment terms for customers (e.g., 30 Days, COD)</li>
                <li><strong>Freight Methods:</strong> Shipping carriers and methods for POs</li>
            </ul>
            
            <div class="tip">
                <strong>💡 Tip:</strong> Set up your custom lists in Settings before creating jobs to have all options readily available.
            </div>
        </div>
        
        <div class="section">
            <h2>🎨 Understanding Traffic Lights</h2>
            
            <h3>Jobs Traffic Lights</h3>
            <ul>
                <li><span style="color: #3498db;">🔵 <strong>Blue (Unassigned):</strong></span> Jobs in "Job Created" status</li>
                <li><span style="color: #e74c3c;">🔴 <strong>Red (Overdue):</strong></span> Jobs past their due date</li>
                <li><span style="color: #f39c12;">🟠 <strong>Orange (Due Today):</strong></span> Jobs due today</li>
                <li><span style="color: #2ecc71;">🟢 <strong>Green (On Time):</strong></span> Jobs with future due dates</li>
            </ul>
            
            <h3>Purchase Order Traffic Lights</h3>
            <ul>
                <li><span style="color: #3498db;">🔵 <strong>Blue (To Order):</strong></span> POs not yet ordered</li>
                <li><span style="color: #2ecc71;">🟢 <strong>Green (Waiting Stock):</strong></span> POs ordered, waiting for delivery</li>
                <li><span style="color: #E67E22;">🟠 <strong>Orange (Received):</strong></span> POs received and complete</li>
                <li><span style="color: #e74c3c;">🔴 <strong>Red (Overdue):</strong></span> POs past their order due date</li>
            </ul>
        </div>
        
        <div class="section">
            <h2>💡 Tips & Best Practices</h2>
            
            <div class="tip">
                <strong>📝 Use Production Notes:</strong> Add detailed production notes to jobs for your team. These notes are separate from customer-facing notes.
            </div>
            
            <div class="tip">
                <strong>🔗 Link POs to Jobs:</strong> When creating a purchase order, link it to relevant jobs so you can track which materials are for which orders.
            </div>
            
            <div class="tip">
                <strong>🎯 Set Priorities:</strong> Use job priorities (Low, Medium, High, Urgent) to help your team focus on critical work.
            </div>
            
            <div class="tip">
                <strong>📅 Monitor Due Dates:</strong> Regularly check the traffic light indicators on the Overview page to stay on top of deadlines.
            </div>
            
            <div class="tip">
                <strong>🔍 Use Search:</strong> Instead of scrolling through cards, use the search boxes to quickly find specific items.
            </div>
        </div>
        
        <div class="section">
            <h2>⚠️ Troubleshooting</h2>
            
            <h3>Common Issues</h3>
            
            <div class="warning">
                <strong>⚠️ Can't find a completed job?</strong><br>
                Completed jobs are automatically archived. Check the <strong>Archive</strong> page to find them.
            </div>
            
            <div class="warning">
                <strong>⚠️ Dropdown options missing?</strong><br>
                Go to <strong>Settings</strong> and add the required items to the appropriate lists (Shops, Personnel, Shipping Options, etc.).
            </div>
            
            <div class="warning">
                <strong>⚠️ Traffic lights not updating?</strong><br>
                The traffic lights update when you navigate to a page. Try clicking on the page again to refresh the data.
            </div>
        </div>
        
        <div class="section">
            <h2>📞 Support</h2>
            <p>For additional assistance or to report issues, please contact your system administrator or IT support team.</p>
        </div>
        
        <div class="section" style="text-align: center; color: #7f8c8d; margin-top: 40px;">
            <p><strong>PrintShop Pilot</strong> - Streamlining Your Print Shop Operations</p>
            <p style="font-size: 11px;">Version 1.0</p>
        </div>
        """
        
        help_browser.setHtml(help_content)
        content_layout.addWidget(help_browser)
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
