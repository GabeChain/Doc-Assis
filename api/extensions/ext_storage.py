import os
import shutil
import platform

from flask import Flask

# Redirect PosixPath to WindowsPath on Windows

if platform.system() == "Windows":
    import pathlib

    temp = pathlib.PosixPath
    pathlib.PosixPath = pathlib.WindowsPath

class Storage:
    def __init__(self):
        self.storage_type = None
        self.client = None
        self.folder = None

    def init_app(self, app: Flask, folder: str = 'storage'):
        self.folder = folder
        if not os.path.isabs(self.folder):
            self.folder = os.path.join(app.root_path, self.folder)

    def save(self, filename, file):
        if not self.folder or self.folder.endswith('/'):
            filename = self.folder + filename
        else:
            filename = self.folder + '/' + filename

        folder = os.path.dirname(filename)
        os.makedirs(folder, exist_ok=True)

        with open(os.path.join(os.getcwd(), filename), "wb") as f:
            f.write(file)

    def load(self, filename):
        if not self.folder or self.folder.endswith('/'):
            filename = self.folder + filename
        else:
            filename = self.folder + '/' + filename

        if not os.path.exists(filename):
            raise FileNotFoundError("File not found")

        with open(filename, "rb") as f:
            file = f.read()

        return file

    def download(self, filename, target_filepath):
        if not self.folder or self.folder.endswith('/'):
            filename = self.folder + filename
        else:
            filename = self.folder + '/' + filename

        if not os.path.exists(filename):
            raise FileNotFoundError("File not found")

        shutil.copyfile(filename, target_filepath)

    def exists(self, filename):
        if not self.folder or self.folder.endswith('/'):
            filename = self.folder + filename
        else:
            filename = self.folder + '/' + filename

        return os.path.exists(filename)


storage = Storage()


def init_app(app: Flask, folder):
    storage.init_app(app, folder)
