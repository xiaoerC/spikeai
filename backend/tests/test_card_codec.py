"""SillyTavern V2/V3 角色卡与 PNG tEXt 编解码器自动化测试套件 (TDD)。

测试涵盖：
1. 从标准 PNG 二进制读取 SillyTavern V2 与 V3 角色卡；
2. 将角色卡数据嵌入 PNG tEXt 'chara' Chunk 并确保无损回读；
3. 支持叙梦 Naro 专属扩展属性 (extensions.naro_prologue_html 等)；
4. 容错与异常边界测试 (非 PNG 格式、缺失 chara 块、损坏 Base64、非法 JSON 等)；
5. 标准 V2/V3 角色卡数据与 Naro 领域模型双向互转。

Usage:
    $ uv run pytest tests/test_card_codec.py -v
"""

import json
from io import BytesIO
from typing import Any

import pytest
from PIL import Image

from app.schemas.character import CharacterCreateRequest, STV2Card, STV3Card
from app.services.card_codec_service import CardCodecService


@pytest.fixture
def blank_png_bytes() -> bytes:
    """生成一张 100x100 纯色测试 PNG 图像字节流。"""
    img = Image.new("RGBA", (100, 100), color=(30, 20, 15, 255))
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def sample_v2_payload() -> dict[str, Any]:
    """生成合法的 SillyTavern V2 角色卡数据字典。"""
    return {
        "name": "艾莉丝·冯·罗兰",
        "description": "帝国皇家魔法学院的首席研究员，精通时空重构法术。",
        "personality": "高傲、严谨，但在面对信任之人时偶尔展现傲娇萌态。",
        "scenario": "学院地下禁忌图书馆，深夜。",
        "first_mes": "（合上手中的羊皮卷轴，抬头望向你）这么晚了，你来禁书区做什么？",
        "mes_example": "<START>\n{{user}}: 我想查阅时空魔法。\n{{char}}: 哼，区区学徒也妄想碰触禁忌吗？",
        "creator_notes": "叙梦官方出品，支持分支剧情探索。",
        "system_prompt": "以第一人称进行沉浸式互动，严格遵循二次元语气风格。",
        "post_history_instructions": "时刻注意当前所处的时间和地点设定。",
        "alternate_greetings": [
            "（正在专注调试水晶魔杖，没有注意到你的靠近）",
            "你终于来了，我等你很久了。"
        ],
        "tags": ["西幻", "魔法", "傲娇", "学院"],
        "creator": "叙梦创作组",
        "character_version": "1.2.0",
        "character_book": {
            "name": "罗兰帝国秘典",
            "entries": [
                {
                    "keys": ["禁忌图书馆", "禁书区"],
                    "content": "学院地下三百米处的神秘区域，封印着上古时空卷轴。",
                    "constant": False,
                    "position": "after_char",
                }
            ]
        },
        "extensions": {
            "naro_prologue_html": "<h2>序幕：星辉之夜</h2><p>魔导纪元742年，宿命的钟声敲响。</p>",
            "naro_variables": {
                "variable_1": "好感度: 15",
                "variable_2": "魔力值: 100"
            }
        }
    }


@pytest.fixture
def sample_v3_payload(sample_v2_payload: dict[str, Any]) -> dict[str, Any]:
    """生成合法的 SillyTavern V3 角色卡数据字典。"""
    return {
        "spec": "chara_card_v3",
        "spec_version": "3.0",
        "data": {
            **sample_v2_payload,
            "assets": [
                {"type": "icon", "uri": "https://example.com/icon.png"}
            ]
        }
    }


class TestCardCodecService:
    """角色卡编解码服务测试集。"""

    def test_embed_and_extract_v2_png(
        self,
        blank_png_bytes: bytes,
        sample_v2_payload: dict[str, Any],
    ) -> None:
        """测试将 V2 角色卡注入 PNG 图像并成功无损提取。"""
        # 1. 注入元数据
        tagged_png = CardCodecService.embed_character_into_png(
            image_bytes=blank_png_bytes,
            card_data=sample_v2_payload,
        )
        assert len(tagged_png) > len(blank_png_bytes)

        # 2. 提取并验证
        extracted_card = CardCodecService.extract_card_from_png(tagged_png)
        assert isinstance(extracted_card, STV2Card)
        assert extracted_card.data.name == "艾莉丝·冯·罗兰"
        assert extracted_card.data.personality == "高傲、严谨，但在面对信任之人时偶尔展现傲娇萌态。"
        assert len(extracted_card.data.alternate_greetings) == 2
        assert "西幻" in extracted_card.data.tags
        assert extracted_card.data.extensions.get("naro_prologue_html") == (
            "<h2>序幕：星辉之夜</h2><p>魔导纪元742年，宿命的钟声敲响。</p>"
        )

    def test_embed_and_extract_v3_png(
        self,
        blank_png_bytes: bytes,
        sample_v3_payload: dict[str, Any],
    ) -> None:
        """测试将 V3 角色卡注入 PNG 图像并成功提取为 STV3Card。"""
        tagged_png = CardCodecService.embed_character_into_png(
            image_bytes=blank_png_bytes,
            card_data=sample_v3_payload,
        )

        extracted_card = CardCodecService.extract_card_from_png(tagged_png)
        assert isinstance(extracted_card, (STV2Card, STV3Card))
        assert extracted_card.data.name == "艾莉丝·冯·罗兰"
        assert extracted_card.data.creator == "叙梦创作组"

    def test_parse_json_string(self, sample_v2_payload: dict[str, Any]) -> None:
        """测试直接从 JSON 字符串反序列化角色卡。"""
        json_str = json.dumps(sample_v2_payload, ensure_ascii=False)
        card = CardCodecService.parse_card_from_json(json_str)

        assert card.data.name == "艾莉丝·冯·罗兰"
        assert card.data.first_mes.startswith("（合上手中")

    def test_convert_to_character_create_request(
        self,
        sample_v2_payload: dict[str, Any],
    ) -> None:
        """测试将标准 SillyTavern 角色卡转换为叙梦内部创建请求对象。"""
        card = STV2Card(data=sample_v2_payload)
        create_req = CardCodecService.to_character_create_request(
            card=card,
            avatar_url="https://example.com/avatar.png",
            category="story",
        )

        assert isinstance(create_req, CharacterCreateRequest)
        assert create_req.name == "艾莉丝·冯·罗兰"
        assert create_req.avatar_url == "https://example.com/avatar.png"
        assert create_req.category == "story"
        assert create_req.prologue_html.startswith("<h2>序幕：星辉之夜</h2>")
        assert len(create_req.worldbooks) == 1
        assert create_req.worldbooks[0].keys == ["禁忌图书馆", "禁书区"]

    def test_convert_db_character_to_st_card(self) -> None:
        """测试将内部角色实体数据转换为可对外导出的标准 ST 角色卡。"""
        mock_char_data = {
            "name": "夜刀神十香",
            "description": "拥有紫水晶般长发与眼眸的精灵少女。",
            "personality": "天真烂漫，极度热爱美食。",
            "scenario": "天宫市废墟。",
            "first_mes": "你也是来杀我的吗？",
            "alternate_greetings": ["肚子好饿...有黄豆粉面包吗？"],
            "system_prompt": "二次元动漫轻小说对话风格。",
            "post_history_instructions": "保持纯真可爱的语气。",
            "prologue_title": "序章·精灵降临",
            "prologue_html": "<p>空间震警报拉响之时...</p>",
            "tags": ["约战", "二次元", "精灵"],
            "version": "1.0.0",
        }

        st_card = CardCodecService.export_to_st_card(mock_char_data, creator_name="橘公司")
        assert st_card.spec == "chara_card_v2"
        assert st_card.data.name == "夜刀神十香"
        assert st_card.data.creator == "橘公司"
        assert st_card.data.extensions["naro_prologue_html"] == "<p>空间震警报拉响之时...</p>"

    def test_error_missing_chara_metadata(self, blank_png_bytes: bytes) -> None:
        """测试当 PNG 文件没有 chara 元数据时抛出精确异常。"""
        with pytest.raises(ValueError, match="未包含 SillyTavern 'chara' 元数据块"):
            CardCodecService.extract_card_from_png(blank_png_bytes)

    def test_error_corrupted_png(self) -> None:
        """测试非法/损坏字节流时抛出异常。"""
        corrupted_bytes = b"NOT_A_PNG_FILE_CONTENT"
        with pytest.raises(ValueError, match="图像格式损坏或非有效 PNG"):
            CardCodecService.extract_card_from_png(corrupted_bytes)

    def test_error_corrupted_base64(self, blank_png_bytes: bytes) -> None:
        """测试当 chara 文本块存在但不是有效 Base64 时的防御处理。"""
        img = Image.open(BytesIO(blank_png_bytes))
        from PIL import PngImagePlugin
        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("chara", "!!!INVALID_BASE64_PAYLOAD!!!")
        out = BytesIO()
        img.save(out, format="PNG", pnginfo=pnginfo)

        with pytest.raises(ValueError, match="解析角色卡 Base64/JSON 失败"):
            CardCodecService.extract_card_from_png(out.getvalue())
