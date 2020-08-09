#!/usr/bin/env python3
import sys
import zipfile
import os

hail_pkg_ext = ".hpkg"
hail_data_path = ""

def get_all_files(directory):
    paths = []
    for root, dirs, files in os.walk(directory):
        for f_name in files:
            path = os.path.join(root, f_name)
            paths.append(path)
    return paths

def validate_subpackage_and_exit_on_fail(folder, subpackage_name):
    if "hail-subpkg" not in os.listdir(folder):
        print("Subpackage " + subpackage_name + " is missing hail-subpkg!")
        exit(1) # Error
    
    ret = ""
    
    package_info = open(os.path.join(folder, "hail-subpkg"), "r")
    linec = 1
    for line in package_info:
        line = line.replace("\n", "").replace("\r", "")

        info = line.split("=")
        if info[0] == "platform":
            if len(info) != 2:
                print("Invalid subpackage configuration!")
                print("Missing a key or value on line " + str(linec) + ", subpackage " + subpackage_name +" !")
                exit(1) # Error
        if info[0] == "install-script":
            if len(info) != 2:
                print("Invalid subpackage configuration!")
                print("Missing a key or value on line " + str(linec) + ", subpackage " + subpackage_name +" !")
                exit(1) # Error
            ret = info[1]
    
    if ret == "":
        print("No install script for subpackage " + subpackage_name + "!")
        exit(1) # Error
    return ret

def validate_package_and_exit_on_fail(folder):
    returned_info = {}
    platforms = []
    linux_subpkg_path = ""
    windows_subpkg_path = ""
    mac_subpkg_path = ""

    if "hail-info" not in os.listdir(folder):
        print("Package is missing hail-info!")
        exit(1) # Error

    package_info = open(os.path.join(folder, "hail-info"), "r")
    linec = 1
    for line in package_info:
        line = line.replace("\n", "").replace("\r", "")

        info = line.split("=")
        # print(info)
        if info[0] == "platforms":
            if len(info) != 2:
                print("Invalid package configuration!")
                print("Missing a key or value on line " + str(linec) + "!")
                exit(1) # Error

            platforms = info[1].split(",")
            if len(platforms) == 0 or platforms[0] == "":
                print("This package does not support any platforms!")
                exit(1) # Error
        elif info[0] == "name":
            if len(info) != 2:
                print("Invalid package configuration!")
                print("Missing a key or value on line " + str(linec) + "!")
                exit(1) # Error
            returned_info["name"] = info[1]
        elif info[0] == "linux-subpackage":
            if len(info) != 2:
                print("Invalid package configuration!")
                print("Missing a key or value on line " + str(linec) + "!")
                exit(1) # Error
            
            linux_subpkg_path = info[1]
        elif info[0] == "windows-subpackage":
            if len(info) != 2:
                print("Invalid package configuration!")
                print("Missing a key or value on line " + str(linec) + "!")
                exit(1) # Error
            
            windows_subpkg_path = info[1]
        elif info[0] == "mac-subpackage":
            if len(info) != 2:
                print("Invalid package configuration!")
                print("Missing a key or value on line " + str(linec) + "!")
                exit(1) # Error
            
            mac_subpkg_path = info[1]

        linec += 1
    
    subpackage_paths = []
    subpackage_names = []
    subpackage_platforms = []

    for p in platforms:
        if p != "linux" and p != "windows" and p != "mac":
            print("Invalid platform " + p + " listed as supported in package config!")
            print("Supported platforms are [linux, windows, mac].")
            exit(1) # Error

        if p == "linux":
            if linux_subpkg_path == "":
                print("No subpackage path found for " + p + " platform listed as supported!")
                exit(1) # Error
            subpackage_paths.append(os.path.join(folder, linux_subpkg_path))
            subpackage_names.append(linux_subpkg_path)
            subpackage_platforms.append(p)
        if p == "windows":
            if windows_subpkg_path == "":
                print("No subpackage path found for " + p + " platform listed as supported!")
                exit(1) # Error
            subpackage_paths.append(os.path.join(folder, windows_subpkg_path))
            subpackage_names.append(windows_subpkg_path)
            subpackage_platforms.append(p)
        if p == "mac":
            if mac_subpkg_path == "":
                print("No subpackage path found for " + p + " platform listed as supported!")
                exit(1) # Error
            subpackage_paths.append(os.path.join(folder, mac_subpkg_path))
            subpackage_names.append(mac_subpkg_path)
            subpackage_platforms.append(p)
        
    package_info.close()

    install_scripts = []
    install_scripts_info = {}
    for i in range(len(subpackage_paths)):
        install_script = validate_subpackage_and_exit_on_fail(subpackage_paths[i], subpackage_names[i])
        install_scripts.append(install_script)
        install_scripts_info[subpackage_platforms[i]] = install_script

    subpackages = {}
    for i in range(len(subpackage_platforms)):
        subpackages[subpackage_platforms[i]] = subpackage_paths[i]

    returned_info["install_scripts"] = install_scripts_info
    returned_info["platforms"] = platforms
    returned_info["subpackages"] = subpackages

    return returned_info

def get_platform():
    p = sys.platform
    if p == "linux" or p == "linux2":
        return "linux"
    if p == "win32":
        return "windows"
    if p == "darwin":
        return "mac"

def validate_script_and_run(script_path, script_cwd):
    with open(script_path, "r") as script_fp:
        # Check script for weird things
        pass
    old_cwd = os.getcwd()
    os.chdir(script_cwd)
    os.system(script_path)
    os.chdir(old_cwd)

def install_package_and_exit_on_failure(folder, package_info):
    if not get_platform() in package_info["platforms"]:
        print("This package does not support the current platform! (" + get_platform() + ")!")
        exit(1)
    install_script_name = package_info["install_scripts"][get_platform()]
    subpackage_path = package_info["subpackages"][get_platform()]
    validate_script_and_run(os.path.abspath(os.path.join(subpackage_path, install_script_name)), os.path.abspath(subpackage_path))

def get_package_name(folder):
    package_info = open(os.path.join(folder, "hail-info"), "r")
    for line in package_info:
        line = line.replace("\n", "").replace("\r", "")

        info = line.split("=")
        if info[0] == "name":
            return info[1]

def setup_hail():
    global hail_data_path

    home = os.path.expanduser("~")
    if get_platform() == "windows":
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
        print("Usage: " + sys.argv[0] + " <command> [file] [option string (starts with a +)]")
        exit(1) # Error
    if len(argv) > 3 and option_string == None or len(argv) > 4:
        print("Usage: " + sys.argv[0] + " <command> [file] [option string (starts with a +)]")
        exit(1) # Error
    
    if argv[1] == "package":
        if len(argv) < 3 or (option_string != None and len(argv) < 4):
            print("Expected a [file] argument for this command!")
            exit(1) # Error
        folder = argv[2]

        if folder[0] != "\\" and folder[0] != "/":
            folder = os.path.join("./", folder)
        print("Attempting to package folder " + folder + ".")

        # Validate package and zip it
        validate_package_and_exit_on_fail(folder)
        with zipfile.ZipFile(get_package_name(folder) + hail_pkg_ext, "w") as zf:
            paths = get_all_files(folder)
            for file in paths:
                zf.write(file)
    elif argv[1] == "unpack":
        if len(argv) < 3 or (option_string != None and len(argv) < 4):
            print("Expected a [file] argument for this command!")
            exit(1) # Error
        package = argv[2]

        if package[0] != "\\" and package[0] != "/":
            package = os.path.join("./", package)
        print("Attempting to unpackage " + package + ".")

        folder = ""

        try:
            with zipfile.ZipFile(package, "r") as zf:
                dirs = list(set([os.path.dirname(x) for x in zf.namelist()]))
                folder = [os.path.split(x)[0] for x in dirs][1]
                zf.extractall()
        except Exception as e:
            print("Package is not valid (Attempting extraction)!")
            print("Python error: " + str(e))
            exit(1) # Error

        validate_package_and_exit_on_fail(folder)
    elif argv[1] == "install":
        if len(argv) < 3 or (option_string != None and len(argv) < 4):
            print("Expected a [file] argument for this command!")
            exit(1) # Error
        package = argv[2]

        if package[0] != "\\" and package[0] != "/":
            package = os.path.join("./", package)
        print("Attempting to install " + package + ".")

        folder = ""
        try:
            with zipfile.ZipFile(package, "r") as zf:
                dirs = list(set([os.path.dirname(x) for x in zf.namelist()]))
                folder = [os.path.split(x)[0] for x in dirs]
                for f in folder:
                    if f != "":
                        folder = f
                        break
                zf.extractall()
        except Exception as e:
            print("Package is not valid (Attempting extraction)!")
            print("Python error: " + str(e))
            exit(1) # Error

        package_info = validate_package_and_exit_on_fail(folder)
        # print(package_info)
        install_package_and_exit_on_failure(folder, package_info)

main(sys.argv)
print("Hail done.")