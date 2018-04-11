# -*- coding: utf-8 -*-

import os
import shutil

import htmlmin
from jinja2 import Environment, FileSystemLoader, select_autoescape
import yaml


# TODO: Where should rst -> html conversion be done?
# TODO: How to handle js & css minification?
# TODO: How to handle asset bundling?


class InzaGenerator():

    def __init__(self, base_dir=os.getcwd(), output_suffix='.html', template_suffix='.j2', autoescape_extensions=['html', 'xml']):
        self.output_suffix = output_suffix
        self.template_suffix = template_suffix
        self.base_dir = base_dir
        self.template_dir = os.path.join(self.base_dir, 'templates')
        self.content_dir = os.path.join(self.base_dir, 'content')
        self.data_dir = os.path.join(self.base_dir, 'data')
        self.build_dir = os.path.join(self.base_dir, 'build')
        self.static_dir = os.path.join(self.base_dir, 'static')
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(autoescape_extensions)
        )

        # TODO: Move these to a separate function and run during build instead of init
        for path in [self.base_dir, self.template_dir, self.data_dir]:
            if not os.path.isdir(path):
                raise FileNotFoundError(path)

        if not os.path.isdir(self.build_dir):
            os.mkdir(self.build_dir)

        self.data = {}

    def __repr__(self):
        return str(self.__class__) + '\n' + '\n'.join((str(item) + ' = ' + str(self.__dict__[item]) for item in sorted(self.__dict__)))

    def get_build_path(self, what):
        return os.path.join(self.build_dir, '{}'.format(what))

    # TODO: Make this more generic, should be able to generate xml for rss feeds using this function as well
    # TODO: Minification should be optional and set via class property
    # TODO: Create separate function for minification that handles different file types
    def write_file(self, template, path):
        rendered = self.env.get_template(template).render(self.data)
        minified = htmlmin.minify(rendered, remove_comments=True)
        with open(path, 'w') as f:
            f.write(minified)

    # TODO: Should this be merged with write_file?
    # TODO: Rename to generate_file
    # TODO: Allow user to pass in output_suffix for generating rss feeds and other file types
    def generate_page(self, template_name, item):
        self.data['current_item'] = item
        dest = self.get_build_path('{}{}'.format(item, self.output_suffix))
        template = '{}{}'.format(template_name, self.template_suffix)
        self.write_file(template, dest)

    # TODO: This feels like overkill. Nuke build directory and re-create?
    def clean(self):
        for root, dirs, files in os.walk(self.build_dir, topdown=False):
            for item in files:
                path = os.path.join(root, item)
                os.remove(path)
            for item in dirs:
                path = os.path.join(root, item)
                if not os.path.islink:
                    os.rmdir(path)

    def copy_static(self):

        # TODO: Make this more generic and use class variable to set name of folder rather than hard-coding node_modules
        for current_dir in [os.path.join(self.base_dir, 'node_modules'), self.static_dir]:

            for root, dirs, files in os.walk(current_dir):

                for item in files:
                    source = os.path.join(root, item)
                    base = os.path.basename(root)

                    if base == 'static':
                        dest_dir = self.build_dir
                    elif 'node_modules' in root:
                        node_module = root.split('node_modules')[1].lstrip('/').split('/')[0]
                        dest_dir = os.path.join(self.build_dir, node_module, os.path.basename(root))
                    else:
                        dest_dir = os.path.join(self.build_dir, os.path.basename(root))

                    if not os.path.isdir(dest_dir):
                        os.makedirs(dest_dir)

                    dest = os.path.join(dest_dir, item)
                    shutil.copyfile(source, dest)

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

    # TODO: Figure out how to handle generating pages and customization of what to generate
    def run(self):
        self.clean()
        self.copy_static()
        self.load_data()
        self.generate_page('index', 'index')

        for item in self.data['people']:
            self.generate_page('person', item)

        print('Site generation complete')
