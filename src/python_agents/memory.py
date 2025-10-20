from abc import ABC, abstractmethod
from python_agents.message import Message


class BaseMemory(ABC):
    @abstractmethod
    def add_message(self, message: Message):
        pass

    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def insert_system_message(self, message: Message):
        pass


class SimpleMemory(BaseMemory):
    def __init__(self):
        self.messages = []

    def add_message(self, message: Message):
        self.messages.append(message)

    def insert_system_message(self, message: Message):
        if len(self.messages) > 0:
            if self.messages[0]["role"] == "system":
                self.messages[0] = message
            else:
                self.messages.insert(0, message)
        else:
            self.messages = [message]

    def clear(self):
        """Clear the memory."""
        self.messages = []
