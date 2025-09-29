"""Input/Output abstractions for PassBrief."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Optional, Protocol


class IOInterface(Protocol):
    """Protocol for interactive input/output channels."""

    def prompt(self, message: str, default: Optional[str] = None) -> str:
        """Prompt the user for input and return the response."""

    def confirm(self, message: str, default: bool = False) -> bool:
        """Ask for a yes/no confirmation and return the decision."""

    def info(self, message: str) -> None:
        """Emit an informational message to the user."""

    def warning(self, message: str) -> None:
        """Emit a warning message to the user."""

    def error(self, message: str) -> None:
        """Emit an error message to the user."""


@dataclass
class ConsoleIO(IOInterface):
    """Console-backed implementation using ``input`` and ``print``."""

    stream: object = sys.stdout

    def prompt(self, message: str, default: Optional[str] = None) -> str:
        suffix = f" [{default}]" if default is not None else ""
        response = input(f"{message}{suffix}: ").strip()
        return response if response else (default or "")

    def confirm(self, message: str, default: bool = False) -> bool:
        default_token = "Y/n" if default else "y/N"
        response = input(f"{message} ({default_token}): ").strip().lower()
        if not response:
            return default
        return response in {"y", "yes"}

    def info(self, message: str) -> None:
        print(message, file=self.stream)

    def warning(self, message: str) -> None:
        print(message, file=self.stream)

    def error(self, message: str) -> None:
        print(message, file=self.stream)
