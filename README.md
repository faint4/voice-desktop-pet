# Voice Desktop Pet

基于 [DesktopGirls](https://github.com/xing133/DesktopGirls) 验证的 Windows 语音桌宠实验项目。

第一阶段目标：让一个透明、置顶的视频人物在 Windows 桌面上运行，并通过明确的动作状态接口切换待机、聆听、思考、说话和情绪动作。聊天、TTS、语音输入和更复杂的动作包会以独立 Issue / Pull Request 递进实现。

## 当前范围

- Windows 桌面透明视频窗口
- 始终置顶、无边框、可拖动
- 视频动作资源按状态切换
- 先用本地按钮 / 快捷键模拟事件
- 后续接入语音识别、LLM、TTS

## 文档

- [开发与测试计划](docs/DEVELOPMENT_PLAN.md)
- [动作协议](docs/ACTION_PROTOCOL.md)
- [MVP 验收清单](docs/MVP_ACCEPTANCE.md)

## 相关项目

- [DesktopGirls](https://github.com/xing133/DesktopGirls)：视频桌宠窗口验证基线
- [TonyNa-code/desktop-pet](https://github.com/TonyNa-code/desktop-pet/)：聊天、角色包、TTS 设计参考
- [desktop-mascot-mcp](https://github.com/rennosuke-haresu/desktop-mascot-mcp)：语音、表情、动作协议参考

## 开发原则

先保证桌面窗口和动作状态稳定，再接入外部服务。所有模型输出必须经过白名单动作协议，不能直接执行任意系统命令。
