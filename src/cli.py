#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import server


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
def generate():
    pass


@cli.command()
def serve():
    s = server.InzaServe(base_dir="~/code/family2/")
    s.serve()


if __name__ == '__main__':
    cli()
