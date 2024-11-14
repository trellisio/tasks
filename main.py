import sys

from app.entrypoints.server.fastapi import listen as fastapi_listen

if __name__ == "__main__":
    entrypoint = sys.argv[1]
    match entrypoint:
        case "fastapi":
            fastapi_listen()
        case _:
            msg = "Unknown entrypoint"
            raise ValueError(msg)
