import unittest

from forum import ForumPostResponse


class ForumPostResponseTests(unittest.TestCase):
    def test_parses_post_response(self) -> None:
        response = ForumPostResponse.from_dict({"status": "Approved"})

        self.assertEqual(response.status, "Approved")


if __name__ == "__main__":
    unittest.main()
