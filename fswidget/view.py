
from typing import Optional
from fnmatch import fnmatch
from PyQt5 import QtWidgets, QtCore


class FileFilterModel(QtCore.QSortFilterProxyModel):

    def __init__(self, exclude_patterns: list[str]) -> None:
        super().__init__()
        self.exclude_patterns = exclude_patterns

    def filterAcceptsRow(self, source_row: int, source_parent: QtCore.QModelIndex) -> bool:
        idx = self.sourceModel().index(source_row, 0, source_parent)
        path = self.sourceModel().filePath(idx) # type: ignore
        return not any(fnmatch(path, pat) for pat in self.exclude_patterns)
    
    def filterAcceptsColumn(self, source_column: int, source_parent: QtCore.QModelIndex) -> bool:
        return source_column == 0


class FileSystemView(QtWidgets.QTreeView):

    def __init__(self, root: str, exclude_patterns: Optional[list[str]] = None):
        super().__init__()
        self.root = root

        self._file_model = QtWidgets.QFileSystemModel()
        root_idx = self._file_model.setRootPath(root)
        self._filter_model = FileFilterModel(exclude_patterns or [])
        self._filter_model.setSourceModel(self._file_model)

        self.setModel(self._filter_model)
        self.setRootIndex(self._filter_model.mapFromSource(root_idx))
        self.setHeaderHidden(True)

    def set_icon_provider(self, icon_provider: QtWidgets.QFileIconProvider):
        self._file_model.setIconProvider(icon_provider)
