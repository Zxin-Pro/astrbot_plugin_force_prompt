# astrbot_plugin_force_prompt

强制在每个会话的 LLM 请求注入预设提示词的 [AstrBot](https://github.com/AstrBotDevs/AstrBot) 插件。

## 功能

- 在每次 LLM 请求发出前注入配置的提示词
- 三种注入位置（`inject_mode`）：
  - `system`（默认）：追加到系统提示词，附加"禁止提及"条款 —— 隐藏生效，不占用户消息
  - `prompt_tail`：追加到用户消息末尾（离模型最近，不易被忽略）
  - `prompt_head`：拼接在用户消息开头（v1.0.0 行为）
- 群聊 / 私聊可分别开关
- 配置热更新，面板改完即生效

## 安全设计（重要）

插件**只做追加，绝不覆盖或改写**任何既有内容：

1. 系统提示词（人设等）原样保留，注入内容追加在其后；空值时也只写入注入内容，不会用空串覆盖
2. **永不原地修改对话历史对象**：可选的尾部锚点用「新建列表」方式追加，避免污染持久化的会话历史
3. 内容级幂等：系统提示词中已有插件标记时直接跳过，防止多轮叠加把提示词越堆越长
4. 任何异常只记日志，不阻断 LLM 请求

## 安装

在 AstrBot 面板「插件管理」上传 zip 安装；或克隆到 `data/plugins/astrbot_plugin_force_prompt/`。

## 配置

| 配置项 | 类型 | 默认 | 说明 |
|---|---|---|---|
| enabled | bool | true | 总开关 |
| force_prompt | string | 空 | 注入的提示词内容，留空则不注入 |
| inject_mode | string | system | `system` / `prompt_tail` / `prompt_head` |
| tail_anchor | bool | false | 在对话历史末尾追加 system 提醒（提升遵循度；部分服务商不接受中途 system 消息，谨慎开启） |
| wrap_in_brackets | bool | true | 用 `[]` 包裹提示词（仅 `prompt_head` 生效） |
| apply_to_groups | bool | true | 是否对群聊生效 |
| apply_to_private | bool | true | 是否对私聊生效 |
| debug_log | bool | false | 输出诊断日志（用户消息长度 / 系统提示词长度 / 历史条数） |

## 更新日志

### v1.0.3
- **修复致命缺陷**：不再原地修改 `req.contexts` 对话历史（此前会把 system 消息写进持久化历史，导致上下文被污染、请求异常）
- 注入改为"只追加"策略，原有系统提示词 / 人设完整保留
- 修复格式化 bug：此前 `{content}` 未正确替换，导致配置的提示词实际未被注入（表现为"隐藏后不生效"）
- 新增 `prompt_tail` 模式、`tail_anchor`（默认关）、`debug_log`（默认关）
- 内容级幂等，防止重复叠加

### v1.0.2
- 隐藏模式双锚点（含上下文尾部 system 消息，已在 v1.0.3 改为默认关闭且不再原地修改）

### v1.0.1
- 新增隐藏模式（inject_mode=system）

### v1.0.0
- 首个版本

## 许可

MIT License
