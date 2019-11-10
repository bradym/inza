#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
from server import InzaServe
from generate import InzaGenerator
from pprint import pprint
import os

# TODO: Add command to check for issues and link to documentation on how to fix


@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    pass


# TODO: Function to initialize base directory & create all required directories
# TODO: Create settings file as part of init
# TODO: Prompt user for input on whether or not to create the following
# TODO: Create .gitignore
# TODO: Create .pre-commit-config.yaml
# TODO: Create package.json
@cli.command()
def init():
    pass


# TODO: Function to generate site (generate.py)
@cli.command()
@click.option('--base-dir', default=os.getcwd())
@click.option('--minify', default=False)
def generate(base_dir, minify):
    g = InzaGenerator(base_dir=base_dir)
    g.run(minify)


@cli.command()
@click.option('--base-dir', default=os.getcwd())
def serve(base_dir):
    s = InzaServe(base_dir=base_dir)
    s.serve()


@cli.command()
def testing():

    import markdown

    md = markdown.Markdown(extensions=[
        'markdown.extensions.meta',
        'markdown.extensions.smarty',
        'markdown.extensions.toc',
        'markdown.extensions.tables',
        'markdown.extensions.codehilite',
        'markdown.extensions.smarty'
    ], extension_configs={
        'markdown.extensions.codehilite': {
            'pygments_style': 'default'
        }
    }, output_format='html5')

    md.convertFile(input=os.path.expanduser("~/Desktop/next.md"), output=os.path.expanduser("~/Desktop/next.html"))

    pprint(md.Meta)

    pass

if __name__ == '__main__':
    cli()
