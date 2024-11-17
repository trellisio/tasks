import sys

if __name__ == "__main__":
    entrypoint = sys.argv[1]
    match entrypoint:
        case "fastapi":
            from app.entrypoints.server.fastapi import listen as fastapi_listen

            fastapi_listen()
        case "graphql":
            from app.entrypoints.server.graphql import listen as graphql_listen

            graphql_listen()
        case _:
            msg = "Unknown entrypoint"
            raise ValueError(msg)
