import os

def get_package_name(folder):
    package_info = open(os.path.join(folder, "hail-info"), "r")
    for line in package_info:
        line = line.replace("\n", "").replace("\r", "")

        info = line.split("=")
        if info[0] == "name":
            return info[1]

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

def check_package(folder):
    returned_info = {}
    platforms = []
    dependencies = []
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
        elif info[0] == "depends":
            if len(info) != 2:
                print("Invalid package configuration!")
                print("Missing a key or value on line " + str(linec) + "!")
                exit(1) # Error
                
            for d in info[1].split(","):
                name_ver = d.split("/")
                dependencies.append(name_ver)
        elif info[0] == "version":
            if len(info) != 2:
                print("Invalid package configuration!")
                print("Missing a key or value on line " + str(linec) + "!")
                exit(1) # Error
                
            returned_info["version"] = info[1]
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
    returned_info["dependencies"] = dependencies

    try:
        _ = returned_info["name"]
    except:
        print("Package missing name!")
        exit(1) # Error
        
    
    try:
        _ = returned_info["version"]
    except:
        print("Package missing version!")
        exit(1) # Error
        

    return returned_info