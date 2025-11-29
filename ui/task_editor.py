from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QLineEdit, QTextEdit, QComboBox, QPushButton, QLabel, QMessageBox,
                               QDateEdit)
from PySide6.QtCore import Qt, QDate
from ui.assets import play_sound
from database import get_db
from models import Task, TaskStatus, Priority

class TaskEditorDialog(QDialog):
    def __init__(self, parent=None, task=None):
        super().__init__(parent)
        self.task = task
        self.is_new = task is None
        
        self.setWindowTitle("New Task" if self.is_new else "Edit Task")
        self.setMinimumWidth(500)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Form
        form_layout = QFormLayout()
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Required")
        form_layout.addRow("Title:", self.title_input)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        self.description_input.setPlaceholderText("Task description or details...")
        form_layout.addRow("Description:", self.description_input)
        
        self.due_date_input = QDateEdit()
        self.due_date_input.setCalendarPopup(True)
        self.due_date_input.setDate(QDate.currentDate().addDays(7))
        form_layout.addRow("Due Date:", self.due_date_input)
        
        self.priority_input = QComboBox()
        self.priority_input.addItems([p.value for p in Priority])
        form_layout.addRow("Priority:", self.priority_input)
        
        self.status_input = QComboBox()
        self.status_input.addItems([s.value for s in TaskStatus])
        form_layout.addRow("Status:", self.status_input)
        
        self.assigned_to_input = QLineEdit()
        self.assigned_to_input.setPlaceholderText("Person responsible")
        form_layout.addRow("Assigned To:", self.assigned_to_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("Save Task")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.save_btn.clicked.connect(self.save_task)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        
        layout.addLayout(btn_layout)
        
        # Load existing data if editing
        if not self.is_new:
            self.load_task_data()
            
    def load_task_data(self):
        self.title_input.setText(self.task.title)
        self.description_input.setPlainText(self.task.description or "")
        if self.task.due_date:
            self.due_date_input.setDate(QDate(self.task.due_date))
        self.priority_input.setCurrentText(self.task.priority)
        self.status_input.setCurrentText(self.task.status)
        self.assigned_to_input.setText(self.task.assigned_to or "")
        
    def save_task(self):
        # Validate
        title = self.title_input.text().strip()
        if not title:
            play_sound("caution")
            QMessageBox.warning(self, "Validation Error", "Title is required.")
            return
            
        try:
            db = next(get_db())
            
            if self.is_new:
                # Generate Task Number
                last_task = db.query(Task).filter(Task.task_number.like("TN%")).order_by(Task.id.desc()).first()
                
                if last_task and last_task.task_number:
                    try:
                        last_num = int(last_task.task_number[2:])
                        new_num = last_num + 1
                    except ValueError:
                        new_num = 1
                else:
                    new_num = 1
                
                task_number = f"TN{new_num:06d}"

                task = Task(
                    task_number=task_number,
                    title=title,
                    description=self.description_input.toPlainText().strip() or None,
                    due_date=self.due_date_input.date().toPython(),
                    priority=self.priority_input.currentText(),
                    status=self.status_input.currentText(),
                    assigned_to=self.assigned_to_input.text().strip() or None
                )
                db.add(task)
            else:
                self.task.title = title
                self.task.description = self.description_input.toPlainText().strip() or None
                self.task.due_date = self.due_date_input.date().toPython()
                self.task.priority = self.priority_input.currentText()
                self.task.status = self.status_input.currentText()
                self.task.assigned_to = self.assigned_to_input.text().strip() or None
                
            db.commit()
            play_sound("celebration")
            self.accept()
            
        except Exception as e:
            play_sound("caution")
            QMessageBox.critical(self, "Error", f"Failed to save task:\n{str(e)}")
