from .task import Task

class Context:
    _name: str
    _statuses: set[str]
    _tasks: list[Task]
    
    def __init__(self, *, name: str, statuses: list[str] | None = None, tasks: list[Task] | None = None):
        if not statuses:
            statuses = set()
        
        if not tasks:
            tasks = []
            
        self._name = name
        self._statuses = statuses
        self._tasks = tasks
    
    @property
    def name(self):
        return self._name
    
    @property
    def statuses(self):
        return self._statuses
    
    @property
    def tasks(self):
        return self._tasks
    
    def add_status(self, *, status: str):
        self._statuses.add(status)
    
    def delete_status(self, *, status: str):
        self._statuses.remove(status)
    
    def add_task(self, *, task: Task):
        self._tasks.append(task)
    
    def delete_task(self, *, task: Task):
        self._tasks.remove(task)