#!/bin/bash

set -e

# Quick and Dirty check about parameters
if [ $# -ne 1 ]; then
	cat << EOF

Usage: $(basename $0) version

version:
  the version number (eg: 1.0.0)

EOF
	exit 1
fi

# Quick and Dirty check about the PWD
if [ $(dirname $(readlink -f $0)) != $PWD ]; then
	cat << EOF

Please run the script from is root directory:

cd $(dirname $(readlink -f $0))

EOF
	exit 1
fi

# Main

VERSION=$1

echo "Updating version..."

# setup
sed -i "s/version=.*/version='$VERSION',/" ./setup.py
# docs
sed -i "s/version = .*/version = '$VERSION'/" ./gendocs/conf.py
sed -i "s/release = .*/release = '$VERSION'/" ./gendocs/conf.py
# packaging
sed -i "s/pkgver=.*/pkgver='$VERSION'/" ./packaging/archlinux/PKGBUILD
sed -i "s/pkgrel=.*/pkgrel=1/" ./packaging/archlinux/PKGBUILD

# generate docs
echo "Generating docs..."
cd gendocs
make clean > /dev/null
make html > /dev/null
rsync -crv --delete --exclude=README.rst _build/html/ ../docs/ > /dev/null
cd ..

# git add
echo "Preparing git commit..."
git add .

# python module for pypi
echo "python module creation..."
if [ -d "./dist/" ]; then
	rm -f ./dist/* > /dev/null
fi
python setup.py bdist_wheel > /dev/null

# NOTICE
cat << EOF

Please check that everything is fine by running :"

git diff HEAD

Once checked, please run :

git commit -m "Bump version: $VERSION"
git push origin master

git tag -m "$VERSION" $VERSION
git push origin $VERSION

# pypi
twine upload dist/*

EOF
