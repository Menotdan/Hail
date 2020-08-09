import zipfile
import os
import packages
import directory

hail_pkg_ext = ".hpkg"

def get_zip_root_name(filepath):
    folder = ""
    with zipfile.ZipFile(filepath, "r") as zf:
        dirs = list(set([os.path.dirname(x) for x in zf.namelist()]))
        folder = [os.path.split(x)[0] for x in dirs]
        for f in folder:
            if f != "":
                folder = f
                break

    return folder

def extract_zip(filepath):
    with zipfile.ZipFile(filepath, "r") as zf:
        zf.extractall()

def extract_package(package):
    extract_zip(package)
    folder = get_zip_root_name(package)
    packages.check_package(folder)
    return folder

def create_package(folder):
    packages.check_package(folder)
    with zipfile.ZipFile(packages.get_package_name(folder) + hail_pkg_ext, "w") as zf:
        paths = directory.get_all_files(folder)
        for file in paths:
            zf.write(file)