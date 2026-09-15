"""SillyTavern (酒馆) 预设与提示词编排数据模型 (DTO)。

包含采样物理参数、提示词流水线条目、排序规则与前后端交互契约。

Usage:
    >>> from app.schemas.tavern import TavernPresetConfig, TavernPromptItem
    >>> config = TavernPresetConfig(...)
"""

from typing import Any, Literal
from pydantic import BaseModel, Field


class TavernPromptItem(BaseModel):
    """单个提示词流水线条目。"""

    identifier: str = Field(description="条目唯一标识符 (UUID 或系统锚点名)")
    name: str = Field(description="条目展示名称")
    role: str = Field(default="system", description="消息角色")
    content: str = Field(default="", description="提示词模板正文内容")
    system_prompt: bool = Field(default=True, description="是否作为系统级指令")
    marker: bool = Field(default=False, description="是否为内置动态插桩锚点 (如 Persona/Char/WorldInfo)")
    enabled: bool = Field(default=True, description="该条目是否启用")
    injection_position: int = Field(default=0, description="插入位置 (0=相对, 1=聊天中)")
    injection_depth: int = Field(default=4, description="插入深度 (当选择聊天中时生效)")
    injection_trigger: list[str] = Field(default_factory=list, description="生效触发器列表 (为空表示所有类型默认)")
    forbid_overrides: bool = Field(default=False, description="是否禁止覆盖")


class TavernPromptOrderItem(BaseModel):
    """流水线排序项。"""

    identifier: str = Field(description="条目唯一标识符")
    enabled: bool = Field(default=True, description="启用状态")
    is_unordered_backup: bool = Field(
        default=False, description="是否为未在原流水线编排中的备选条目"
    )


class TavernRegexScript(BaseModel):
    """单个酒馆正则脚本 (1:1 对齐 SillyTavern extensions.regex_scripts)。

    Usage:
        >>> script = TavernRegexScript(
        ...     id="51b3f4a5-ee72-4980-abda-8d8fb67479be",
        ...     scriptName="【云瑾】包裹最新指示",
        ...     findRegex=r"^([\\s\\S]*)$",
        ...     replaceString="<最新互动>\\n$1\\n</最新互动>",
        ...     placement=[1],
        ...     maxDepth=1,
        ... )
    """

    id: str = Field(description="正则唯一标识符 UUID")
    scriptName: str = Field(description="正则脚本名称")
    findRegex: str = Field(description="查找正则表达式 (支持纯正则或 JS 风格 /pattern/flags)")
    replaceString: str = Field(default="", description="替换目标文本 (支持 $1, $2 反向引用)")
    trimStrings: list[str] = Field(default_factory=list, description="修剪掉的字符列表")
    placement: list[int] = Field(
        default_factory=lambda: [2],
        description="生效时机: 1=用户输入, 2=AI输出, 3=快捷命令, 4=世界书, 5=推理",
    )
    disabled: bool = Field(default=False, description="是否禁用")
    markdownOnly: bool = Field(default=False, description="仅影响显示 (表层替换)")
    promptOnly: bool = Field(default=True, description="仅影响后端提示词")
    runOnEdit: bool = Field(default=True, description="在编辑时运行")
    substituteRegex: int = Field(default=0, description="查找时的宏代换模式 (0=不替换)")
    minDepth: int | None = Field(default=None, description="最小生效消息深度")
    maxDepth: int | None = Field(default=None, description="最大生效消息深度")


# 别名兼容
RegexScript = TavernRegexScript


class TavernAdvancedFormatting(BaseModel):
    """酒馆高级格式化与生成后处理配置 (Advanced Formatting)。

    1:1 借鉴酒馆高级格式化体系，包含推理思维链治理、历史后置指令、自定义终止词、文本清洗流水线与回复前缀引导。

    Usage:
        >>> fmt = TavernAdvancedFormatting(
        ...     parse_think_tags=True,
        ...     reasoning_history_depth=0,
        ...     enable_post_history_instruction=True,
        ...     post_history_instruction="[System: 请保持当前性格与语气，继续剧情]",
        ...     stop_sequences=["\\nUser:", "<|eot_id|>"],
        ... )
    """

    # 1. 推理与思维链 (Reasoning & CoT)
    parse_think_tags: bool = Field(
        default=True,
        description="自动解析并剥离 <think> 与 <thinking> 标签，解耦正文与思考过程",
    )
    reasoning_history_depth: int = Field(
        default=0,
        ge=0,
        le=10,
        description="回传给后续上下文的历史思考链条数 (0表示完全不回传，大幅节省Token与避免思维干扰)",
    )
    auto_expand_reasoning: bool = Field(
        default=False,
        description="前端渲染对话气泡时默认是否自动展开思维链折叠面板",
    )

    # 2. 历史后置指令 (Post-History Instruction / 近因效应人设强化)
    enable_post_history_instruction: bool = Field(
        default=False,
        description="是否在多轮对话历史末端再次注入 System 强化提示词 (解决长文本人设遗忘与崩皮套)",
    )
    post_history_instruction: str = Field(
        default="",
        description="后置强化指令正文模板 (支持宏代换，如 {{char}}, {{user}})",
    )
    post_history_depth: int = Field(
        default=0,
        ge=0,
        le=10,
        description="后置强化指令注入深度 (0为末尾最后一条消息之后，1为倒数第一条之前)",
    )

    # 3. 自定义终止字符串 (Stop Sequences)
    stop_sequences: list[str] = Field(
        default_factory=list,
        description="自定义终止字符串列表 (透传给底层大模型 API 的 stop 参数)",
    )
    char_name_as_stop: bool = Field(
        default=False,
        description="是否自动将角色名换行作为终止词 (防止模型冒充角色自我重复)",
    )
    user_name_as_stop: bool = Field(
        default=False,
        description="是否自动将用户名换行作为终止词 (防止模型伪造玩家发言自言自语)",
    )

    # 4. 文本修剪与清洗流水线 (Text Cleaning Pipeline)
    collapse_newlines: bool = Field(
        default=True,
        description="折叠 3 个以上连续多余换行符收敛为双换行",
    )
    trim_incomplete_sentences: bool = Field(
        default=False,
        description="截断时修剪未闭合的不完整句子至末尾最后一个有效标点",
    )
    trim_whitespace: bool = Field(
        default=True,
        description="修剪输出文本首尾多余空白字符",
    )

    # 5. 回复引导 (Assistant Prefill)
    reply_prefix: str = Field(
        default="",
        description="以...开始回复 (Assistant Prefill 引导词，如动作引导符 '*')",
    )
    show_reply_prefix: bool = Field(
        default=True,
        description="是否在前端气泡中显式呈现该回复前缀",
    )


class TavernPresetConfig(BaseModel):
    """完整的酒馆生成预设与提示词编排配置。"""

    preset_name: str = Field(default="仓鼠之神V2", description="预设名称")
    is_active: bool = Field(default=True, description="当前用户是否激活该酒馆预设")

    # 1. 采样物理参数
    temperature: float = Field(default=1.0, ge=0.0, le=2.0, description="采样温度")
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0, description="频率惩罚")
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0, description="存在惩罚")
    top_p: float = Field(default=1.0, ge=0.0, le=1.0, description="核采样阈值")
    top_k: int = Field(default=0, ge=0, description="Top K 采样")
    top_a: float = Field(default=1.0, ge=0.0, description="Top A 采样")
    min_p: float = Field(default=0.0, ge=0.0, le=1.0, description="Min P 采样")
    repetition_penalty: float = Field(default=1.0, description="重复惩罚")

    # 2. 上下文与物理限制
    max_context_unlocked: bool = Field(default=True, description="解锁上下文上限")
    openai_max_context: int = Field(default=2000000, description="上下文最大 Token 数")
    openai_max_tokens: int = Field(default=32000, description="最大回复 Token 数")
    stream_openai: bool = Field(default=True, description="是否启用流式传输")
    seed: int = Field(default=-1, description="随机数种子 (-1 表示真随机)")
    reasoning_effort: Literal["low", "medium", "high", "auto"] = Field(default="high", description="思维链推理强度")
    squash_system_messages: bool = Field(default=False, description="是否压缩合并系统消息")

    # 3. 提示词条目库与排序
    prompts: list[TavernPromptItem] = Field(default_factory=list, description="全部提示词条目清单")
    prompt_order: list[TavernPromptOrderItem] = Field(default_factory=list, description="提示词流水线先后执行顺序")

    # 4. 正则脚本引擎 (1:1 SillyTavern extensions.regex_scripts)
    regex_scripts: list[TavernRegexScript] = Field(default_factory=list, description="全部预设正则脚本清单")

    # 5. 高级格式化与后处理
    advanced_formatting: TavernAdvancedFormatting = Field(
        default_factory=TavernAdvancedFormatting,
        description="高级格式化与生成后处理配置",
    )


class TavernPresetUpdateRequest(BaseModel):
    """更新酒馆预设请求体。"""

    is_active: bool | None = None
    temperature: float | None = None
    frequency_penalty: float | None = None
    presence_penalty: float | None = None
    top_p: float | None = None
    max_context_unlocked: bool | None = None
    openai_max_context: int | None = None
    openai_max_tokens: int | None = None
    stream_openai: bool | None = None
    seed: int | None = None
    reasoning_effort: Literal["low", "medium", "high", "auto"] | None = None
    prompts: list[TavernPromptItem] | None = None
    prompt_order: list[TavernPromptOrderItem] | None = None
    regex_scripts: list[TavernRegexScript] | None = None
    advanced_formatting: TavernAdvancedFormatting | None = None


class TavernPresetSummary(BaseModel):
    """预设摘要简报。"""

    preset_name: str = Field(description="预设名称")
    is_builtin: bool = Field(default=False, description="是否为官方内置预设")
    temperature: float = Field(description="采样温度")
    top_p: float = Field(description="核采样")
    prompts_count: int = Field(description="条目总数")
    active_prompts_count: int = Field(description="激活条目数")
