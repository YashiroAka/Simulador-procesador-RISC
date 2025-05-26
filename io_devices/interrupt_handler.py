
class InterruptHandler:
    def __init__(self):
        self.interrupt_queue = []

    def trigger(self, interrupt):
        self.interrupt_queue.append(interrupt)

    def handle_next(self):
        if self.interrupt_queue:
            interrupt = self.interrupt_queue.pop(0)
            print(f"Manejando interrupción: {interrupt}")
            return interrupt
        return None
