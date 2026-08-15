from collections.abc import Callable
import re

from config import BotConfig
from db import ForumMessage, ResponseType
from market_data import MarketQuote, fetch_market_quote


class ResponseGenerator:
    def __init__(
        self,
        config: BotConfig,
        quote_fetcher: Callable[[str], MarketQuote] = fetch_market_quote,
    ):
        self.config = config
        self.quote_fetcher = quote_fetcher

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
        if command == "quote":
            return self._generate_quote_response(params)

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
        commands = " | ".join(
            f"{self.config.command_symbol}{command.name} - {command.description}"
            for command in self.config.valid_commands
        )
        return f"Available commands: {commands}"

    def _generate_quote_response(self, params: list[str]) -> str:
        if len(params) != 1 or not re.fullmatch(r"[A-Za-z0-9.^=-]{1,20}", params[0]):
            return f"Usage: {self.config.command_symbol}quote TICKER"

        ticker = params[0].upper()
        try:
            quote = self.quote_fetcher(ticker)
        except Exception as error:
            print(f"Quote lookup failed for {ticker}: {error}", flush=True)
            return f"Quote unavailable for {ticker}."

        change = quote.price - quote.previous_close
        percent_change = change / quote.previous_close * 100
        indicator = "📈 " if change > 0 else "📉 " if change < 0 else ""

        return (
            f"{indicator}{quote.ticker} — ${quote.price:.2f} "
            f"{self._format_signed_currency(change)} ({percent_change:+.2f}%) | "
            f"O: ${quote.open:.2f} H: ${quote.high:.2f} "
            f"L: ${quote.low:.2f} Vol: {self._format_volume(quote.volume)}"
        )

    @staticmethod
    def _format_signed_currency(value: float) -> str:
        sign = "+" if value >= 0 else "-"
        return f"{sign}${abs(value):.2f}"

    @staticmethod
    def _format_volume(volume: int) -> str:
        for threshold, suffix in (
            (1_000_000_000_000, "T"),
            (1_000_000_000, "B"),
            (1_000_000, "M"),
            (1_000, "K"),
        ):
            if volume >= threshold:
                return f"{volume / threshold:.1f}{suffix}"
        return str(volume)
