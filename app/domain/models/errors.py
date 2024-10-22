class InvalidStatus(Exception):
    def __init__(self, *, status: str):
        super().__init__(f"Invalid status {status}")
