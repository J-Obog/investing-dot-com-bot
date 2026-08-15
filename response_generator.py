from config import BotConfig
from db import ForumMessage, ResponseType


class ResponseGenerator:
    def __init__(self, config: BotConfig):
        self.config = config

    def generate_response(
        self,
        message: ForumMessage,
        response_type: ResponseType,
    ) -> str:
        if response_type is ResponseType.COMMAND:
            return self._generate_command_response(message)

        return "Hey, I've been watching this stock too!"

    def _generate_command_response(self, message: ForumMessage) -> str:
        command, params = self._extract_command(message)

        if command == "help":
            return self._generate_help_response()

        return f"Unknown command: {self.config.command_symbol}{command}"

    def _extract_command(self, message: ForumMessage) -> tuple[str, list[str]]:
        _, content_after_mention = message.content.split(
            self.config.at_bot,
            maxsplit=1,
        )
        command_text = content_after_mention.strip()
        if command_text.startswith(self.config.command_symbol):
            command_text = command_text[len(self.config.command_symbol):]

        parts = command_text.split()
        if not parts:
            return "", []

        return parts[0].casefold(), parts[1:]

    def _generate_help_response(self) -> str:
        commands = "\n".join(
            f"{self.config.command_symbol}{command.name} - {command.description}"
            for command in self.config.valid_commands
        )
        return f"Available commands:\n{commands}"
