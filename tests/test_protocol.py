import unittest
from pathlib import Path


class ProtocolDocumentationTests(unittest.TestCase):
    def test_action_directories_are_documented(self):
        text = Path("assets/actions/README.md").read_text(encoding="utf-8")
        for action in ("idle", "listen", "wave", "speak"):
            self.assertIn(f"{action}/frame_0001.png", text)


if __name__ == "__main__":
    unittest.main()
