import json
import tempfile
import unittest
from pathlib import Path

from voice_desktop_pet.actions import ActionSpec, discover_actions, load_action_spec


class ActionMetadataTests(unittest.TestCase):
    def test_legacy_action_uses_safe_defaults(self):
        with tempfile.TemporaryDirectory() as temporary:
            action_dir = Path(temporary) / "idle"
            action_dir.mkdir()
            (action_dir / "frame_0001.png").touch()

            self.assertEqual(load_action_spec(action_dir), ActionSpec(name="idle"))

    def test_metadata_controls_playback_policy(self):
        with tempfile.TemporaryDirectory() as temporary:
            action_dir = Path(temporary) / "wave"
            action_dir.mkdir()
            (action_dir / "metadata.json").write_text(
                json.dumps({"id": "wave", "fps": 12, "loop": False, "return_to": "idle"}),
                encoding="utf-8",
            )

            spec = load_action_spec(action_dir)
            self.assertEqual(spec.name, "wave")
            self.assertEqual(spec.interval_ms, 83)
            self.assertFalse(spec.loop)
            self.assertEqual(spec.return_to, "idle")

    def test_display_name_is_loaded(self):
        with tempfile.TemporaryDirectory() as temporary:
            action_dir = Path(temporary) / "listen"
            action_dir.mkdir()
            (action_dir / "metadata.json").write_text(
                json.dumps({"id": "listen", "display_name": "聆听"}), encoding="utf-8"
            )
            self.assertEqual(load_action_spec(action_dir).display_name, "聆听")

    def test_actions_follow_explicit_menu_order(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name, order in (("wave", 2), ("idle", 1)):
                action_dir = root / name
                action_dir.mkdir()
                (action_dir / "frame_0001.png").touch()
                (action_dir / "metadata.json").write_text(
                    json.dumps({"id": name, "menu_order": order}), encoding="utf-8"
                )
            self.assertEqual(discover_actions(root), ["idle", "wave"])

    def test_discover_actions_ignores_empty_directories(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "empty").mkdir()
            playable = root / "speak"
            playable.mkdir()
            (playable / "frame_0001.png").touch()

            self.assertEqual(discover_actions(root), ["speak"])


if __name__ == "__main__":
    unittest.main()
