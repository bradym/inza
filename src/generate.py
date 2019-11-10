# -*- coding: utf-8 -*-

import os
import shutil
import io
import htmlmin
from jinja2 import Environment, FileSystemLoader, select_autoescape
import markdown
import yaml
from pprint import pprint
import pathlib
import datetime
import lesscpy
import glob
import subprocess

# TODO: How to handle js & css minification?
# TODO: How to handle asset bundling?


class InzaGenerator():

    def __init__(self, base_dir=os.getcwd(), autoescape_extensions=['html', 'xml']):
        self.base_dir = base_dir
        self.sub_dirs = ['templates', 'data', 'static', 'pages', 'build']
        self.dirs_no_check = ['build']
        self.get_dirs()
        self.data = {}
        self.env = Environment(loader=FileSystemLoader(self.templates_dir), autoescape=select_autoescape(autoescape_extensions))

    def __repr__(self):
        return str(self.__class__) + '\n' + '\n'.join((str(item) + ' = ' + str(self.__dict__[item]) for item in sorted(self.__dict__)))

    def get_dirs(self):
        for dir_name in self.sub_dirs:
            setattr(self, '{}_dir'.format(dir_name), os.path.join(self.base_dir, dir_name))

    def validate_dirs(self):
        for dir_name in self.sub_dirs:
            if not os.path.isdir(getattr(self, '{}_dir'.format(dir_name))) and dir_name not in self.dirs_no_check:
                raise FileNotFoundError(getattr(self, dir_name))

    def generate_files(self, should_minify):
        for root, dirs, files in os.walk(self.pages_dir):
            for item in files:
                full_path = os.path.join(root, item)
                current = self.parse_markdown(full_path)
                path = current['meta']['path']
                template = current['meta']['template']
                dest = os.path.join(self.build_dir, path)
                page_data = {'meta': current['meta'], 'content': current['content']}
                rendered = self.env.get_template(template).render({**self.data, **page_data})

                if should_minify:
                    file_type = pathlib.Path(path).suffix
                    output = self.minify(rendered, file_type)
                else:
                    output = rendered

                with open(dest, 'w') as f:
                    f.write(output)

    def minify(self, data, file_type):
        if file_type == '.html':
            return htmlmin.minify(data, remove_comments=True)
        else:
            return data

    def parse_markdown(self, file):

        markdown_extensions = [
            'markdown.extensions.meta',
            'markdown.extensions.smarty',
            'markdown.extensions.toc',
            'markdown.extensions.tables',
            'markdown.extensions.codehilite',
            'markdown.extensions.smarty'
        ]

        with open(file, 'r') as f:
            raw_md = f.read()

        m = markdown.Markdown(extensions=markdown_extensions, output_format='html5')
        rendered = m.convert(raw_md)

        meta = {}

        for key in m.Meta:
            if key in ['path', 'template', 'date'] and len(m.Meta[key]) > 1:
                raise AttributeError('Multiple values found for {0}, but {0} must be a single value.'.format(key))

            if len(m.Meta[key]) == 1:
                meta[key] = m.Meta[key][0]
            else:
                meta[key] = ', '.join(m.Meta[key])

        return {
            'meta': meta,
            'content': rendered
        }

    def clean(self):
        shutil.rmtree(self.build_dir, ignore_errors=True)

    def copy_static(self):
        shutil.copytree(self.static_dir, self.build_dir)

    def load_data(self):
        for root, dirs, files in os.walk(self.data_dir):
            for item in files:

                data_type = os.path.basename(root)
                full_path = os.path.join(root, item)
                name = os.path.splitext(item)[0]

                if data_type not in self.data:
                    self.data[data_type] = {}

                with open(full_path, 'rb') as f:
                    self.data[data_type][name] = yaml.load(f)

        self.data['data']['date'] = datetime.datetime.today()

    def compile_less(self):
        less_dir = os.path.join(self.base_dir, 'less')

        if not os.path.isdir(less_dir):
            return

        css_dir = os.path.realpath(os.path.join(self.static_dir, 'css'))

        if not os.path.isdir(css_dir):
            os.makedirs(css_dir)

        for file_name in glob.glob('{}/{}'.format(less_dir, "*.less")):
            less_path = os.path.realpath(file_name)
            base_name = pathlib.Path(less_path).stem
            css_path = os.path.realpath(os.path.join(css_dir, '{}.css'.format(base_name)))

            subprocess.run('lessc {} {}'.format(less_path, css_path), check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)



    def run(self, minify=False):
        self.clean()
        self.validate_dirs()
        self.copy_static()
        self.load_data()
        self.generate_files(minify)
        self.compile_less()
        print('Site generation complete')
