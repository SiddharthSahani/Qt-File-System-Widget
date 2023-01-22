
from PyQt5.QtCore import QFile, QDir, QFileInfo


def add_path(root: str, name: str) -> str:
    return QDir(root).filePath(name)

def exists(root_dir: str, name: str) -> bool:
    dir = QDir(root_dir)
    return QFileInfo.exists(dir.filePath(name))


def new_file(root_dir: str, filename: str) -> bool:
    filepath = add_path(root_dir, filename)
    file = QFile(filepath)
    return file.open(QFile.OpenModeFlag.NewOnly)

def rename_file(root_dir: str, old_filename: str, new_filename: str) -> bool:
    old_filepath = add_path(root_dir, old_filename)
    new_filepath = add_path(root_dir, new_filename)
    return QFile.rename(old_filepath, new_filepath)

def remove_file(root_dir: str, filename: str) -> bool:
    filepath = QDir(root_dir).filePath(filename)
    return QFile.moveToTrash(filepath)[0]


def new_dir(root_dir: str, dirname: str) -> bool:
    dir = QDir(root_dir)
    return dir.mkdir(dirname)

def rename_dir(root_dir: str, old_dirname: str, new_dirname: str) -> bool:
    dir = QDir(root_dir)
    return dir.rename(old_dirname, new_dirname)

def remove_dir(root_dir: str, dirname: str) -> bool:
    dirpath = add_path(root_dir, dirname)
    return QFile.moveToTrash(dirpath)[0]
