
from PyQt5 import QtWidgets, QtCore


class ConfirmDeleteDialog(QtWidgets.QDialog):
    confirmed = QtCore.pyqtSignal()

    def __init__(self, parent: QtWidgets.QWidget, proj_dir: str, path: str):
        super().__init__(parent, QtCore.Qt.WindowType.Popup)

        is_file = QtCore.QFileInfo(path).isFile()

        label_1 = QtWidgets.QLabel(f"Project name: {QtCore.QDir(proj_dir).dirName()}")
        label_2 = QtWidgets.QLabel(f"Deleting {'file' if is_file else 'dir'}: {QtCore.QDir(proj_dir).relativeFilePath(path)}")
        label_3 = QtWidgets.QLabel("Confirm delete")
        button = QtWidgets.QPushButton("Confirm")

        button.clicked.connect(self._confirm)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(label_1)
        layout.addWidget(label_2)
        layout.addWidget(label_3)
        layout.addWidget(button, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
        self.setLayout(layout)

    def _confirm(self) -> None:
        self.confirmed.emit()
        self.close()
