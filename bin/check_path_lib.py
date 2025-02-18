from pathlib import Path

def check_path(inipath):
    ini_file = Path(inipath)
    if ini_file.exists() == False:
        print('File not exists.')
        exit(1)