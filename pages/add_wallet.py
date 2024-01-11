import bittensor as bt
import os
import sys
from PyQt5.QtWidgets import (QPushButton, QLabel, QVBoxLayout,QWidget, QLineEdit, 
                             QMessageBox, QHBoxLayout, QFileDialog, QGroupBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class AddWalletPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.parent = parent

        self.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-family: Georgia;
            }
            #     QPushButton:hover {
            #         background-color: #005500;
            #     }
        """)

        # Header Group with links
        header_group = QGroupBox("BitCurrent", self)
        header_group.setFont(QFont("Georgia", 18, QFont.Bold))
        header_group.setAlignment(Qt.AlignLeft) 
        header_layout = QHBoxLayout(header_group)
        
        empty_label = QLabel("", self)
        empty_label.setFont(QFont("Georgia", 18))
        header_layout.addWidget(empty_label)
        header_group.setFixedHeight(50)   
        layout.addWidget(header_group)

        # Wallet Info       
        details_box = QGroupBox()
        details_layout = QVBoxLayout(details_box)
        label = QLabel("Wallet Details", self)
        label.setFont(QFont("Georgia", 26, QFont.Bold))
        details_layout.addWidget(label)


        # Wallet Name
        wallet_name_label = QLabel("Wallet Name:", self)
        wallet_name_label.setFont(QFont("Georgia", 16, QFont.Bold))
        details_layout.addWidget(wallet_name_label)
        self.wallet_name_input = QLineEdit(self)
        details_layout.addWidget(self.wallet_name_input)

        
        # Wallet Path
        wallet_path_label = QLabel("Wallet Path:", self)
        wallet_path_label.setFont(QFont("Georgia", 18))
        details_layout.addWidget(wallet_path_label)
        self.wallet_path_input = QLineEdit(self)
        self.wallet_path_input.setPlaceholderText("Select wallet path")
        self.wallet_path_input.setText(os.getcwd())
        details_layout.addWidget(self.wallet_path_input)
        browse_button = QPushButton("Browse", self)
        browse_button.setFont(QFont("Georgia", 16))
        browse_button.clicked.connect(self.browse_wallet_path)
        details_layout.addWidget(browse_button)
        details_box.setFixedHeight(200) 

        

        # Other Fields (Add as necessary)
        # Example: Wallet Password
        # wallet_password_label = QLabel("Wallet Password:", self)
        # wallet_password_label.setFont(QFont("Georgia", 18, QFont.Bold))
        # details_layout.addWidget(wallet_password_label)
        # self.wallet_password_input = QLineEdit(self)
        # self.wallet_password_input.setEchoMode(QLineEdit.Password)  # Hides text entry for password
        # details_layout.addWidget(self.wallet_password_input)

        layout.addWidget(details_box)

        h_layout = QHBoxLayout()
        previous_button = QPushButton("Back to Main Menu", self)
        previous_button.clicked.connect(parent.show_start_page)
        h_layout.addWidget(previous_button)
        
        # Save Button
        save_button = QPushButton("Save and Mine", self)
        save_button.clicked.connect(self.save_wallet_details)
        save_button.clicked.connect(self.parent.show_dashboard_page)#TODO move wallet details
        h_layout.addWidget(save_button)

        # Add more fields as needed...
        layout.addLayout(h_layout)

        self.setLayout(layout)

    def browse_wallet_path(self):
        # Open a QFileDialog to select the path
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.wallet_path = QFileDialog.getExistingDirectory(self, "Select Wallet Path", options=options)
        if self.wallet_path:
            self.wallet_path_input.setText(self.wallet_path)

    def save_wallet_details(self):
        # Logic to handle saving wallet details
        self.wallet_name = self.wallet_name_input.text()
        self.wallet_path = self.wallet_path_input.text()
        # self.wallet_password = self.wallet_password_input.text()

        wallet = bt.wallet(name=self.wallet_name, path=self.wallet_path)
        wallet.create_new_coldkey(use_password = False)
        wallet.create_new_hotkey(use_password=False)

        
        if self.wallet_name and self.wallet_path:
            self.parent.wallet_name = self.wallet_name
            self.parent.wallet_path = os.path.join(self.wallet_path, self.wallet_name) 
            ok = QMessageBox.information(self, "Save Wallet Details", "Wallet details saved successfully.")
        



