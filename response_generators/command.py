import math
import re

import yfinance as yf

from config import BotConfig

US_INDICES = (
    ("SPX", "^GSPC"),
    ("NDX", "^NDX"),
    ("DJI", "^DJI"),
    ("RUT", "^RUT"),
)


class CommandResponseGenerator:
    def __init__(self, config: BotConfig):
        self.config = config

    def generate(self, content: str) -> str:
        command, params = self._extract_command(content)

        if command == "help":
            return self._generate_help_response()
        if command == "quote":
            return self._generate_quote_response(params)
        if command == "indices":
            return self._generate_indices_response(params)

        return f"Unknown command: {self.config.command_symbol}{command}"

    def _extract_command(self, content: str) -> tuple[str, list[str]]:
        _, content_after_mention = content.split(
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
            info = yf.Ticker(ticker).fast_info
            price = float(info.last_price)
            previous_close = float(info.previous_close)
            open_price = float(info.open)
            high = float(info.day_high)
            low = float(info.day_low)
            volume = float(info.last_volume)

            values = (price, previous_close, open_price, high, low, volume)
            if not all(math.isfinite(value) for value in values):
                raise ValueError("Incomplete market data")
            if previous_close == 0:
                raise ValueError("Invalid previous close")
        except Exception as error:
            print(f"Quote lookup failed for {ticker}: {error}", flush=True)
            return f"Quote unavailable for {ticker}."

        change = price - previous_close
        percent_change = change / previous_close * 100
        indicator = "📈 " if change > 0 else "📉 " if change < 0 else ""

        return (
            f"{indicator}{ticker} — ${price:.2f} "
            f"{self._format_signed_currency(change)} ({percent_change:+.2f}%) | "
            f"O: ${open_price:.2f} H: ${high:.2f} "
            f"L: ${low:.2f} Vol: {self._format_volume(int(volume))}"
        )

    def _generate_indices_response(self, params: list[str]) -> str:
        if params:
            return f"Usage: {self.config.command_symbol}indices"

        indices = []
        try:
            for name, ticker in US_INDICES:
                info = yf.Ticker(ticker).fast_info
                price = float(info.last_price)
                previous_close = float(info.previous_close)
                if not math.isfinite(price) or not math.isfinite(previous_close):
                    raise ValueError(f"Incomplete market data for {ticker}")
                if previous_close == 0:
                    raise ValueError(f"Invalid previous close for {ticker}")

                percent_change = (price - previous_close) / previous_close * 100
                indicator = (
                    "🟢" if percent_change > 0
                    else "🔴" if percent_change < 0
                    else "⚪"
                )
                indices.append(f"{name} {indicator} {percent_change:+.2f}%")
        except Exception as error:
            print(f"Index lookup failed: {error}", flush=True)
            return "Index data is currently unavailable."

        return f"🇺🇸 {' | '.join(indices)}"

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
