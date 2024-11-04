class InvalidStatusError(Exception):
    def __init__(self, *, status: str):
        super().__init__(f"Invalid status {status}")


class ArchivedStatusError(Exception):
    def __init__(self):
        super().__init__("Cannot remove the archived status")
