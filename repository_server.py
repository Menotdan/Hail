import packer
import packages
import repositories
import installer
import os
import socket
import shutil
import time

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 9977))
    s.listen(10)
    conn = None

    try:
        while True:
            conn,_ = s.accept()
            
            string = repositories.read_data(conn)
            time.sleep(0.1)
            print("Got request with string = " + string + ".")
            if string == "list":
                packages_list = []
                files = os.listdir("packages")
                os.chdir("packages")
                for f in files:
                    folder = packer.extract_package(f)
                    info = packages.check_package(folder)
                    packages_list.append((info["name"], info["version"]))
                    shutil.rmtree(folder) # Delete the extracted package

                to_send = ""
                for p in packages_list:
                    to_send += p[0] + "*" + p[1] + "&"
                conn.send(repositories.get_data_send(to_send))
                conn.close()
                os.chdir("../")
            elif string[:4] == "down":
                package_name = string[4:] + ".hpkg"
                if package_name in os.listdir("packages"):
                    fp = open(os.path.join("packages", package_name), "rb")
                    to_send = repositories.struct.pack("!I", os.path.getsize(os.path.join("packages", package_name)))
                    to_send = to_send + fp.read()
                    conn.sendall(to_send)
            else:
                print("Bruh!!1")
                print(string)
    except Exception as e:
        print("Exception!")
        print(str(e))
        try:
            s.close()
        except:
            print("Failed to close server socket.")
            pass

        try:
            conn.close()
        except:
            print("Failed to close client socket.")
            pass
        exit(1)
                
main()