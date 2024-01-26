# Plug and Play miner
# Kofi Osei - Bonsu 
# 30/12/2023 


import os
import sys
import json

import bittensor as bt
from config import search_directory

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout,
    QWidget, QLineEdit, QTextEdit, QMessageBox, QStackedWidget, QHBoxLayout, QFileDialog, 
    QGroupBox, QInputDialog, QSpacerItem, QSizePolicy
)

from PyQt5.QtGui import QPixmap, QFont, QPalette, QBrush, QColor, QFontDatabase, QDesktopServices
from PyQt5.QtCore import Qt, QUrl

from pages.startpage import StartPage
from pages.add_wallet import AddWalletPage
from pages.dashboard import SelectDashboardPage
from pages.wallet import WalletDetailsTable


class MiningWizard(QMainWindow):
    def __init__(self):
        super().__init__()
        ##
        self.subtensor = bt.subtensor(network = 'test')
        self.subnet = self.subtensor.metagraph(netuid = 25) #bt.metagraph(netuid = 25)
        
        # self.neuron = None
        
        self.setWindowTitle("Plug and play miner")
        self.setGeometry(100, 100, 800, 600)
       
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        
        # Initialize pages
        self.start_page = StartPage(self)
        
        # Adding pages to the stack
        self.central_widget.addWidget(self.start_page)

        # initialise vars
        self.wallet_name = None
        self.wallet_path = None

    # functions to open pages
    def show_start_page(self):
        self.central_widget.setCurrentWidget(self.start_page)

    def show_create_wallet_page(self):
        self.create_wallet_page = AddWalletPage(self)
        self.central_widget.addWidget(self.create_wallet_page)
        self.central_widget.setCurrentWidget(self.create_wallet_page)


    def show_dashboard_page(self):
        if self.wallet_name is not None:
            self.dashboard_page = SelectDashboardPage(self)
            self.central_widget.addWidget(self.dashboard_page)
            self.central_widget.setCurrentWidget(self.dashboard_page)
        else:
            self.wallet_name, ok = QInputDialog.getText(self, "Wallet Name", "Please confirm wallet name:")
            while True:
                if not ok:
                    break  # Break out of the loop if the user cancels
                try:
                    self.wallet_path = search_directory(os.path.expanduser('~'), self.wallet_name)
                    # print(self.wallet_path)
                    if self.wallet_path:
                        self.dashboard_page = SelectDashboardPage(self)
                        self.central_widget.addWidget(self.dashboard_page)
                        self.central_widget.setCurrentWidget(self.dashboard_page)
                        break  # Break out of the loop if the directory is found
                except FileNotFoundError as e:
                    new_directory, ok = QInputDialog.getText(self, "Wallet not found", str(e) + "\nEnter a valid wallet name:")
                    if not ok:
                        # print("User canceled")
                        break  # Break out of the loop if the user cancels
                    self.wallet_name = new_directory  # Update the wallet name for the next iteration
    
    def show_dashboard_page_from_mining(self, wallet_name):
            self.wallet_name = wallet_name
            self.wallet_path = search_directory(os.path.expanduser('~'), self.wallet_name)
            if self.wallet_path:
                self.dashboard_page = SelectDashboardPage(self)
                self.central_widget.addWidget(self.dashboard_page)
                self.central_widget.setCurrentWidget(self.dashboard_page)
   
    def show_wallet_page(self):
        if self.wallet_name != None:
            self.wallet_page = WalletDetailsTable(self)
            self.central_widget.addWidget(self.wallet_page)
            self.central_widget.setCurrentWidget(self.wallet_page)
        else:
            self.wallet_name, ok = QInputDialog.getText(self, "Wallet Name", "Plese confirm wallet name:")
            if ok and self.wallet_name:
                self.wallet_page = WalletDetailsTable(self)
                self.central_widget.addWidget(self.wallet_page)
                self.central_widget.setCurrentWidget(self.wallet_page)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("QMainWindow::separator { background: rgba(0, 0, 0, 0.3); width: 1px; }")
    window = MiningWizard()
    window.show()
    sys.exit(app.exec_())
