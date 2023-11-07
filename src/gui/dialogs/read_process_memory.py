from PyQt5.QtWidgets import QDialog, QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QMessageBox

from masup.modules.processes import Process
from gui.dialogs.hex_viewer import HexViewer
import pymem.exception

class ReadProcessMemory(QDialog):
    def __init__(self, parent=None):
        super(ReadProcessMemory, self).__init__(parent)

        self.parent_window = parent
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Read process memory')

        self.process_name = QLineEdit(self)
        self.start_address = QLineEdit(self)
        self.bytes_length = QLineEdit(self)

        formLayout = QFormLayout()
        formLayout.addRow('Process name:', self.process_name)
        formLayout.addRow('Memory address:', self.start_address)
        formLayout.addRow('Length:', self.bytes_length)

        saveButton = QPushButton('View', self)
        saveButton.clicked.connect(self.view)

        cancelButton = QPushButton('Cancel', self)
        cancelButton.clicked.connect(lambda x : self.close())

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(saveButton)
        buttonLayout.addWidget(cancelButton)

        mainLayout = QVBoxLayout(self)
        mainLayout.addLayout(formLayout)
        mainLayout.addLayout(buttonLayout)
    
    def view(self):
        try:
            process = Process(self.process_name.text())
        except pymem.exception.ProcessNotFound as msg:
            self.show_error_dialog(str(msg))
            return

        try:
            memory = process.extract_memory(int(self.start_address.text(), 16), int(self.bytes_length.text()))
        except ValueError:
            self.show_error_dialog(f"{self.bytes_length.text()} is not a valid hex value")
            return
        except pymem.exception.MemoryReadError:
            self.show_error_dialog(f"Could not read memory at: {self.start_address.text()}, length: {self.bytes_length.text()}")
            return

        HexViewer(f"Memory view of {self.process_name.text()} @ address {self.start_address.text()}, showing {self.bytes_length.text()} bytes", memory, self.parent_window).show()

        self.close()
    
    def show_error_dialog(self, message):
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle("Error")
        error_dialog.setText(f"An error occurred:\n{message}")
        error_dialog.exec_()