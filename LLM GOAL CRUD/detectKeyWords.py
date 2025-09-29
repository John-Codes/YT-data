class DetectKWs:
    def __init__(self):
        self.goal = False
        self.task = False
        self.read = False
        self.update = False
        self.delete = False
        self.create = False

    def detect_crud(self, user_input):
        keywords = ['read', 'update', 'delete', 'create']
        for keyword in keywords:
            if keyword in user_input:
                setattr(self, keyword[:-1], True)

    def detect_goal(self, user_input):
        if 'goal' in user_input:
            self.goal = True

    def detect_task(self, user_input):
        if 'task' in user_input:
            self.goal = True

def detectKW(user_input):
    data = DetectKWs()
    data.detect_crud(user_input)
    data.detect_goal(user_input)
    data.detect_task(user_input)
    return {
        "goal": data.goal,
        "task": data.task,
        "read": data.read,
        "update": data.update,
        "delete": data.delete,
        "create": data.create
    }

if __name__ == "__main__":
    test_input = "This is a test input for the AI Function Manager LLM. It includes read and update operations."
    result = detectKW(test_input)
    print(f"Read: {result.read}, Update: {result.update}, Delete: {result.delete}, Create: {result.create}")
