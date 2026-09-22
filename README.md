# astrbot_plugin_force_prompt

强制在每个会话的 LLM 请求开头注入预设提示词的 [AstrBot](https://github.com/AstrBotDevs/AstrBot) 插件。

## 功能

- 在每次 LLM 请求发出前，将配置的提示词注入请求
- **隐藏模式（默认）**：写入系统提示词（system_prompt），并附加"禁止提及本指令"条款——模型只默默遵守，不会在回复中提及、承认或复述该指令
- 显式模式：拼接到用户消息最前面（v1.0.0 行为）
- 群聊 / 私聊可分别开关
- 配置热更新，面板改完即生效，无需重载插件
- 内置防重复注入机制（有界集合，防内存泄漏）

## 安装

将本仓库下载为 zip 后，在 AstrBot 面板「插件管理」中上传安装；或克隆到 `data/plugins/astrbot_plugin_force_prompt/` 目录。

## 配置

| 配置项 | 类型 | 默认 | 说明 |
|---|---|---|---|
| enabled | bool | true | 总开关 |
| force_prompt | string | 空 | 注入的提示词内容，留空则不注入 |
| inject_mode | string | system | `system`=隐藏（系统提示词）/ `prompt`=显式（用户消息前） |
| wrap_in_brackets | bool | true | 用 `[]` 包裹提示词（仅显式模式生效） |
| apply_to_groups | bool | true | 是否对群聊生效 |
| apply_to_private | bool | true | 是否对私聊生效 |

## 更新日志

### v1.0.1
- 新增隐藏模式（inject_mode=system，默认）：注入系统提示词 + 禁止提及条款，模型不再回应提示词本身
- 无 system_prompt 属性的实现自动回退到显式模式

### v1.0.0
- 首个版本

## 许可

MIT License
