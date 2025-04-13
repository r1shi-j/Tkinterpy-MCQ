import os
from config import SETTINGS_FILE_PATH

def read_setting() -> str:
    make_file_if_doesnt_exist()
    with open(SETTINGS_FILE_PATH, "r") as file:
        return file.read()

def write_setting(new_value: str):
    make_file_if_doesnt_exist()
    with open(SETTINGS_FILE_PATH, "w") as file:
        file.write(new_value)

def make_file_if_doesnt_exist():
    if not os.path.exists(SETTINGS_FILE_PATH):
        with open(SETTINGS_FILE_PATH, "w") as file:
            pass

def is_first_run() -> bool:
    if read_setting() == "True":
        return False
    else:
        return True
    
def has_run_now():
    write_setting("True")