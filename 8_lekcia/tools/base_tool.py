"""
Base Tool class — all tools inherit from this.
"""

from abc import ABC, abstractmethod


class BaseTool(ABC):
    """
    Every tool must define:
    - name: unique identifier used in the ReAct loop
    - description: explains to the LLM what this tool does and when to use it
    - input_schema: dict describing expected parameters
    - run(inputs): executes the tool and returns a string result
    """

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def input_schema(self) -> dict:
        pass

    @abstractmethod
    def run(self, inputs: dict) -> str:
        pass
