from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QFrame, QScrollArea)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QPixmap, QDesktopServices, QCursor
from ui.assets import get_icon

class AboutWidget(QWidget):
    def __init__(self):
        super().__init__()
        # Gradient background
        self.setStyleSheet("""
            QWidget { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ecf0f1, stop:1 #bdc3c7);
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area to handle overflow
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        # Container widget
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignCenter)
        container_layout.setContentsMargins(20, 20, 20, 20)
        
        # Main content frame
        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 16px;
                border: 2px solid #3498db;
            }
        """)
        content_frame.setFixedSize(650, 750)
        
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(40, 30, 40, 30)
        content_layout.setSpacing(15)
        
        # Logo with background
        logo_container = QFrame()
        logo_container.setFixedHeight(110)
        logo_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                border-radius: 12px;
                border: none;
            }
        """)
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(20, 20, 20, 20)
        
        logo_label = QLabel()
        logo_path = r"C:\Users\PC\Downloads\Antigravity\Assets\PrintShop Piolet\PrintShop Pilot LOGO Light.png"
        try:
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(400, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            logo_layout.addWidget(logo_label)
        except:
            app_title = QLabel("PrintShop Pilot")
            app_title.setStyleSheet("font-size: 36px; font-weight: bold; color: white;")
            app_title.setAlignment(Qt.AlignCenter)
            logo_layout.addWidget(app_title)
        
        content_layout.addWidget(logo_container)
        
        # Version badge
        version_badge = QLabel("🚀 Version Alpha")
        version_badge.setFixedHeight(40)
        version_badge.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: white;
                background-color: #e74c3c;
                padding: 8px 20px;
                border-radius: 20px;
                font-weight: bold;
                border: none;
            }
        """)
        version_badge.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(version_badge)
        
        # Tagline
        tagline = QLabel("✨ Streamlining Your Print Shop Operations ✨")
        tagline.setFixedHeight(30)
        tagline.setStyleSheet("""
            font-size: 14px;
            color: #7f8c8d;
            font-style: italic;
            font-weight: 500;
            background: transparent;
            border: none;
        """)
        tagline.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(tagline)
        
        # Created By section
        created_section = QFrame()
        created_section.setFixedHeight(90)
        created_section.setStyleSheet("""
            QFrame {
                background-color: #ecf0f1;
                border-radius: 10px;
                border: none;
            }
        """)
        created_layout = QVBoxLayout(created_section)
        created_layout.setContentsMargins(20, 15, 20, 15)
        created_layout.setSpacing(5)
        
        created_title = QLabel("👥 Created By")
        created_title.setStyleSheet("font-size: 14px; color: #7f8c8d; font-weight: bold;")
        created_title.setAlignment(Qt.AlignCenter)
        created_layout.addWidget(created_title)
        
        creators = QLabel("David and Fredrick Seth")
        creators.setStyleSheet("font-size: 18px; color: #2c3e50; font-weight: 700;")
        creators.setAlignment(Qt.AlignCenter)
        created_layout.addWidget(creators)
        
        content_layout.addWidget(created_section)
        
        # Built With section
        built_section = QFrame()
        built_section.setFixedHeight(90)
        built_section.setStyleSheet("""
            QFrame {
                background-color: #e8f4f8;
                border-radius: 10px;
                border: none;
            }
        """)
        built_layout = QVBoxLayout(built_section)
        built_layout.setContentsMargins(20, 15, 20, 15)
        built_layout.setSpacing(5)
        
        built_title = QLabel("⚡ Built With")
        built_title.setStyleSheet("font-size: 14px; color: #7f8c8d; font-weight: bold;")
        built_title.setAlignment(Qt.AlignCenter)
        built_layout.addWidget(built_title)
        
        built_text = QLabel("Google Antigravity")
        built_text.setStyleSheet("font-size: 18px; color: #3498db; font-weight: 700;")
        built_text.setAlignment(Qt.AlignCenter)
        built_layout.addWidget(built_text)
        
        content_layout.addWidget(built_section)
        
        # Contact title
        contact_title = QLabel("📞 Contact Information")
        contact_title.setFixedHeight(30)
        contact_title.setStyleSheet("font-size: 15px; color: #2c3e50; font-weight: bold; background: transparent; border: none;")
        contact_title.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(contact_title)
        
        # Website
        website_container = QFrame()
        website_container.setFixedHeight(50)
        website_container.setStyleSheet("""
            QFrame {
                background-color: #e8f4f8;
                border-radius: 8px;
                border: none;
            }
            QFrame:hover {
                background-color: #d4e9f2;
            }
        """)
        website_container.setCursor(Qt.PointingHandCursor)
        website_container.mousePressEvent = lambda e: QDesktopServices.openUrl(QUrl("https://printshoppilot.com"))
        
        website_layout = QHBoxLayout(website_container)
        website_layout.setContentsMargins(15, 10, 15, 10)
        
        website_icon = QLabel()
        website_icon.setPixmap(get_icon("fa5s.globe", color="#3498db").pixmap(20, 20))
        website_layout.addWidget(website_icon)
        
        website_text = QLabel("🌐 printshoppilot.com")
        website_text.setStyleSheet("font-size: 15px; color: #3498db; font-weight: 600;")
        website_layout.addWidget(website_text)
        
        website_layout.addStretch()
        
        website_status = QLabel("(Coming Soon)")
        website_status.setStyleSheet("font-size: 12px; color: #95a5a6; font-style: italic;")
        website_layout.addWidget(website_status)
        
        content_layout.addWidget(website_container)
        
        # Email
        email_container = QFrame()
        email_container.setFixedHeight(50)
        email_container.setStyleSheet("""
            QFrame {
                background-color: #fdeaea;
                border-radius: 8px;
                border: none;
            }
            QFrame:hover {
                background-color: #fbd5d5;
            }
        """)
        email_container.setCursor(Qt.PointingHandCursor)
        email_container.mousePressEvent = lambda e: QDesktopServices.openUrl(QUrl("mailto:admin@printshoppilot.com"))
        
        email_layout = QHBoxLayout(email_container)
        email_layout.setContentsMargins(15, 10, 15, 10)
        
        email_icon = QLabel()
        email_icon.setPixmap(get_icon("fa5s.envelope", color="#e74c3c").pixmap(20, 20))
        email_layout.addWidget(email_icon)
        
        email_text = QLabel("📧 admin@printshoppilot.com")
        email_text.setStyleSheet("font-size: 15px; color: #e74c3c; font-weight: 600;")
        email_layout.addWidget(email_text)
        
        email_layout.addStretch()
        
        email_status = QLabel("(Coming Soon)")
        email_status.setStyleSheet("font-size: 12px; color: #95a5a6; font-style: italic;")
        email_layout.addWidget(email_status)
        
        content_layout.addWidget(email_container)
        
        # Copyright
        copyright_label = QLabel("© 2025 PrintShop Pilot. All rights reserved.")
        copyright_label.setFixedHeight(25)
        copyright_label.setStyleSheet("font-size: 11px; color: #95a5a6; font-weight: 500; background: transparent; border: none;")
        copyright_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(copyright_label)
        
        # Add content frame to container
        container_layout.addWidget(content_frame)
        
        # Set container to scroll area
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
