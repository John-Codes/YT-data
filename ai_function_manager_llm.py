class LLMFunctionData:
    def __init__(self):
        self.task = False
        self.read = False
        self.update = False
        self.delete = False
        self.create = False

    def detect_crud(self, user_input):
        keywords = ['read*', 'update*', 'delete*', 'create*']
        for keyword in keywords:
            if keyword in user_input:
                setattr(self, keyword[:-1], True)

    def detect_task(self, user_input):
        if 'task*' in user_input:
            self.task = True

def main(user_input):
    data = LLMFunctionData()
    data.detect_crud(user_input)
    data.detect_task(user_input)
    return data

if __name__ == "__main__":
    test_input = "This is a test input for the AI Function Manager LLM. It includes read and update operations."
    result = main(test_input)
    print(f"Read: {result.read}, Update: {result.update}, Delete: {result.delete}, Create: {result.create}")
