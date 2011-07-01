#! /usr/bin/python
import os
os.system("python setup.py --command-packages=stdeb.command sdist_dsc")

controlFile = "deb_dist/empyre-0.0.0/debian/control"

with open(controlFile, "r") as f:
    control = f.read()

control = control.replace("${misc:Depends}, ${python:Depends}",
                          "python (>= 2.6), python-qt4 (>= 4.7), python-yaml")
control = control.replace("Breaks: ${python:Breaks}",
                          "")
control = control.replace("\nDescription", "Description")
control = control[:-1] + "XS-Python-Version: >= 2.6\n"

with open(controlFile, "w") as f:
    f.write(control)

os.system("cd deb_dist/empyre-0.0.0 && dpkg-buildpackage -rfakeroot -uc -us")
