#!/usr/bin/python

from distutils.core import setup

setup (
    name = "Empyre",
    author = "Diony Rosa",
    author_email = "dhrosa@gmail.com",
    requires = ["PyQt4 (>=4.6)", "yaml"], 
    packages = ["empyre", "empyre.client", "empyre.server"],
    package_data = {"empyre": ["boards/*/*"]},
    scripts = ["empyre-client", "empyre-server"]
)
