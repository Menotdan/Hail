# Hail
A simple (and bad) package manager made in python.

## Install
To install hail, either run `install_hail.bat` as administrator if you are on Windows, or run `install_hail.sh` on Linux/Mac.

## .HPKG
`.hpkg` files are simply zip files containing the contents of the package. Hail will extract them during an install.

## Repository_server.py
The repository server allows anyone to host their own package repositories. When a client sends a request to the repository server, it will look for that package and if it's found it will send the full zip file for the package to the client.

## Example_package
An example package is included to demonstrate how the system works. The `hail-info` file in the root of the folder is used to define the package name, version, supported platforms, locations of platform subpackages, and package dependencies. The `hail-subpkg` included in each subpackage defines which platform the subpackage is for, and defines where the install script is for the platform-specific subpackage.

## Features
Cross-platform (Windows/Linux/Mac)

Install Scripts for Packages

Simple(ish) Package Format

Compressed Packages

Installed Packages List

Repository Hosting

Package Dependencies
