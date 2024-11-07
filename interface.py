import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton,QMessageBox,QTextEdit,QSpinBox
)
from PyQt5.QtCore import Qt
from logic import BotWorker

class BotControlPanel(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.bot_worker = None  # Store the reference to the thread

    def initUI(self):
        self.setWindowTitle("Bot Control Panel")
        self.setMinimumSize(800, 800) # Set the window title and size

        # Main layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(20, 20, 20, 0)

        # Header
        header_layout = QHBoxLayout()
        logo = QLabel("🤖")  # Placeholder for SVG logo
        header_title = QLabel("Bot Control Panel")
        header_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #141414;")
        header_layout.addWidget(logo)
        header_layout.addWidget(header_title)
        header_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addLayout(header_layout)

        # Input fields
        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText("Enter email")
        self.email_input.setFixedHeight(40)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(40)
        #comments
        self.comment_input = QTextEdit(self)
        self.comment_input.setPlaceholderText("Enter comments for each post (Double Comma Separated)")
        self.comment_input.setFixedHeight(40) 
        #messages       
        self.message_input = QTextEdit(self)
        self.message_input.setPlaceholderText("Enter messages for each post (Double Comma Separated)")
        self.message_input.setFixedHeight(40)


        self.link_input = QTextEdit(self)
        self.link_input.setPlaceholderText("List of Post Links (Double Comma Separated)")
        self.link_input.setAlignment(Qt.AlignTop)
        self.link_input.setFixedHeight(100)

        # Add input fields to layout
        for input_widget in [self.email_input, self.password_input, self.comment_input,self.message_input, self.link_input]:
            layout.addWidget(input_widget)

        # Layout for buttons
        button_layout_1 = QHBoxLayout()
        button_layout_2 = QHBoxLayout()

        # Start button
        self.start_button = QPushButton("Start Bot", self)
        self.start_button.clicked.connect(self.run_bot)
        self.start_button.setFixedHeight(50)
        button_layout_1.addWidget(self.start_button)     

        # Delete cache
        self.delete_cache_button = QPushButton("Delete Memory Cache", self)
        self.delete_cache_button.clicked.connect(self.delete_cookies)
        self.delete_cache_button.setFixedHeight(50)
        button_layout_2.addWidget(self.delete_cache_button)

        # End application
        self.end_app_button = QPushButton("End Application", self)
        self.end_app_button.setFixedHeight(50)
        self.end_app_button.clicked.connect(self.end_application)
        button_layout_2.addWidget(self.end_app_button)

        # SpinBox for setting the time interval (in min)
        self.interval_spinbox = QSpinBox(self)
        self.interval_spinbox.setMinimum(1) # Minimum 1 min
        self.interval_spinbox.setFixedHeight(50)
        self.interval_spinbox.setMaximum(1440)  # Maximum 1 hour
        self.interval_spinbox.setSuffix(" Min")
        button_layout_2.addWidget(self.interval_spinbox)        


        # Toggle password visibility
        self.toggle_button = QPushButton("Show password", self)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setFixedHeight(50)
        self.toggle_button.clicked.connect(self.toggle_password_visibility)
        button_layout_1.addWidget(self.toggle_button)


        self.times_spinbox = QSpinBox(self)
        self.times_spinbox.setMinimum(1)
        self.times_spinbox.setFixedHeight(50)
        self.times_spinbox.setMaximum(60)
        self.times_spinbox.setSuffix(" Time")
        button_layout_1.addWidget(self.times_spinbox)

        layout.addLayout(button_layout_1)
        layout.addLayout(button_layout_2)
                
        # Status label
        self.status = QLabel("Bot Status: Ready", self)
        self.status.setStyleSheet("font-size: 20px")
        layout.addWidget(self.status)

        # Status log (Text area)
        self.status_log = QTextEdit(self)
        self.status_log.setStyleSheet("font-size: 15px")
        self.status_log.setReadOnly(True)  # Make the log read-only
        layout.addWidget(self.status_log)
        


        # Footer
        footer = QLabel("Copyright © 2023 Bot Control Panel")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #A0A0A0;")
        layout.addWidget(footer)

        # Set the main layout
        self.setLayout(layout)


    def run_bot(self):
        email = self.email_input.text()
        password = self.password_input.text()
        message = self.message_input.toPlainText().split(',,')
        posts = self.link_input.toPlainText().split(',,')
        comments = self.comment_input.toPlainText().split(',,')
        interval = self.interval_spinbox.value() * 60 
        times = self.times_spinbox.value()

        # Check if all required fields are filled
        if not email or not password or not posts or not comments :
            QMessageBox.warning(self, "Error", "All Fields are Required")
            return

        if len(posts) != len(comments):
            QMessageBox.warning(self, "Error", "The number of comments must match the number of posts")
            return

        # Check if the bot worker is already running
        if self.bot_worker is not None and self.bot_worker.isRunning():
            self.status.setText("Bot Status: Already running, waiting to finish...")
            return  # Wait for the current bot run to finish before starting again

        # Start a new bot worker
        self.bot_worker = BotWorker(email, password, posts, comments ,message, interval , times)
        self.bot_worker.isfinished.connect(self.on_bot_finished)
        self.bot_worker.error_signal.connect(self.on_error)
        self.bot_worker.status_signal.connect(self.update_status)
        self.status.setText(f"Bot will run every {self.interval_spinbox.value()} min.")
        self.status.setText("Bot Status: Running ...")
        self.bot_worker.start()


    def on_bot_finished(self):
        QMessageBox.information(self, "Bot", "Bot finished successfully!")
        self.status.setText("Bot Status: Stopped")


    def on_error(self, error_message):
        QMessageBox.critical(self, "Error", error_message)


    def delete_cookies(self):
        cookies_path = "cookies.pkl"
        if os.path.exists(cookies_path):
            os.remove(cookies_path)
            QMessageBox.information(self ,"Success", "Cookies file deleted successfully." )
        else:
            QMessageBox.information(self ,"Error" ,"Cookies file not found." )

    def end_application(self):
        if self.bot_worker and self.bot_worker.isRunning():
            self.status.setText("Stopping the bot...")
            self.bot_worker.stop()
            self.bot_worker.wait(msecs=60000)  # Ensure the thread is fully stopped before quittin
        QApplication.quit()


    def update_status(self, message):
        self.status_log.append(message)


    def toggle_password_visibility(self):
        # Check the button's state (pressed or not) to show/hide password
        if self.toggle_button.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)  # Show password
            self.toggle_button.setText("Hide Password")  # Change icon or text on the button
        else:
            self.password_input.setEchoMode(QLineEdit.Password)  # Hide password
            self.toggle_button.setText("Show Password")
