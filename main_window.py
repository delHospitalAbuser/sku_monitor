from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtGui import QCloseEvent
from PySide6.QtCore import QTimer
from winotify import Notification
import csv
from status import Status
from product_status_worker import *



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.sku_line_edit = None
        self.previous_product_availability = {}

        self.setup()
        self.read_file()
        self.set_product_availability()
        self.set_table()
        self.get_product_status()
        self.product_status_refreshing()

    def setup(self):

        
        width = 700

        self.table = QTableWidget(self)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["SKU", "Status"])
        #self.table.move(10, 10)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        sku_label = QLabel("Add SKU:", self)
        sku_label.move(500, 30)

        self.sku_line_edit = QLineEdit('SKU', self)
        self.sku_line_edit.setFixedWidth(200)
        self.sku_line_edit.move(400, 50)

        submit_button = QPushButton('Submit', self)
        submit_button.move(500, 80)
        submit_button.clicked.connect(self.submit)

        quit_button = QPushButton('Quit', self)
        quit_button.move(550, 550)
        quit_button.clicked.connect(QApplication.instance().quit)

        self.setFixedSize(width, 600)
        self.setWindowTitle('Nike_monitor')

        self.show()

    def submit(self):
        self.rowPosition = self.table.rowCount()
        self.table.insertRow(self.rowPosition)
        self.table.setItem(self.rowPosition, 0, QTableWidgetItem(self.sku_line_edit.text()))

        with open('text.txt', 'a') as file:
            file.write(f'{self.sku_line_edit.text()},')

        self.update_product_availability(self.sku_line_edit.text())
        self.update_table()


    def set_product_availability(self):
        self.product_availability = {sku: None for sku in self.skus}
        self.previous_product_availability = self.product_availability.copy()

    def update_product_availability(self, new_key):
        self.product_availability[new_key] = Status(2).name
        self.previous_product_availability[new_key] = Status(2).name

    def send_notification(self):
        for sku, status in self.product_availability.items():
            previous_status = self.previous_product_availability.get(sku)
            if status == Status(1).name and (previous_status == Status(0).name or previous_status == Status(2).name):
                toast = Notification(app_id=f'Nike monitor:{sku}', title='Search result:',
                                     msg=f"Product: {sku} is available", duration='short')
                toast.show()
                self.previous_product_availability[sku] = status

    def read_file(self):
        self.skus = []
        with open('text.txt', 'r') as file:
            csvReader = csv.reader(file, delimiter=',')
            for row in csvReader:
                self.skus.append(row)
        if len(self.skus) > 0:
            self.skus = self.skus[0][:-1]

    def set_table(self):
        self.table.setRowCount(len(self.product_availability))
        for i, (sku, status) in enumerate(self.product_availability.items()):
            self.table.setItem(i, 0, QTableWidgetItem(sku))
     

    def update_table(self):
        for i, (sku, status) in enumerate(self.product_availability.items()):
            self.table.setItem(i, 1, QTableWidgetItem(status))
        self.send_notification()


    def get_product_status(self):
        self.product_status_worker = ProductStatusWorker(self.product_availability)
        self.product_status_worker.updated.connect(self.update_table)
        self.product_status_worker.start()
        

    def product_status_refreshing(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.get_product_status)
        self.timer.start(10000)

    def closeEvent(self, event: QCloseEvent):
        should_close = QMessageBox.question(self, 'Close app', 'Do you really want to quit?',
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if should_close == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()