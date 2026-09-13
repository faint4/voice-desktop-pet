# Mint Assistant 动作包

该动作包由同一张透明角色母图生成，因此角色身份、服装和轮廓在动作之间保持一致。

```text
actions/
├── idle/    # 待机呼吸循环，4 秒
├── listen/  # 聆听循环，3 秒
└── speak/   # 说话身体节奏循环，3 秒
```

动作帧规格：360×640、RGBA PNG、24 FPS。每个目录中的 `metadata.json` 描述循环和回退策略。

重新生成：

```powershell
.\desktopgirls-source\.venv\Scripts\python.exe tools\generate_motion_pack.py `
  --master assets\characters\mint-assistant\master.png `
  --output assets\packs\mint-assistant\actions
```

运行自动演示：

```powershell
uv run python -m voice_desktop_pet.player `
  --actions-dir assets\packs\mint-assistant\actions `
  --initial-action idle `
  --demo
```
