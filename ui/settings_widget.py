from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QFormLayout, QGroupBox, QListWidget, QMessageBox, QScrollArea)
from PySide6.QtCore import Qt, Signal
from settings_manager import get_settings

class SettingsWidget(QWidget):
    settings_changed = Signal()
    
    def __init__(self):
        super().__init__()
        
        # Main layout with ScrollArea
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        content_widget = QWidget()
        content_widget.setStyleSheet("QWidget { background-color: transparent; }")
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        # Title with icon
        title_container = QHBoxLayout()
        title_icon = QLabel()
        from ui.assets import get_icon
        title_icon.setPixmap(get_icon("fa5s.cog", color="#2c3e50").pixmap(32, 32))
        title_container.addWidget(title_icon)
        
        title = QLabel("Settings")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-left: 8px;")
        title_container.addWidget(title)
        title_container.addStretch()
        layout.addLayout(title_container)
        
        layout.addSpacing(20)
        
        # Organization Settings Group
        org_group = QGroupBox("Organization")
        org_group.setStyleSheet(self.get_group_style())
        org_layout = QFormLayout(org_group)
        
        # Organization Name
        self.org_name_input = QLineEdit()
        self.org_name_input.setPlaceholderText("Your Organisation")
        self.org_name_input.setFixedWidth(400)
        self.org_name_input.setStyleSheet(self.get_input_style())
        
        org_layout.addRow("Organization Name:", self.org_name_input)
        
        layout.addWidget(org_group)
        
        # Shops Group
        shops_group = QGroupBox("Shops")
        shops_group.setStyleSheet(self.get_group_style())
        shops_layout = QVBoxLayout(shops_group)
        
        self.shops_list = QListWidget()
        self.shops_list.setMaximumHeight(100)
        shops_layout.addWidget(self.shops_list)
        
        shop_input_layout = QHBoxLayout()
        self.shop_input = QLineEdit()
        self.shop_input.setPlaceholderText("New Shop Name")
        self.shop_input.setStyleSheet(self.get_input_style())
        
        add_shop_btn = QPushButton("Add")
        add_shop_btn.setStyleSheet(self.get_button_style("#3498db"))
        add_shop_btn.clicked.connect(self.add_shop)
        
        remove_shop_btn = QPushButton("Remove Selected")
        remove_shop_btn.setStyleSheet(self.get_button_style("#e74c3c"))
        remove_shop_btn.clicked.connect(self.remove_shop)
        
        shop_input_layout.addWidget(self.shop_input)
        shop_input_layout.addWidget(add_shop_btn)
        shop_input_layout.addWidget(remove_shop_btn)
        shops_layout.addLayout(shop_input_layout)
        
        layout.addWidget(shops_group)

        # Personnel Group
        personnel_group = QGroupBox("Personnel")
        personnel_group.setStyleSheet(self.get_group_style())
        personnel_layout = QVBoxLayout(personnel_group)
        
        self.personnel_list = QListWidget()
        self.personnel_list.setMaximumHeight(100)
        personnel_layout.addWidget(self.personnel_list)
        
        personnel_input_layout = QHBoxLayout()
        self.personnel_input = QLineEdit()
        self.personnel_input.setPlaceholderText("New Staff Name")
        self.personnel_input.setStyleSheet(self.get_input_style())
        
        add_personnel_btn = QPushButton("Add")
        add_personnel_btn.setStyleSheet(self.get_button_style("#3498db"))
        add_personnel_btn.clicked.connect(self.add_personnel)
        
        remove_personnel_btn = QPushButton("Remove Selected")
        remove_personnel_btn.setStyleSheet(self.get_button_style("#e74c3c"))
        remove_personnel_btn.clicked.connect(self.remove_personnel)
        
        personnel_input_layout.addWidget(self.personnel_input)
        personnel_input_layout.addWidget(add_personnel_btn)
        personnel_input_layout.addWidget(remove_personnel_btn)
        personnel_layout.addLayout(personnel_input_layout)
        
        layout.addWidget(personnel_group)

        # Shipping Options Group
        shipping_group = QGroupBox("Shipping Options")
        shipping_group.setStyleSheet(self.get_group_style())
        shipping_layout = QVBoxLayout(shipping_group)
        
        self.shipping_list = QListWidget()
        self.shipping_list.setMaximumHeight(100)
        shipping_layout.addWidget(self.shipping_list)
        
        shipping_input_layout = QHBoxLayout()
        self.shipping_input = QLineEdit()
        self.shipping_input.setPlaceholderText("New Shipping Option")
        self.shipping_input.setStyleSheet(self.get_input_style())
        
        add_shipping_btn = QPushButton("Add")
        add_shipping_btn.setStyleSheet(self.get_button_style("#3498db"))
        add_shipping_btn.clicked.connect(self.add_shipping_option)
        
        remove_shipping_btn = QPushButton("Remove Selected")
        remove_shipping_btn.setStyleSheet(self.get_button_style("#e74c3c"))
        remove_shipping_btn.clicked.connect(self.remove_shipping_option)
        
        shipping_input_layout.addWidget(self.shipping_input)
        shipping_input_layout.addWidget(add_shipping_btn)
        shipping_input_layout.addWidget(remove_shipping_btn)
        shipping_layout.addLayout(shipping_input_layout)
        
        layout.addWidget(shipping_group)
        
        # Business Details Group
        business_group = QGroupBox("Business Details")
        business_group.setStyleSheet(self.get_group_style())
        business_layout = QFormLayout(business_group)
        
        # Tax Type
        self.tax_type_input = QLineEdit()
        self.tax_type_input.setPlaceholderText("ABN, VAT, GST, etc.")
        self.tax_type_input.setFixedWidth(200)
        self.tax_type_input.setStyleSheet(self.get_input_style())
        business_layout.addRow("Tax Type:", self.tax_type_input)
        
        # Tax Number
        self.tax_number_input = QLineEdit()
        self.tax_number_input.setPlaceholderText("12 345 678 901")
        self.tax_number_input.setFixedWidth(200)
        self.tax_number_input.setStyleSheet(self.get_input_style())
        business_layout.addRow("Tax Number:", self.tax_number_input)
        
        # Business Phone
        self.business_phone_input = QLineEdit()
        self.business_phone_input.setPlaceholderText("(02) 1234 5678")
        self.business_phone_input.setFixedWidth(200)
        self.business_phone_input.setStyleSheet(self.get_input_style())
        business_layout.addRow("Phone:", self.business_phone_input)
        
        # Business Email
        self.business_email_input = QLineEdit()
        self.business_email_input.setPlaceholderText("business@example.com")
        self.business_email_input.setFixedWidth(300)
        self.business_email_input.setStyleSheet(self.get_input_style())
        business_layout.addRow("Email:", self.business_email_input)
        
        # Business Address
        self.business_address_input = QLineEdit()
        self.business_address_input.setPlaceholderText("123 Main St, Suburb, State, Postcode")
        self.business_address_input.setFixedWidth(400)
        self.business_address_input.setStyleSheet(self.get_input_style())
        business_layout.addRow("Address:", self.business_address_input)
        
        layout.addWidget(business_group)
        
        # Account Types Group
        account_types_group = QGroupBox("Account Types")
        account_types_group.setStyleSheet(self.get_group_style())
        account_types_layout = QVBoxLayout(account_types_group)
        
        self.account_types_list = QListWidget()
        self.account_types_list.setMaximumHeight(100)
        account_types_layout.addWidget(self.account_types_list)
        
        account_types_input_layout = QHBoxLayout()
        self.account_types_input = QLineEdit()
        self.account_types_input.setPlaceholderText("New Account Type (e.g., 60 Days)")
        self.account_types_input.setStyleSheet(self.get_input_style())
        
        add_account_type_btn = QPushButton("Add")
        add_account_type_btn.setStyleSheet(self.get_button_style("#3498db"))
        add_account_type_btn.clicked.connect(self.add_account_type)
        
        remove_account_type_btn = QPushButton("Remove Selected")
        remove_account_type_btn.setStyleSheet(self.get_button_style("#e74c3c"))
        remove_account_type_btn.clicked.connect(self.remove_account_type)
        
        account_types_input_layout.addWidget(self.account_types_input)
        account_types_input_layout.addWidget(add_account_type_btn)
        account_types_input_layout.addWidget(remove_account_type_btn)
        account_types_layout.addLayout(account_types_input_layout)
        
        layout.addWidget(account_types_group)
        
        # Freight Methods Group
        freight_methods_group = QGroupBox("Freight Methods")
        freight_methods_group.setStyleSheet(self.get_group_style())
        freight_methods_layout = QVBoxLayout(freight_methods_group)
        
        self.freight_methods_list = QListWidget()
        self.freight_methods_list.setMaximumHeight(100)
        freight_methods_layout.addWidget(self.freight_methods_list)
        
        freight_methods_input_layout = QHBoxLayout()
        self.freight_methods_input = QLineEdit()
        self.freight_methods_input.setPlaceholderText("New Freight Method (e.g., Same Day)")
        self.freight_methods_input.setStyleSheet(self.get_input_style())
        
        add_freight_method_btn = QPushButton("Add")
        add_freight_method_btn.setStyleSheet(self.get_button_style("#3498db"))
        add_freight_method_btn.clicked.connect(self.add_freight_method)
        
        remove_freight_method_btn = QPushButton("Remove Selected")
        remove_freight_method_btn.setStyleSheet(self.get_button_style("#e74c3c"))
        remove_freight_method_btn.clicked.connect(self.remove_freight_method)
        
        freight_methods_input_layout.addWidget(self.freight_methods_input)
        freight_methods_input_layout.addWidget(add_freight_method_btn)
        freight_methods_input_layout.addWidget(remove_freight_method_btn)
        freight_methods_layout.addLayout(freight_methods_input_layout)
        
        layout.addWidget(freight_methods_group)
        
        layout.addSpacing(20)
        
        # Save Button
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save Settings")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        # Load current settings
        self.load_settings()
    
    def get_group_style(self):
        return """
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """

    def get_input_style(self):
        return """
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
            }
        """

    def get_button_style(self, color="#3498db"):
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 5px 15px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {color}DD;
            }}
            QPushButton:pressed {{
                background-color: {color}AA;
            }}
        """
    
    def load_settings(self):
        """Load settings from manager"""
        settings = get_settings()
        self.org_name_input.setText(settings.get_organization_name())
        
        self.shops_list.clear()
        self.shops_list.addItems(settings.get_shops())
        
        self.personnel_list.clear()
        self.personnel_list.addItems(settings.get_personnel())
        
        self.shipping_list.clear()
        self.shipping_list.addItems(settings.get_shipping_options())
        
        # Business Details
        self.tax_type_input.setText(settings.get_tax_type())
        self.tax_number_input.setText(settings.get_tax_number())
        self.business_phone_input.setText(settings.get_business_phone())
        self.business_email_input.setText(settings.get_business_email())
        self.business_address_input.setText(settings.get_business_address())
        
        # Account Types
        self.account_types_list.clear()
        self.account_types_list.addItems(settings.get_account_types())
        
        # Freight Methods
        self.freight_methods_list.clear()
        self.freight_methods_list.addItems(settings.get_freight_methods())
    
    def save_settings(self):
        """Save settings to manager"""
        settings = get_settings()
        settings.set_organization_name(self.org_name_input.text())
        
        # Business Details
        settings.set_tax_type(self.tax_type_input.text())
        settings.set_tax_number(self.tax_number_input.text())
        settings.set_business_phone(self.business_phone_input.text())
        settings.set_business_email(self.business_email_input.text())
        settings.set_business_address(self.business_address_input.text())
        
        # Emit signal to notify other widgets
        self.settings_changed.emit()
        
        QMessageBox.information(self, "Settings Saved", "Settings have been saved successfully!")

    def add_shop(self):
        name = self.shop_input.text().strip()
        if name:
            settings = get_settings()
            settings.add_shop(name)
            self.shop_input.clear()
            self.load_settings()
            self.settings_changed.emit()

    def remove_shop(self):
        current_item = self.shops_list.currentItem()
        if current_item:
            settings = get_settings()
            settings.remove_shop(current_item.text())
            self.load_settings()
            self.settings_changed.emit()

    def add_personnel(self):
        name = self.personnel_input.text().strip()
        if name:
            settings = get_settings()
            settings.add_personnel(name)
            self.personnel_input.clear()
            self.load_settings()
            self.settings_changed.emit()

    def remove_personnel(self):
        current_item = self.personnel_list.currentItem()
        if current_item:
            settings = get_settings()
            settings.remove_personnel(current_item.text())
            self.load_settings()
            self.settings_changed.emit()

    def add_shipping_option(self):
        name = self.shipping_input.text().strip()
        if name:
            settings = get_settings()
            settings.add_shipping_option(name)
            self.shipping_input.clear()
            self.load_settings()
            self.settings_changed.emit()

    def remove_shipping_option(self):
        current_item = self.shipping_list.currentItem()
        if current_item:
            settings = get_settings()
            settings.remove_shipping_option(current_item.text())
            self.load_settings()
            self.settings_changed.emit()

    def add_account_type(self):
        name = self.account_types_input.text().strip()
        if name:
            settings = get_settings()
            settings.add_account_type(name)
            self.account_types_input.clear()
            self.load_settings()
            self.settings_changed.emit()

    def remove_account_type(self):
        current_item = self.account_types_list.currentItem()
        if current_item:
            settings = get_settings()
            settings.remove_account_type(current_item.text())
            self.load_settings()
            self.settings_changed.emit()

    def add_freight_method(self):
        name = self.freight_methods_input.text().strip()
        if name:
            settings = get_settings()
            settings.add_freight_method(name)
            self.freight_methods_input.clear()
            self.load_settings()
            self.settings_changed.emit()

    def remove_freight_method(self):
        current_item = self.freight_methods_list.currentItem()
        if current_item:
            settings = get_settings()
            settings.remove_freight_method(current_item.text())
            self.load_settings()
            self.settings_changed.emit()
