from pathlib import Path


def test_action_directories_are_documented():
    text = Path("assets/actions/README.md").read_text(encoding="utf-8")
    for action in ("idle", "listen", "wave", "speak"):
        assert f"{action}/frame_0001.png" in text
