from mongointerface import create_document, read_document, update_document, delete_document

class Task:
    def __init__(self, description):
        self.description = description
        self.todo = True
        self.pending = False
        self.done = False

class GoalManager:
    def __init__(self):
        self.long_term_goal = None
        self.tasks = []

    def set_long_term_goal(self, goal):
        self.long_term_goal = goal
        create_document("goals", {"type": "long_term", "goal": goal})

    def get_long_term_goal(self):
        documents = read_document("goals", {"type": "long_term"})
        if documents:
            self.long_term_goal = documents[0]["goal"]
        return self.long_term_goal

    def add_task(self, task):
        task_obj = Task(task)
        self.tasks.append(task_obj)
        create_document("tasks", {"description": task, "todo": True, "pending": False, "done": False})

    def get_tasks(self, status=None):
        if status is None:
            return self.tasks
        return [task for task in self.tasks if getattr(task, status)]

    def update_task_status(self, task_description, new_status):
        for task in self.tasks:
            if task.description == task_description:
                task.todo = False
                task.pending = False
                task.done = False
                setattr(task, new_status, True)
                update_document("tasks", {"description": task_description}, {"todo": task.todo, "pending": task.pending, "done": task.done})
                break

    def delete_task(self, task_description):
        for task in self.tasks:
            if task.description == task_description:
                self.tasks.remove(task)
                delete_document("tasks", {"description": task_description})
                break

if __name__ == "__main__":
    manager = GoalManager()
    
    # Test setting long-term goal
    manager.set_long_term_goal("Become a software engineer")
    print("Long-term goal:", manager.get_long_term_goal())
    
    # Test adding tasks
    manager.add_task("Learn Python")
    manager.add_task("Learn Git")
    print("All tasks:", [task.description for task in manager.get_tasks()])
    
    # Test updating task status
    manager.update_task_status("Learn Python", "done")
    print("Done tasks:", [task.description for task in manager.get_tasks("done")])
    print("Todo tasks after completion:", [task.description for task in manager.get_tasks("todo")])
    
    # Test updating task status to pending
    manager.update_task_status("Learn Git", "pending")
    print("Pending tasks:", [task.description for task in manager.get_tasks("pending")])
    
    # Test deleting a task
    manager.delete_task("Learn Git")
    print("All tasks after deletion:", [task.description for task in manager.get_tasks()])

    # Test reading tasks from the database
    tasks_from_db = read_document("tasks", {})
    print("Tasks from database:", [task["description"] for task in tasks_from_db])
