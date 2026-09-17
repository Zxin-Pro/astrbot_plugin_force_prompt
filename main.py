import asyncio
from typing import Any, Set

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register


@register(
    "astrbot_plugin_force_prompt",
    "Zxin-Pro",
    "强制在每个会话的 LLM 请求开头注入预设提示词",
    "v1.0.0",
)
class ForcePromptPlugin(Star):
    """
    astrbot_plugin_force_prompt 主类。

    功能：在每次 LLM 请求发出前，把配置中的 force_prompt 拼接到
    请求提示词的最前面，实现"强制提示词"效果。

    特性：
    1. 支持群聊 / 私聊分别开关；
    2. 可选用 [] 方括号包裹提示词以作区分；
    3. 配置支持热更新（每次请求都重新读取配置，改完即生效，无需重载插件）；
    4. 内置防重复注入机制（基于 id(req) 的有界集合，防止内存泄漏）。
    """

    # 防重复集合的最大容量上限，超出后清理最旧记录，防止长期运行内存泄漏
    MAX_INJECTED_SET_SIZE = 512

    def __init__(self, context: Context, config: Any = None):
        super().__init__(context)
        # config 由 AstrBot 加载器自动注入（来自 _conf_schema.json）
        self.config = config
        # 记录已注入过的 req 对象 id（id(req) 在对象存活期内唯一）
        self._injected_ids: Set[int] = set()
        logger.info("astrbot_plugin_force_prompt v1.0.0 已加载")

    async def terminate(self):
        """插件卸载/停用时清理资源"""
        self._injected_ids.clear()
        logger.info("astrbot_plugin_force_prompt 已卸载，注入记录已清空")

    def _get_conf(self) -> dict:
        """
        读取当前生效配置。

        优先尝试 context.get_config()（每次请求时实时读取，天然支持热更新），
        若其中不含本插件的配置项，则回退到加载器注入的 self.config。
        这样无论部署在哪个 AstrBot 版本上都能拿到最新配置。
        """
        try:
            conf = self.context.get_config()
            if conf is not None and "force_prompt" in conf:
                return conf
        except Exception:
            pass
        return self.config if self.config is not None else {}

    @filter.on_llm_request()
    async def on_llm_request(self, event: AstrMessageEvent, req):
        """
        LLM 请求钩子：在请求真正发给模型前执行。

        - req: ProviderRequest 对象，其中 req.prompt 即本次请求的提示词。
        - 判断群聊/私聊是否允许注入 -> 拼接提示词 -> 防重复。
        """
        try:
            conf = self._get_conf()

            # 1. 总开关检查
            if not bool(conf.get("enabled", True)):
                return

            # 2. 提示词为空则无事可做
            force_prompt = str(conf.get("force_prompt", "") or "").strip()
            if not force_prompt:
                return

            # 3. 防重复注入：同一 req 对象只注入一次
            #    （Agent 循环 / 工具调用等场景下 req 可能被多次传入钩子）
            req_id = id(req)
            if req_id in self._injected_ids:
                return
            # 有界集合：超过上限时清空重记（记录只是"去重"用途，清空不影响正确性）
            if len(self._injected_ids) >= self.MAX_INJECTED_SET_SIZE:
                self._injected_ids.clear()
            self._injected_ids.add(req_id)

            # 4. 会话类型判断：群聊 / 私聊
            #    get_group_id() 群聊返回群号，私聊返回 None / 空串
            group_id = event.get_group_id()
            is_group = bool(group_id)

            if is_group and not bool(conf.get("apply_to_groups", True)):
                return
            if not is_group and not bool(conf.get("apply_to_private", True)):
                return

            # 5. 拼接提示词：按配置决定是否用 [] 包裹
            if bool(conf.get("wrap_in_brackets", True)):
                prompt_prefix = f"[{force_prompt}]"
            else:
                prompt_prefix = force_prompt

            original = req.prompt or ""
            req.prompt = f"{prompt_prefix} {original}".strip()

            logger.debug(
                f"[force_prompt] 已注入提示词（会话类型={'群聊' if is_group else '私聊'}，"
                f"群号={group_id}，长度={len(force_prompt)}）"
            )
        except Exception as e:
            # 任何异常都不应阻断正常 LLM 请求流程
            logger.error(f"[force_prompt] 注入提示词时出错: {e}")
