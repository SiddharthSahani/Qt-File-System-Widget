
import sys
from PyQt5 import QtWidgets, QtCore
from fswidget import FileSystemWidget, Config


app = QtWidgets.QApplication([])

# bunch of test directories
roots = [
    QtCore.QDir.homePath(),
    QtCore.QDir.currentPath(),
    QtCore.QFileInfo(sys.executable).dir().path(),
]

# patterns to not show
exclude_patterns = [
    '*/env',
    '*/__pycache__',
    '*/.mypy_cache',
    '*.exe'
]

# configurations
config = Config(can_rename_file=False, can_rename_dir=False)


wid = FileSystemWidget(roots, exclude_patterns=exclude_patterns, config=config)
wid.setWindowTitle('FSWidget demo')
wid.set_splitter_sizes([1000, 2000, 2000])
wid.resize(400, 600)
wid.show()

wid.open_file_request.connect(lambda filepath: print('Opening', filepath))
wid.new_file_created.connect(lambda path: print('New file', path))
wid.new_dir_created.connect(lambda path: print('New dir', path))
wid.file_renamed.connect(lambda oldpath, newpath: print('Renamed file', oldpath, 'to', newpath))
wid.dir_renamed.connect(lambda oldpath, newpath: print('Renamed dir', oldpath, 'to', newpath))
wid.file_removed.connect(lambda path: print('Removed file', path))
wid.dir_removed.connect(lambda path: print('Removed dir', path))


app.exec()
