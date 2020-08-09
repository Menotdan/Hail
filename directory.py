import os

def get_all_files(directory):
    paths = []
    for root, _, files in os.walk(directory):
        for f_name in files:
            path = os.path.join(root, f_name)
            paths.append(path)
    return paths