import os
import re
import json
import requests
import pandas as pd

from config import configure_logger, get_earnings_by_date_range
import bittensor as bt



from PyQt5.QtWidgets import QPushButton, QVBoxLayout,QHBoxLayout, QWidget, QLabel, QPushButton, QGroupBox,QMessageBox
from PyQt5.QtGui import QFont, QDesktopServices
from PyQt5.QtCore import Qt,QUrl, QProcess, QProcessEnvironment, QTimer, QDateTime
import pyqtgraph as pg
import matplotlib.dates as mdates




class SelectDashboardPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.data_logger = configure_logger(f"./{self.parent.wallet_name}/full_user_data.log")
       
       # Connect to taostats
        url = "https://taostats.io/data.json"
        response = requests.get(url)
        taostats = json.loads(response.content)
        price = float(taostats[0]['price'])  
        
        # data for charts
        reward_data = get_earnings_by_date_range(f"./{self.parent.wallet_name}/full_user_data.log")
        print(len(mdates.date2num(reward_data['date'].tolist()).tolist()))
        print(len(reward_data.balance.tolist()))

        with open(f'{os.path.join(self.parent.wallet_path)}/coldkey', 'r') as f:
            address_json = json.load(f)
        coldkey = address_json['ss58Address']

        if coldkey in self.parent.subnet.coldkeys:
            uid = self.parent.subnet.coldkeys.index(coldkey)
            self.wallet_bal_tao = self.parent.subnet.stake.tolist()[uid]
        else:
            self.wallet_bal_tao = 0

        self.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-family: Georgia;
            }
        """)
    
        layout = QVBoxLayout()
        # Header Group with links
        header_group = QGroupBox("BitCurrent")
        header_group.setFont(QFont("Georgia", 18, QFont.Bold))
        header_group.setAlignment(Qt.AlignLeft) 
        header_layout = QHBoxLayout(header_group)


        # header_layout.addWidget(QLabel("BITCURRENT"))
        home_button = QPushButton("Home")
        home_button.clicked.connect(self.parent.show_start_page)
        header_layout.addWidget(home_button)

        wallet_button = QPushButton("Wallet")
        wallet_button.clicked.connect(self.parent.show_wallet_page)
        header_layout.addWidget(wallet_button)


        self.mine_button = QPushButton("Start Mining")
        self.mine_button.clicked.connect(self.toggle_mining)
        header_layout.addWidget(self.mine_button)

        log_button = QPushButton("Log Out")
        header_layout.addWidget(log_button)

        layout.addWidget(header_group)
            
        # Summary Stats
        summary_group = QGroupBox(f'Welcome {self.parent.wallet_name}!!')
        summary_group.setFont(QFont("Georgia", 26, QFont.Bold, italic=True))
        summary_group.setAlignment(Qt.AlignLeft) 
        summary_layout = QHBoxLayout(summary_group)

  
        wallet_bal_dol = round(self.wallet_bal_tao * price, 2)
        earnings_group = QGroupBox()
        earnings_layout = QVBoxLayout(earnings_group)
        earnings_layout.addWidget(QLabel("Wallet Balance",font=QFont('Georgia', 10)))
        earnings_layout.addWidget(QLabel(f"${wallet_bal_dol}", font= QFont('Georgia', 20, QFont.Bold)))
        earnings_layout.addWidget(QLabel(f"TAO {self.wallet_bal_tao}", font= QFont('Georgia', 10)))
        
        summary_layout.addWidget(earnings_group)
       

        # Mining infomation
        mining_info_group = QGroupBox()
        mining_info_layout = QVBoxLayout(mining_info_group)
        mining_info_layout.addWidget(QLabel("Average Mining Time", font=QFont('Georgia', 10)))
        mining_info_layout.addWidget(QLabel("23.5HRS", font= QFont('Georgia', 20, QFont.Bold)))
        mining_info_layout.addWidget(QLabel(" ", font= QFont('Georgia', 10)))
        
        summary_layout.addWidget(mining_info_group)
        # layout.addWidget(summary_group)

        # CPU USAGE
        cpu_info_group = QGroupBox()
        cpu_info_layout = QVBoxLayout(cpu_info_group)
        cpu_info_layout.addWidget(QLabel("CPU Usage", font=QFont('Georgia', 10)))
        cpu_info_layout.addWidget(QLabel("12.3%", font= QFont('Georgia', 20, QFont.Bold)))
        cpu_info_layout.addWidget(QLabel(" ", font= QFont('Georgia', 10)))
        
        summary_layout.addWidget(cpu_info_group)


        # GPU USAGE
        gpu_info_group = QGroupBox()
        gpu_info_layout = QVBoxLayout(gpu_info_group)
        gpu_info_layout.addWidget(QLabel("GPU Usage", font=QFont('Georgia', 10)))
        gpu_info_layout.addWidget(QLabel("54.3%", font= QFont('Georgia', 20, QFont.Bold)))
        gpu_info_layout.addWidget(QLabel(" ", font= QFont('Georgia', 10)))
        summary_layout.addWidget(gpu_info_group)
        

        # Timer
        self.timer = QTimer(self) # Create timer 
        timer_group = QGroupBox()
        timer_info_layout = QVBoxLayout(timer_group)
        timer_info_layout.addWidget(QLabel("Live Mining Time", font=QFont('Georgia', 10)))
        self.timer_label = QLabel("0h: 0m: 0s", self)
        self.timer_label.setFont(QFont("Georgia", 20, QFont.Bold)) 
        timer_info_layout.addWidget(self.timer_label)
        timer_info_layout.addWidget(QLabel(" ", font= QFont('Georgia', 10)))
        
        # Define Mining/Live time
        self.mining_process = None
        self.start_time = QDateTime.currentDateTime()
        self.timer.timeout.connect(self.update_timer)
        summary_layout.addWidget(timer_group)
        layout.addWidget(summary_group)

        # User Activity Chart
        activity_plot = pg.PlotWidget()
        activity_plot.setBackground((50, 50, 50))
        activity_plot.getPlotItem().getAxis('left').setPen((200, 200, 200))
        activity_plot.getPlotItem().getAxis('bottom').setPen((200, 200, 200))
        activity_plot.getPlotItem().getAxis('left').setTextPen((200, 200, 200))
        activity_plot.getPlotItem().getAxis('bottom').setTextPen((200, 200, 200))
        activity_plot.showGrid(x=True, y=True, alpha=0.5)
        num_dates = mdates.date2num(reward_data['date'].tolist()).tolist()
        activity_plot.plot(num_dates, reward_data['balance'].tolist(), pen='g', symbol='o', symbolPen='g', symbolBrush=(50, 205, 50), symbolSize=10)
        activity_plot.getAxis('bottom').setTicks([[(num_dates[i], reward_data['date'].tolist()[i].strftime('%Y-%m-%d')) for i in range(len(reward_data['date'].tolist()))]])

        # Reward History Chart
        reward_plot = pg.PlotWidget()
        reward_plot.setBackground((50, 50, 50))
        reward_plot.getPlotItem().getAxis('left').setPen((200, 200, 200))
        reward_plot.getPlotItem().getAxis('bottom').setPen((200, 200, 200))
        reward_plot.getPlotItem().getAxis('left').setTextPen((200, 200, 200))
        reward_plot.getPlotItem().getAxis('bottom').setTextPen((200, 200, 200))
        reward_plot.showGrid(x=True, y=True, alpha=0.5)
        reward_plot.plot([0, 1, 2, 3,5], [0, 5, 3, 8, 2], pen='r', symbol='o', symbolPen='r', symbolBrush=(255, 0, 0), symbolSize=10)

        # Charts Section
        charts_group = QGroupBox("Charts")
        charts_group.setStyleSheet("QGroupBox { font-size: 18px; color: #ffffff; border: 2px solid #3498db; border-radius: 5px; margin-top: 10px;}")
        charts_layout = QVBoxLayout(charts_group)
        charts_layout.addWidget(QLabel("User Activity Chart", font=QFont('Georgia', 14, QFont.Bold)))
        charts_layout.addWidget(activity_plot)
        charts_layout.addWidget(QLabel("Reward History Chart", font=QFont('Georgia', 14, QFont.Bold)))
        charts_layout.addWidget(reward_plot)
        layout.addWidget(charts_group)

        self.setLayout(layout)
    
    # **********
    # Functions
    # ********** 
    def toggle_mining(self):
        if self.mining_process is None or self.mining_process.state() == QProcess.NotRunning:
            self.start_mining()
        else:
            self.stop_mining()

    def start_mining(self):
        # Run script with QProcess

        script_path = '/Users/beekin/projects/btt-plug-n-play/gpu_cpu.py' # Replace with the actual path
        self.mining_process = QProcess(self)
        self.mining_process.setProcessChannelMode(QProcess.MergedChannels)
        self.mining_process.readyReadStandardOutput.connect(self.handle_output)
        self.data_logger.info(f' Activity: Start Mining')
        # Set environment variables if needed
        env = QProcessEnvironment.systemEnvironment()
        # env.insert("KEY", "VALUE")
        self.mining_process.setProcessEnvironment(env)

        self.start_time = QDateTime.currentDateTime()
        self.timer.start(1000)  # Update timer every second
        # self.timer = QTimer(self) # Create timer 
        self.timer.timeout.connect(self.update_timer)
       
        # log balance and start of mining
        self.data_logger.info(f' Balance - Start: {self.wallet_bal_tao}')
        self.mining_process.start("python", [script_path])
        self.mining_process.finished.connect(self.stop_mining)
        self.mine_button.setText("Stop Mining")
        

    def stop_mining(self):
        if self.mining_process is not None and self.mining_process.state() == QProcess.Running:
            self.mining_process.terminate()
            self.timer.stop() 
            self.mining_process.waitForFinished()
            self.mining_process = None
            self.mine_button.setText("Start Mining")

    def handle_output(self):
        # Handle output from the mining script if needed
        self.stop_timer()
        output = self.mining_process.readAllStandardOutput().data().decode("utf-8")
        self.data_logger.info(f' Balance - Stop: {self.wallet_bal_tao}') 
        self.data_logger.info(f' Activity: Stop Mining') 
        self.mine_button.setText("Start Mining")

        cpu_usage_match = re.search(r'CPU Usage: ([\d.]+)%', output)
        # time_taken_cpu_match = re.search(r'Time taken on CPU: ([\d.]+) seconds', output)
        if cpu_usage_match: # and time_taken_cpu_match:
            cpu_usage = float(cpu_usage_match.group(1))
            self.data_logger.info(f' Activity - CPU Usage%: {cpu_usage}')
            # time_taken_cpu = float(time_taken_cpu_match.group(1))     
        print(output)
    
    def start_timer(self):
        # Start the timer with a 1-second interval
        self.timer.start(1000)

    def update_timer(self):
        # This function is called every second to update the timer display
        if self.mining_process is not None and self.mining_process.state() == QProcess.Running:
            current_time = QDateTime.currentDateTime()
            elapsed_time = self.start_time.secsTo(current_time)
            hours = elapsed_time // 3600
            minutes = (elapsed_time % 3600) // 60
            seconds = elapsed_time % 60
            self.timer_label.setText(f"{hours}h: {minutes}m: {seconds}s")
        # else:
        #     self.data_logger.info(f'Balance Stop: {self.wallet_bal_tao}')
        #     self.data_logger.info(f'- Stop Mining')

    def stop_timer(self):
        # Stop the timer
        self.timer.stop()






