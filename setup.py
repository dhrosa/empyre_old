#!/usr/bin/python
from distutils.core import setup
from empyre.version import version
setup (
    name = "Empyre",
    version = version(),
    author = "Diony Rosa",
    author_email = "dhrosa@gmail.com",
    requires = ["PyQt4 (>=4.6)", "yaml", "argparse"], 
    packages = ["empyre", "empyre.client", "empyre.server"],
    package_data = {"empyre": ["boards/*/*"],
                    "empyre.server": ["words"]},
    scripts = ["empyre-client", "empyre-server"]
)
