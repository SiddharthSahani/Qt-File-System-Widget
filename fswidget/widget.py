
from typing import Optional, NamedTuple
from PyQt5 import QtWidgets, QtCore
from .view import FileSystemView
from .new_item_dialog import NewItemDialog
from .rename_item_dialog import RenameItemDialog
from .confirm_delete_dialog import ConfirmDeleteDialog
from .import file_handling


class Config(NamedTuple):
    can_create_file: bool = True
    can_rename_file: bool = True
    can_remove_file: bool = True
    can_create_dir: bool = True
    can_rename_dir: bool = True
    can_remove_dir: bool = False
    confirm_removal: bool = True


class FileSystemWidget(QtWidgets.QMainWindow):
    open_file_request = QtCore.pyqtSignal(str)
    new_file_created = QtCore.pyqtSignal(str)
    file_renamed = QtCore.pyqtSignal(str, str)
    file_removed = QtCore.pyqtSignal(str)
    new_dir_created = QtCore.pyqtSignal(str)
    dir_renamed = QtCore.pyqtSignal(str, str)
    dir_removed = QtCore.pyqtSignal(str)

    def __init__(self, roots: list[str], exclude_patterns: Optional[list[str]] = None, config: Config = Config()) -> None:
        super().__init__()

        self.roots = roots
        self.views = [FileSystemView(root, exclude_patterns) for root in roots]
        self.config = config

        for view in self.views:
            view.doubleClicked.connect(self._double_clicked)
        
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._handle_context_menu)
        
        self.view_displayer = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        for view in self.views:
            self.view_displayer.addWidget(view)
        self.view_displayer.setHandleWidth(0)
        self.view_displayer.setChildrenCollapsible(False)
        self.setCentralWidget(self.view_displayer)

    def set_splitter_sizes(self, sizes: list[int]) -> None:
        self.view_displayer.setSizes(sizes)

    def set_icon_provider(self, icon_provider: QtWidgets.QFileIconProvider) -> None:
        for view in self.views:
            view.set_icon_provider(icon_provider)

    def get_index(self, view_idx: int, proxy_index: QtCore.QModelIndex) -> QtCore.QModelIndex:
        return self.views[view_idx]._filter_model.mapToSource(proxy_index)

    def get_info(self, view_idx: int, proxy_index: QtCore.QModelIndex) -> QtCore.QFileInfo:
        index = self.get_index(view_idx, proxy_index)
        return self.views[view_idx]._file_model.fileInfo(index)

    def _get_view_idx(self, pos: QtCore.QPoint) -> int:
        for idx, view in enumerate(self.views):
            if view.geometry().contains(pos):
                return idx
        return -1

    def _get_proxy_index(self, view_idx: int, pos: QtCore.QPoint) -> QtCore.QModelIndex:
        y_offset = sum(self.views[i].height() for i in range(view_idx))
        pos.setY(pos.y() - y_offset)
        return self.views[view_idx].indexAt(pos)
    
    def _handle_context_menu(self, pos: QtCore.QPoint) -> None:
        view_idx = self._get_view_idx(pos)
        if view_idx == -1:
            return
        
        proxy_index = self._get_proxy_index(view_idx, pos)
        fileinfo = self.get_info(view_idx, proxy_index)
        path = fileinfo.filePath()

        menu = QtWidgets.QMenu()

        if path:
            if fileinfo.isFile():
                menu.addAction("Open in editor", lambda: self._open_file(path))
                if self.config.can_rename_file:
                    menu.addAction("Rename file", lambda: self._rename_file(view_idx, fileinfo.dir().path(), fileinfo.fileName()))
                if self.config.can_remove_file:
                    menu.addAction("Remove file", lambda: self._remove_file(view_idx, path))
            else:
                if self.config.can_create_file:
                    menu.addAction("New file", lambda: self._create_new_file(view_idx, path))
                if self.config.can_create_dir:
                    menu.addAction("New subdir", lambda: self._create_new_dir(view_idx, path))
                if self.config.can_rename_dir:
                    menu.addAction("Rename dir", lambda: self._rename_dir(view_idx, fileinfo.dir().path(), fileinfo.fileName()))
                if self.config.can_remove_dir:
                    menu.addAction("Remove dir", lambda: self._remove_dir(view_idx, path))
            menu.addAction("Copy relative path", lambda: QtWidgets.QApplication.clipboard().setText(QtCore.QDir(self.roots[view_idx]).relativeFilePath(path)))
            menu.addAction("Copy full path", lambda: QtWidgets.QApplication.clipboard().setText(path))
        else:
            path = self.roots[view_idx]
            if self.config.can_create_file:
                menu.addAction("New file", lambda: self._create_new_file(view_idx, path))
            if self.config.can_create_dir:
                menu.addAction("New subdir", lambda: self._create_new_dir(view_idx, path))
            menu.addAction("Copy project path", lambda: QtWidgets.QApplication.clipboard().setText(path))
        
        y_offset = sum(self.views[i].height() for i in range(view_idx))
        pos.setY(pos.y() + y_offset)
        menu.exec(self.mapToGlobal(pos))

    def _double_clicked(self, proxy_index: QtCore.QModelIndex) -> None:
        proj_path = proxy_index.model().sourceModel().rootPath() # type: ignore
        view_idx = self.roots.index(proj_path)
        fileinfo = self.get_info(view_idx, proxy_index)
        if fileinfo.isFile():
            self.open_file_request.emit(fileinfo.filePath())

    def _create_new_dir(self, view_idx: int, dirpath: str) -> None:
        def func(name: str) -> None:
            if file_handling.new_dir(dirpath, name):
                self.new_dir_created.emit(file_handling.add_path(dirpath, name))

        dia = NewItemDialog(self, self.roots[view_idx], dirpath, False)
        dia.create_request.connect(func)
        dia.exec()

    def _rename_dir(self, view_idx: int, dirpath: str, name: str) -> None:
        def func(new_name: str) -> None:
            if file_handling.rename_dir(dirpath, name, new_name):
                self.dir_renamed.emit(file_handling.add_path(dirpath, name), file_handling.add_path(dirpath, new_name))
        
        dia = RenameItemDialog(self, self.roots[view_idx], dirpath, name)
        dia.rename_request.connect(func)
        dia.exec()
    
    def _remove_dir(self, view_idx: int, dirpath: str) -> None:
        def func():
            if file_handling.remove_dir(parent_dirpath, name):
                self.dir_removed.emit(info.filePath())

        info = QtCore.QFileInfo(dirpath)
        parent_dirpath = info.dir().path()
        name = info.fileName()
        if self.config.confirm_removal:
            dia = ConfirmDeleteDialog(self, self.roots[view_idx], dirpath)
            dia.confirmed.connect(func)
            dia.exec()
        else:
            func()

    def _create_new_file(self, view_idx: int, dirpath: str) -> None:
        def func(name: str) -> None:
            if file_handling.new_file(dirpath, name):
                self.new_file_created.emit(file_handling.add_path(dirpath, name))
        
        dia = NewItemDialog(self, self.roots[view_idx], dirpath, True)
        dia.create_request.connect(func)
        dia.exec()

    def _rename_file(self, view_idx: int, dirpath: str, name: str) -> None:
        def func(new_name: str) -> None:
            if file_handling.rename_file(dirpath, name, new_name):
                self.file_renamed.emit(file_handling.add_path(dirpath, name), file_handling.add_path(dirpath, new_name))
        
        dia = RenameItemDialog(self, self.roots[view_idx], dirpath, name)
        dia.rename_request.connect(func)
        dia.exec()

    def _remove_file(self, view_idx: int, filepath: str) -> None:
        def func():
            if file_handling.remove_file(dirpath, name):
                self.file_removed.emit(filepath)

        info = QtCore.QFileInfo(filepath)
        dirpath = info.dir().path()
        name = info.fileName()
        if self.config.confirm_removal:
            dia = ConfirmDeleteDialog(self, self.roots[view_idx], filepath)
            dia.confirmed.connect(func)
            dia.exec()
        else:
            func()

    def _open_file(self, filepath: str) -> None:
        self.open_file_request.emit(filepath)
