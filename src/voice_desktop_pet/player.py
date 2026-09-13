"""Minimal Windows transparent frame-sequence desktop pet."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QAction, QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QMenu, QWidget

from .actions import ActionSpec, discover_actions, load_action_spec


class PetWindow(QWidget):
    FPS = 24
    ACTION_KEYS = {Qt.Key_1: "idle", Qt.Key_2: "listen", Qt.Key_3: "speak", Qt.Key_4: "wave"}

    def __init__(self, actions_dir: Path, scale: float = 1.0, initial_action: str = "idle") -> None:
        super().__init__()
        self.actions_dir, self.scale = actions_dir, max(0.1, min(scale, 3.0))
        self.action, self.frames, self.index = "idle", [], 0
        self.spec = ActionSpec(name="idle")
        self.drag_origin: QPoint | None = None
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.label = QLabel(self)
        self.label.setAttribute(Qt.WA_TranslucentBackground, True)
        self.label.setAlignment(Qt.AlignCenter)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_frame)
        self.set_action(initial_action)
        self.move_to_work_area()
        self.timer.start(self.spec.interval_ms)

    def move_to_work_area(self) -> None:
        screen = QApplication.primaryScreen()
        if screen:
            area = screen.availableGeometry()
            self.move(area.right() - self.width() - 32, area.bottom() - self.height() - 32)

    def set_action(self, action: str) -> None:
        action_dir = self.actions_dir / action
        frames = sorted(action_dir.glob("*.png"))
        if not frames:
            if action != "idle":
                self.set_action("idle")
            return
        self.spec = load_action_spec(action_dir)
        self.action, self.frames, self.index = action, [QPixmap(str(p)) for p in frames], 0
        self.timer.setInterval(self.spec.interval_ms)
        self.resize_to_frame()
        self.show_frame()

    def resize_to_frame(self) -> None:
        if self.frames:
            self.resize(self.frames[0].size() * self.scale)
            self.label.resize(self.size())

    def show_frame(self) -> None:
        if self.frames:
            pixmap = self.frames[self.index]
            if self.scale != 1.0:
                pixmap = pixmap.scaled(pixmap.size() * self.scale, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.label.setPixmap(pixmap)

    def next_frame(self) -> None:
        if self.frames:
            if self.index + 1 >= len(self.frames):
                if not self.spec.loop:
                    self.set_action(self.spec.return_to)
                    return
                self.index = 0
            else:
                self.index += 1
            self.show_frame()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton:
            self.drag_origin = event.globalPosition().toPoint() - self.pos()
        elif event.button() == Qt.RightButton:
            self.context_menu(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if self.drag_origin is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_origin)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton:
            self.drag_origin = None

    def keyPressEvent(self, event) -> None:  # noqa: N802
        if event.key() in self.ACTION_KEYS:
            self.set_action(self.ACTION_KEYS[event.key()])
        elif event.key() == Qt.Key_Space:
            self.timer.stop() if self.timer.isActive() else self.timer.start(round(1000 / self.FPS))
        elif event.key() == Qt.Key_Escape:
            self.close()

    def context_menu(self, position: QPoint) -> None:
        menu = QMenu(self)
        known_shortcuts = {action: key - Qt.Key_0 for key, action in self.ACTION_KEYS.items()}
        actions = discover_actions(self.actions_dir)
        for action in actions:
            shortcut = known_shortcuts.get(action)
            label = f"{shortcut}: {action}" if shortcut is not None else action
            item = QAction(label, menu)
            item.triggered.connect(lambda _checked=False, name=action: self.set_action(name))
            menu.addAction(item)
        menu.addSeparator()
        menu.addAction("退出", self.close)
        menu.exec(position)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--actions-dir", type=Path, default=Path("assets/actions"))
    parser.add_argument("--scale", type=float, default=1.0)
    parser.add_argument("--initial-action", default="idle")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Cycle through idle/listen/speak to demonstrate interaction states.",
    )
    args = parser.parse_args(argv)
    app = QApplication(sys.argv)
    window = PetWindow(args.actions_dir, args.scale, args.initial_action)
    window.show()
    if args.demo:
        demo_actions = [name for name in ("idle", "listen", "speak") if name in discover_actions(args.actions_dir)]
        if demo_actions:
            demo_index = 0
            demo_timer = QTimer(window)

            def advance_demo() -> None:
                nonlocal demo_index
                demo_index = (demo_index + 1) % len(demo_actions)
                window.set_action(demo_actions[demo_index])

            demo_timer.timeout.connect(advance_demo)
            demo_timer.start(4000)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
