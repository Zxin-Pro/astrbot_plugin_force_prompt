# astrbot_plugin_force_prompt

强制在每个会话的 LLM 请求开头注入预设提示词的 [AstrBot](https://github.com/AstrBotDevs/AstrBot) 插件。

## 功能

- 在每次 LLM 请求发出前，将配置的提示词拼接到请求最前面
- 群聊 / 私聊可分别开关
- 可选用 `[]` 方括号包裹提示词以区分正文
- 配置热更新，面板改完即生效，无需重载插件
- 内置防重复注入机制（有界集合，防内存泄漏）

## 安装

将本仓库下载为 zip 后，在 AstrBot 面板「插件管理」中上传安装；或克隆到 `data/plugins/astrbot_plugin_force_prompt/` 目录。

## 配置

| 配置项 | 类型 | 默认 | 说明 |
|---|---|---|---|
| enabled | bool | true | 总开关 |
| force_prompt | string | 空 | 注入的提示词内容，留空则不注入 |
| wrap_in_brackets | bool | true | 用 `[]` 包裹提示词 |
| apply_to_groups | bool | true | 是否对群聊生效 |
| apply_to_private | bool | true | 是否对私聊生效 |

## 许可

MIT License
