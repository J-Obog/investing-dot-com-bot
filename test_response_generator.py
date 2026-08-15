import unittest

from config import BotConfig
from db import ForumMessage, ResponseType
from market_data import MarketQuote
from response_generator import ResponseGenerator


class QuoteResponseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = BotConfig(
            at_bot="$Hedgey",
            command_symbol="!",
            valid_commands=[],
            visible_forums=[],
        )

    def test_formats_gain(self) -> None:
        quote = MarketQuote(
            ticker="NVDA",
            price=182.41,
            previous_close=179.31,
            open=179.82,
            high=183.20,
            low=178.91,
            volume=142_300_000,
        )
        generator = ResponseGenerator(self.config, lambda ticker: quote)
        message = ForumMessage(
            id="1",
            company_id="8181",
            user_id="2",
            username="tester",
            parent_id=None,
            content="$Hedgey !quote nvda",
            created_at=0,
        )

        response = generator.generate_response(message, ResponseType.COMMAND)

        self.assertEqual(
            response,
            "📈 NVDA — $182.41 +$3.10 (+1.73%) | "
            "O: $179.82 H: $183.20 L: $178.91 Vol: 142.3M",
        )

    def test_formats_loss(self) -> None:
        quote = MarketQuote(
            ticker="NVDA",
            price=176.21,
            previous_close=179.31,
            open=179.82,
            high=180.20,
            low=175.91,
            volume=950_000,
        )
        generator = ResponseGenerator(self.config, lambda ticker: quote)

        response = generator._generate_quote_response(["NVDA"])

        self.assertTrue(response.startswith("📉 NVDA — $176.21 -$3.10 (-1.73%)"))
        self.assertTrue(response.endswith("Vol: 950.0K"))

    def test_requires_one_valid_ticker(self) -> None:
        generator = ResponseGenerator(self.config)

        self.assertEqual(
            generator._generate_quote_response([]),
            "Usage: !quote TICKER",
        )
        self.assertEqual(
            generator._generate_quote_response(["NVDA", "AAPL"]),
            "Usage: !quote TICKER",
        )


if __name__ == "__main__":
    unittest.main()
