"""SillyTavern 正则脚本引擎 (Regex Scripts) 单元测试。

验证:
1. 出厂预设包含 9 项预设正则脚本;
2. JS 风格正则表达式 (/pattern/flags) 与 $1, $2 反向引用正确转换为 Python 正则;
3. Placement 1 (用户输入包裹 <最新互动>) 在 depth=1 时准确触发;
4. Placement 2 (AI 输出清洗) 标签抹除、八股抹除与标点规范准确触发;
5. disabled 与深度 (minDepth, maxDepth) 过滤机制有效。

Usage:
    uv run pytest tests/test_tavern_regex.py -v
"""

import pytest

from app.schemas.tavern import TavernRegexScript
from app.services.tavern_service import TavernService


def test_default_preset_loads_regex_scripts():
    """验证出厂默认预设是否成功加载 9 项正则脚本。"""
    preset = TavernService.get_default_preset()
    assert len(preset.regex_scripts) >= 9

    names = [s.scriptName for s in preset.regex_scripts]
    assert "【云瑾】包裹最新指示" in names
    assert "【云瑾】移除额外tag_1.5" in names
    assert "【云瑾】八股抹除 - 4.24" in names
    assert "【夏瑾】破折号处理" in names


def test_parse_js_regex_basic_and_flags():
    """验证 JS 正则表达式解析及标志位识别。"""
    # 纯正则表达式
    res1 = TavernService.parse_js_regex(r"^([\s\S]*)$", "<tag>\n$1\n</tag>")
    assert res1 is not None
    compiled1, repl1 = res1
    assert repl1 == "<tag>\n\\g<1>\n</tag>"
    assert compiled1.sub(repl1, "hello") == "<tag>\nhello\n</tag>"

    # 带 /pattern/flags 格式
    res2 = TavernService.parse_js_regex(r"/hello/i", "world")
    assert res2 is not None
    compiled2, repl2 = res2
    assert compiled2.sub(repl2, "HELLO there") == "world there"


def test_placement_1_user_input_wrap():
    """验证 Placement 1 用户输入包裹规则 (深度仅限 1)。"""
    script = TavernRegexScript(
        id="test-wrap",
        scriptName="【云瑾】包裹最新指示",
        findRegex=r"^([\s\S]*)$",
        replaceString="<最新互动>\n$1\n</最新互动>",
        placement=[1],
        disabled=False,
        maxDepth=1,
    )

    # depth=1 生效
    out1 = TavernService.execute_regex_scripts(
        text="请继续写下去",
        scripts=[script],
        placement=1,
        depth=1,
    )
    assert out1 == "<最新互动>\n请继续写下去\n</最新互动>"

    # depth=2 不生效
    out2 = TavernService.execute_regex_scripts(
        text="前文互动",
        scripts=[script],
        placement=1,
        depth=2,
    )
    assert out2 == "前文互动"


def test_placement_2_tag_and_cliche_removal():
    """验证 Placement 2 AI 输出清洗：标签剥离与八股抹除。"""
    preset = TavernService.get_default_preset()
    scripts = preset.regex_scripts

    dirty_output = (
        "<-begin-response->我将进行符合需求的创作：\n"
        "<thinking>内部思考</thinking>\n"
        "她难以察觉地微微皱眉，这是不可否认的一个动作——随后轻声道：好的。"
    )

    cleaned = TavernService.execute_regex_scripts(
        text=dirty_output,
        scripts=scripts,
        placement=2,
    )

    # 验证内部标签被剔除
    assert "<-begin-response->" not in cleaned
    assert "我将进行符合需求的创作：" not in cleaned
    assert "<thinking>" not in cleaned
    # 验证破折号被替换为逗号
    assert "——" not in cleaned
    assert "，随后轻声道：好的。" in cleaned


def test_disabled_scripts_are_ignored():
    """验证 disabled 状态的正则脚本不会被执行。"""
    script = TavernRegexScript(
        id="disabled-script",
        scriptName="禁用测试",
        findRegex=r"bad",
        replaceString="good",
        placement=[2],
        disabled=True,
    )
    res = TavernService.execute_regex_scripts(
        text="this is bad",
        scripts=[script],
        placement=2,
    )
    assert res == "this is bad"


def test_placement_999_runs_on_ai_output():
    """验证酒馆生态特有的 placement=[999] 脚本在 placement=2 (AI输出/问候清洗) 时能够正常触发。"""
    script = TavernRegexScript(
        id="clean-initvar",
        scriptName="清理初始化变量",
        findRegex=r"/<initvar>[\s\S]*?<\/initvar>/gmi",
        replaceString="",
        placement=[999],
        disabled=False,
    )

    dirty_text = (
        "<initvar>\n"
        "{\n"
        '  "世界": {"时间": "清晨"}\n'
        "}\n"
        "</initvar>\n"
        "这是真正的角色对白正文。"
    )

    cleaned = TavernService.execute_regex_scripts(
        text=dirty_text,
        scripts=[script],
        placement=2,
    )

    assert "<initvar>" not in cleaned
    assert "这是真正的角色对白正文。" in cleaned


def test_js_replacer_handles_bad_escapes_without_crashing():
    """验证包含 JS/HTML 特有正则字符 (如 \\s, \\d, \\w) 的 replaceString 不会触发 Python bad escape 异常。"""
    script = TavernRegexScript(
        id="render-html-card",
        scriptName="渲染地点卡",
        findRegex=r"/(<SceneHeaderPlaceHolder\s*\/>)/gm",
        replaceString=(
            "```html\n"
            "<script>\n"
            "const regex = /\\s+/g;\n"
            "const num = /\\d+/;\n"
            "</script>\n"
            "<div class=\"hz-card\">木叶废墟: $1</div>\n"
            "```"
        ),
        placement=[999],
        disabled=False,
    )

    raw_text = "前言 <SceneHeaderPlaceHolder/> 结语"
    cleaned = TavernService.execute_regex_scripts(
        text=raw_text,
        scripts=[script],
        placement=2,
    )

    assert '<div class="hz-card">木叶废墟: <SceneHeaderPlaceHolder/></div>' in cleaned
    assert "const regex = /\\s+/g;" in cleaned

