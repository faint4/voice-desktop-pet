# Voice Desktop Pet

基于 [DesktopGirls](https://github.com/xing133/DesktopGirls) 验证的 Windows 语音桌宠实验项目。

第一阶段目标：让一个透明、置顶的视频人物在 Windows 桌面上运行，并通过明确的动作状态接口切换待机、聆听、思考、说话和情绪动作。聊天、TTS、语音输入和更复杂的动作包会以独立 Issue / Pull Request 递进实现。

## 当前范围

- Windows 桌面透明视频窗口
- 始终置顶、无边框、可拖动
- 视频动作资源按状态切换
- 先用本地按钮 / 快捷键模拟事件
- 后续接入语音识别、LLM、TTS

## M1 本地运行

需要 Windows 10/11、Python 3.11+ 和透明 PNG 帧。先准备 `assets/actions` 下的动作目录，然后执行：

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -e .
py -m voice_desktop_pet.player --actions-dir assets/actions
```

快捷键：`1` 待机、`2` 聆听、`3` 说话、`4` 挥手；空格暂停/恢复；`Esc` 退出。左键拖动，右键打开动作菜单。

## M2.1 AI 角色演示

项目包含原创的 Mint Assistant 透明角色母图，以及以该角色为身份参考生成的完整动作包。右键菜单可对照预览待机、聆听、思考、说话、点头、挥手、开心、惊讶、疑惑、安慰和告别。双击 `tools/run-mint-demo.cmd`，或执行：

```powershell
uv run python -m voice_desktop_pet.player `
  --actions-dir assets\packs\mint-assistant\actions `
  --initial-action idle `
  --demo
```

演示会每四秒自动切换 `idle → listen → speak`。也可以按 `1`、`2`、`3` 手动切换，按空格暂停或恢复，按 `Esc` 退出。

## 文档

- [开发与测试计划](docs/DEVELOPMENT_PLAN.md)
- [M2.1 AI 角色与核心动作](docs/M2_1_AI_CHARACTER.md)
- [M2.2 完整动作包与右键菜单](docs/M2_2_FULL_ACTION_PACK.md)
- [动作协议](docs/ACTION_PROTOCOL.md)
- [MVP 验收清单](docs/MVP_ACCEPTANCE.md)

## 相关项目

- [DesktopGirls](https://github.com/xing133/DesktopGirls)：视频桌宠窗口验证基线
- [TonyNa-code/desktop-pet](https://github.com/TonyNa-code/desktop-pet/)：聊天、角色包、TTS 设计参考
- [desktop-mascot-mcp](https://github.com/rennosuke-haresu/desktop-mascot-mcp)：语音、表情、动作协议参考

## 开发原则

先保证桌面窗口和动作状态稳定，再接入外部服务。所有模型输出必须经过白名单动作协议，不能直接执行任意系统命令。
