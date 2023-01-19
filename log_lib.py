import subprocess

import enum_lib


def log(type_, message):
    print(f"[{type_}] {message}")

        
def command(command):
    log("CMD", command)
    subprocess.run(command)

