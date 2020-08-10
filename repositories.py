import socket
import struct
import time

def get_data_send(string):
    return struct.pack("!I", len(string)) + string.encode("ASCII")

def read_data(s):
    length = s.recv(4)
    length = struct.unpack("!I", length)
    buf = b""
    while len(buf) < length[0]:
        buf += s.recv(1024)
    string = buf.decode("ASCII")
    return string

def get_package_list(repository_addr):
    packages = []
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((repository_addr, 9977))
    s.sendall(get_data_send("list"))
    string = read_data(s)
    stuff = string.split("&")

    packages = []
    for s in stuff:
        info = s.split("*")
        if s != "":
            print(info[0] + " version " + info[1])
            packages.append((info[0], info[1]))
    return packages

def download_package(repository_addr, package):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((repository_addr, 9977))
    s.sendall(get_data_send("down" + package))

    length = s.recv(4)
    length = struct.unpack("!I", length)
    buf = b""
    while len(buf) < length[0]:
        buf += s.recv(1024)
    
    fp = open(package + ".hpkg", "wb")
    fp.write(buf)
    fp.close()
    return package + ".hpkg"