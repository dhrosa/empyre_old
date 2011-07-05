#! /bin/sh
./setup.py --command-packages=stdeb.command sdist_dsc
sed -i 's/${python:Depends}/python (>=2.6)/' deb_dist/empyre-*/debian/control
sed -i 's/${misc:Depends},//' deb_dist/empyre-*/debian/control
sed -i 's/${python:Breaks}//' deb_dist/empyre-*/debian/control
cd deb_dist/empyre-*
dpkg-buildpackage -rfakeroot -uc -us