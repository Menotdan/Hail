#!/usr/bin/env python3
import sys
import zipfile
import os
import packer
import packages
import installer
import directory

hail_data_path = ""

def setup_hail():
    global hail_data_path

    home = os.path.expanduser("~")
    if installer.get_platform() == "windows":
        hail_data_path = os.path.join(home, "AppData\\Local\\hail")
        if not os.path.isdir(hail_data_path):
            os.mkdir(hail_data_path)
            open(os.path.join(hail_data_path, "installed-packages"), "w").close()
            open(os.path.join(hail_data_path, "trusted-packages"), "w").close()
            open(os.path.join(hail_data_path, "repositories"), "w").close()
    else:
        hail_data_path = os.path.join(home, ".hail")
        if not os.path.isdir(hail_data_path):
            os.mkdir(hail_data_path)
            open(os.path.join(hail_data_path, "installed-packages"), "w").close()
            open(os.path.join(hail_data_path, "trusted-packages"), "w").close()
            open(os.path.join(hail_data_path, "repositories"), "w").close()

def main(argv):
    setup_hail()
    option_string = None
    for a in argv:
        if a[0] == "+":
            option_string = a[1:]

    if len(argv) < 2:
        print("Usage: hail <command> [file] [option string (starts with a +)]")
        exit(1) # Error
        quit()
    if len(argv) > 3 and option_string == None or len(argv) > 4:
        print("Usage: hail <command> [file] [option string (starts with a +)]")
        exit(1) # Error
        quit()
    
    if argv[1] == "package":
        if len(argv) < 3 or (option_string != None and len(argv) < 4):
            print("Expected a [file] argument for this command!")
            exit(1) # Error
            quit()
        folder = argv[2]

        if folder[0] != "\\" and folder[0] != "/":
            folder = os.path.join("./", folder)
        print("Attempting to package folder " + folder + ".")

        # Validate package and zip it
        try:
            packer.create_package(folder)
        except Exception as e:
            print("Failed to create package! Folder may be missing!")
            print("Python error: " + str(e))
            exit(1) # Error
            quit()
    elif argv[1] == "unpackage":
        if len(argv) < 3 or (option_string != None and len(argv) < 4):
            print("Expected a [file] argument for this command!")
            exit(1) # Error
            quit()
        package = argv[2]

        if package[0] != "\\" and package[0] != "/":
            package = os.path.join("./", package)
        print("Attempting to unpackage " + package + ".")

        folder = ""
        try:
            folder = packer.extract_package(package)
        except Exception as e:
            print("Package is not valid (Attempting extraction)!")
            print("Python error: " + str(e))
            exit(1) # Error
            quit()

    elif argv[1] == "install":
        if len(argv) < 3 or (option_string != None and len(argv) < 4):
            print("Expected a [file] argument for this command!")
            exit(1) # Error
            quit()
        package = argv[2]

        if package[0] != "\\" and package[0] != "/":
            package = os.path.join("./", package)
        print("Attempting to install " + package + ".")

        installer.install_package(package, hail_data_path)

os.chdir(sys.argv[len(sys.argv) - 1])
sys.argv.pop()
main(sys.argv)
print("Hail done.")