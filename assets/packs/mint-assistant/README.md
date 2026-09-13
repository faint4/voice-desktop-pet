# Mint Assistant 动作包

该动作包以同一角色母图为身份参考生成独立姿态，并经过本地 U2Net 抠像。右键菜单按以下顺序显示中文名称和协议 ID：

```text
actions/
├── idle/       # 待机：循环
├── listen/     # 聆听：循环
├── think/      # 思考：循环
├── speak/      # 说话：循环
├── nod/        # 点头：单次
├── wave/       # 挥手：单次
├── happy/      # 开心：单次
├── surprised/  # 惊讶：单次
├── confused/   # 疑惑：单次
├── comfort/    # 安慰：单次
└── goodbye/    # 告别：单次
```

动作帧规格：360×640、RGBA PNG、24 FPS。每个目录中的 `metadata.json` 描述循环和回退策略。

重新生成：

```powershell
.\desktopgirls-source\.venv\Scripts\python.exe tools\generate_motion_pack.py `
  --master assets\characters\mint-assistant\master.png `
  --poses-dir assets\characters\mint-assistant\poses-rgba `
  --output assets\packs\mint-assistant\actions
```

运行自动演示：

```powershell
uv run python -m voice_desktop_pet.player `
  --actions-dir assets\packs\mint-assistant\actions `
  --initial-action idle `
  --demo
```
