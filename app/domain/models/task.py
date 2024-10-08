class Task:
    _title: str
    _description: str
    _status: str
    _tags: set[str]
    
    def __init__(self, *, title: str, description: str, status: str, tags: list[str] | None = None):
        if not tags:
            tags = set()
        
        self._title = title
        self._description = description
        self._status = status
        self._tags = tags

    @property
    def title(self):
        return self._title

    @property
    def description(self):
        return self._description

    @property
    def status(self):
        return self._status
    
    @property
    def tags(self):
        return self._tags
