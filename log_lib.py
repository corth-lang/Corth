import subprocess

import enum_lib


def log(type_, message):
    print(f"[{type_}] {message}")

        
def command(command):
    log("CMD", command)

    try:
        process = subprocess.run(command)

    except KeyboardInterrupt:
        log("INFO", "Interrupted while executing command")

    except Exception as e:
        log("ERROR", f"Unhandled error; {type(e)} '{e}'")

    else:
        if process.returncode:
            log("ERROR", f"Command returned non-zero return code; got {process.returncode}")

        else:
            log("INFO", "Successfully executed command")

