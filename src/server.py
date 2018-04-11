# -*- coding: utf-8 -*-

import glob
import os

from livereload import Server
from livereload.watcher import Watcher

import generate


class CustomWatcher(Watcher):

    def is_glob_changed(self, path, ignore=None):
        for f in glob.glob(path, recursive=True):
            if self.is_file_changed(f, ignore):
                return True
        return False


class InzaServe():

    def __init__(self, base_dir=os.getcwd()):
        self.base_dir = os.path.realpath(os.path.expanduser(base_dir))
        self.build_dir = os.path.join(self.base_dir, 'build')
        self.watch_paths = ['data', 'node_modules', 'static', 'templates']

    def serve(self):
        g = generate.InzaGenerator(base_dir=self.base_dir)
        g.run()

        server = Server(watcher=CustomWatcher())

        for path in self.watch_paths:
            current_path = os.path.join(self.base_dir, path)
            server.watch('./{}/**/*'.format(current_path), g.run())

        server.serve(root=self.build_dir)
