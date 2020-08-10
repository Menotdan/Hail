import os
import sys
import shutil
import packer
import packages
import repositories

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

def check_version1_greater(version1, version2):
    ver_str1 = version1.split(".")
    ver_parts1 = []

    ver_str2 = version2.split(".")
    ver_parts2 = []

    ver_states = []

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

def install_package_and_exit_on_failure(folder, package_info, installed_from_repo):
    if not get_platform() in package_info["platforms"]:
        print("This package does not support the current platform! (" + get_platform() + ")!")
        if installed_from_repo: # Remove if installed from repository
            os.remove(package_info["name"])
            shutil.rmtree(folder)
        exit(1) # Error

    for d in package_info["dependencies"]:
        print("Package " + package_info["name"] + " depends on " + d[0] + ".")
        install_package(d[0], d[0], hail_data_path)

    if check_if_package_installed(package_info["name"]):
        if not check_package_version_greater(package_info["name"], package_info["version"]):
            print("Package already installed!")
            if installed_from_repo: # Remove if installed from repository
                os.remove(package_info["name"])
                shutil.rmtree(folder)
            exit(1) # Error
            
        else:
            change_version_number_installed_package(package_info["name"], package_info["version"])
    else:
        add_package_installed(package_info["name"], package_info["version"])


    install_script_name = package_info["install_scripts"][get_platform()]
    subpackage_path = package_info["subpackages"][get_platform()]
    validate_script_and_run(os.path.abspath(os.path.join(subpackage_path, install_script_name)), os.path.abspath(subpackage_path))

def install_package(package, package_name, hail_path):
    global hail_data_path
    hail_data_path = hail_path
    installed_from_repo = False

    print("Installing package " + package_name + ".")

    if not os.path.isfile(package):
        # Download from a repository
        print("Package file not found! Attempting to install from a repository.")
        best_repo = ""
        best_version = ""
        for repo in os.listdir(os.path.join(hail_data_path, "repo")):
            fp = open(os.path.join(hail_data_path, "repo", repo), "r")
            for l in fp:
                l = l.replace("\r", "").replace("\n", "")
                if l != "":
                    info = l.split(" - ")
                    if info[0] == package_name:
                        if best_version == "":
                            best_repo = repo
                            best_version = info[1]
                        else:
                            if check_version1_greater(info[1], best_version):
                                best_repo = repo
                                best_version = info[1]
            fp.close()
        if best_repo == "":
            print("No repository has this package!")
            exit(1) # Error

        try:
            package = repositories.download_package(best_repo, package_name)
        except:
            print("Downloading package from repository failed! Package not installed.")
            exit(1) # Error
        installed_from_repo = True
    folder = ""
    try:
        folder = packer.extract_package(package)
    except Exception as e:
        print("Package is not valid (Attempting extraction)!")
        print("Python error: " + str(e))
        exit(1) # Error
        

    package_info = packages.check_package(folder)
    install_package_and_exit_on_failure(folder, package_info, installed_from_repo)

    if installed_from_repo: # Remove if installed from repository
        os.remove(package)
        shutil.rmtree(folder)