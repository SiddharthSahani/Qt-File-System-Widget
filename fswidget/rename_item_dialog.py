
from PyQt5 import QtWidgets, QtCore
from .file_handling import exists, add_path


class RenameItemDialog(QtWidgets.QDialog):
    rename_request = QtCore.pyqtSignal(str)

    def __init__(self, parent: QtWidgets.QWidget, proj_dir: str, parent_dir: str, name: str):
        super().__init__(parent, QtCore.Qt.WindowType.Popup)
        self.proj_dir = proj_dir
        self.parent_dir = parent_dir
        self.is_file = QtCore.QFileInfo(QtCore.QDir(parent_dir).filePath(name)).isFile()

        label_1 = QtWidgets.QLabel(f"Project name: {QtCore.QDir(proj_dir).dirName()}")
        label_2 = QtWidgets.QLabel(f"Rename {'file' if self.is_file else 'dir'} from: {name}")
        label_3 = QtWidgets.QLabel(f"To:")
        self.name_editor = QtWidgets.QLineEdit(name)
        self.status_label = QtWidgets.QLabel()

        self.name_editor.selectAll()
        self.name_editor.textChanged.connect(self._update)
        self.name_editor.returnPressed.connect(self._create)

        main_layout = QtWidgets.QVBoxLayout()
        sub_layout = QtWidgets.QHBoxLayout()
        main_layout.addWidget(label_1)
        main_layout.addWidget(label_2)
        main_layout.addLayout(sub_layout)
        main_layout.addWidget(self.status_label)
        sub_layout.addWidget(label_3)
        sub_layout.addWidget(self.name_editor)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        QtCore.QTimer.singleShot(100, self.name_editor.setFocus)

    def _update(self, name: str) -> None:
        if not name:
            self.status_label.setStyleSheet("")
            self.status_label.clear()
            return
        
        rel_path = QtCore.QDir(self.proj_dir).relativeFilePath(add_path(self.parent_dir, name))
        if exists(self.parent_dir, name):
            if self.is_file:
                self.status_label.setText(f"File at {rel_path!r} already exists")
            else:
                self.status_label.setText(f"Dir at {rel_path!r} already exists")
            self.status_label.setStyleSheet("background-color: red")
        else:
            if self.is_file:
                self.status_label.setText(f"File will be renamed to: {rel_path!r}")
            else:
                self.status_label.setText(f"Dir will be renamed to: {rel_path!r}")
            self.status_label.setStyleSheet("background-color: green")

    def _create(self) -> None:
        name = self.name_editor.text()
        if not name:
            return
        self.rename_request.emit(name)
        self.close()
