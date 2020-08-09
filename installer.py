import os
import sys
import packer
import packages

hail_data_path = ""

def get_platform():
    p = sys.platform
    if p == "linux" or p == "linux2":
        return "linux"
    if p == "win32":
        return "windows"
    if p == "darwin":
        return "mac"

def validate_script_and_run(script_path, script_cwd):
    with open(script_path, "r") as _:
        # Check script for weird things
        pass
    old_cwd = os.getcwd()
    os.chdir(script_cwd)
    os.system(script_path)
    os.chdir(old_cwd)

def check_package_version_greater(package_name, package_version):
    ver_str1 = package_version.split(".")
    ver_parts1 = []

    ver_str2 = None
    ver_parts2 = []

    ver_states = []
    
    fp = open(os.path.join(hail_data_path, "installed-packages"), "r")
    for l in fp:
        l = l.replace("\n", "").replace("\r", "")
        info = l.split(" - ")
        if info[0] == package_name:
            ver_str2 = info[1].split(".")
            break
    fp.close()

    for v in ver_str1:
        ver_parts1.append(int(v))
    for v in ver_str2:
        ver_parts2.append(int(v))
    
    for i in range(len(ver_str1)):
        if ver_parts1[i] > ver_parts2[i]:
            ver_states.append(0) # Greater
        if ver_parts1[i] == ver_parts2[i]:
            ver_states.append(1) # Equal
        if ver_parts1[i] < ver_parts2[i]:
            ver_states.append(2) # Lesser
    
    all_equal = True
    for s in ver_states:
        if s == 2:
            return False
        if s != 1:
            all_equal = False
    
    if all_equal == True:
        return False
    return True

def add_package_installed(package_name, version):
    fp = open(os.path.join(hail_data_path, "installed-packages"), "a")
    fp.write(package_name + " - " + version + "\n")
    fp.close()

def change_version_number_installed_package(package_name, version):
    fp = open(os.path.join(hail_data_path, "installed-packages"), "r")
    packages = fp.read().replace("\r", "").split("\n")
    for i in range(len(packages)):
        if packages[i].split(" - ")[0] == package_name:
            packages[i] = package_name + " - " + version
    fp.close()
    
    fp = open(os.path.join(hail_data_path, "installed-packages"), "w")
    fp.write('\n'.join(packages))
    fp.close()

def check_if_package_installed(package_name):
    fp = open(os.path.join(hail_data_path, "installed-packages"), "r")
    for l in fp:
        l = l.replace("\n", "").replace("\r", "")
        info = l.split(" - ")
        if info[0] == package_name:
            fp.close()
            return True
    fp.close()
    return False

def install_package_and_exit_on_failure(folder, package_info):
    if not get_platform() in package_info["platforms"]:
        print("This package does not support the current platform! (" + get_platform() + ")!")
        exit(1) # Error
        

    if check_if_package_installed(package_info["name"]):
        if not check_package_version_greater(package_info["name"], package_info["version"]):
            print("Package already installed!")
            exit(1) # Error
            
        else:
            change_version_number_installed_package(package_info["name"], package_info["version"])
    else:
        add_package_installed(package_info["name"], package_info["version"])

    install_script_name = package_info["install_scripts"][get_platform()]
    subpackage_path = package_info["subpackages"][get_platform()]
    validate_script_and_run(os.path.abspath(os.path.join(subpackage_path, install_script_name)), os.path.abspath(subpackage_path))

def install_package(package, hail_path):
    global hail_data_path
    hail_data_path = hail_path
    folder = ""
    try:
        folder = packer.extract_package(package)
    except Exception as e:
        print("Package is not valid (Attempting extraction)!")
        print("Python error: " + str(e))
        exit(1) # Error
        

    package_info = packages.check_package(folder)
    install_package_and_exit_on_failure(folder, package_info)