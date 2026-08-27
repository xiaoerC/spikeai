"""SillyTavern V2 与 V3 角色卡与 PNG tEXt/iTXt 元数据无损编解码领域服务。

遵循酒馆生态标准协议规范，支持无损读取、注入 PNG 图片元数据，并在 SillyTavern 与
叙梦 Naro 角色模型之间实现双向平滑转换。

Usage:
    >>> from app.services.card_codec_service import CardCodecService
    >>> card = CardCodecService.extract_card_from_png(png_bytes)
    >>> tagged_png = CardCodecService.embed_character_into_png(raw_png_bytes, card)
"""

import base64
import json
import logging
from io import BytesIO
from typing import Any

from PIL import Image, PngImagePlugin, UnidentifiedImageError

from app.schemas.character import (
    CharacterCreateRequest,
    STV2Card,
    STV2Data,
    STV3Card,
    WorldBookEntryDTO,
)

logger = logging.getLogger(__name__)


class CardCodecService:
    """SillyTavern 角色卡编解码与转换核心服务。"""

    @classmethod
    def extract_card_from_png(cls, image_bytes: bytes) -> STV2Card | STV3Card:
        """从 PNG 图片二进制字节流中提取 SillyTavern 角色卡数据。

        Args:
            image_bytes: PNG 图像原始字节流。

        Returns:
            STV2Card | STV3Card: 解析并校验后的 SillyTavern 标准角色卡实例。

        Raises:
            ValueError: 图像非有效 PNG、缺少 'chara' 元数据块或 JSON 解析失败时抛出。

        Usage:
            >>> with open("character.png", "rb") as f:
            >>>     card = CardCodecService.extract_card_from_png(f.read())
        """
        try:
            with Image.open(BytesIO(image_bytes)) as img:
                raw_b64: str | None = None

                # 优先读取 text 属性 (tEXt / iTXt)
                if hasattr(img, "text") and isinstance(img.text, dict):
                    raw_b64 = img.text.get("chara") or img.text.get("ccv3")

                # 兜底读取 info 字典
                if not raw_b64 and hasattr(img, "info") and isinstance(img.info, dict):
                    raw_b64 = img.info.get("chara") or img.info.get("ccv3")

                if not raw_b64:
                    raise ValueError("PNG 文件中未包含 SillyTavern 'chara' 元数据块")

                try:
                    json_bytes = base64.b64decode(raw_b64)
                    raw_dict: dict[str, Any] = json.loads(json_bytes.decode("utf-8"))
                except Exception as e:
                    logger.error("Base64 反序列化角色卡失败: %s", e)
                    raise ValueError(f"解析角色卡 Base64/JSON 失败: {e}") from e

                return cls._dict_to_card(raw_dict)

        except UnidentifiedImageError as e:
            logger.error("无法识别图像格式: %s", e)
            raise ValueError(f"图像格式损坏或非有效 PNG: {e}") from e
        except ValueError:
            raise
        except Exception as e:
            logger.exception("提取角色卡过程中发生未知异常")
            raise ValueError(f"图像格式损坏或非有效 PNG: {e}") from e

    @classmethod
    def embed_character_into_png(
        cls,
        image_bytes: bytes,
        card_data: dict[str, Any] | STV2Card | STV3Card,
    ) -> bytes:
        """将角色卡 JSON 数据经过 Base64 编码后注入到 PNG 的 'chara' tEXt 元数据块中。

        Args:
            image_bytes: 原始 PNG 图像字节流。
            card_data: 待嵌入的角色卡数据 (支持 dict、STV2Card 或 STV3Card)。

        Returns:
            bytes: 包含隐写角色卡元数据的无损 PNG 图像字节流。

        Raises:
            ValueError: 图像处理或编码失败时抛出。

        Usage:
            >>> tagged_png = CardCodecService.embed_character_into_png(raw_png, card_data)
        """
        try:
            # 序列化为规范 dict
            if isinstance(card_data, (STV2Card, STV3Card)):
                payload = card_data.model_dump()
            else:
                payload = card_data

            json_str = json.dumps(payload, ensure_ascii=False)
            b64_str = base64.b64encode(json_str.encode("utf-8")).decode("ascii")

            with Image.open(BytesIO(image_bytes)) as img:
                pnginfo = PngImagePlugin.PngInfo()

                # 保留原有非 chara 元数据
                if hasattr(img, "text") and isinstance(img.text, dict):
                    for k, v in img.text.items():
                        if k not in ("chara", "ccv3"):
                            pnginfo.add_text(k, str(v))

                pnginfo.add_text("chara", b64_str)

                output = BytesIO()
                img.save(output, format="PNG", pnginfo=pnginfo)
                return output.getvalue()

        except Exception as e:
            logger.exception("注入角色卡元数据到 PNG 失败")
            raise ValueError(f"注入角色卡元数据失败: {e}") from e

    @classmethod
    def parse_card_from_json(cls, json_str: str) -> STV2Card | STV3Card:
        """从 JSON 字符串反序列化并校验角色卡。

        Args:
            json_str: JSON 文本字符串。

        Returns:
            STV2Card | STV3Card: 角色卡模型。

        Raises:
            ValueError: JSON 解析或校验失败。
        """
        try:
            raw_dict = json.loads(json_str)
            return cls._dict_to_card(raw_dict)
        except Exception as e:
            logger.error("JSON 角色卡解析失败: %s", e)
            raise ValueError(f"JSON 角色卡解析失败: {e}") from e

    @classmethod
    def to_character_create_request(
        cls,
        card: STV2Card | STV3Card,
        avatar_url: str,
        category: str = "story",
    ) -> CharacterCreateRequest:
        """将 SillyTavern 角色卡转换为叙梦 Naro 的内部创建请求实体。

        Args:
            card: SillyTavern 角色卡模型。
            avatar_url: 角色立绘 URL。
            category: 大分类 (story / nsfw / rpg)。

        Returns:
            CharacterCreateRequest: 叙梦内部创建请求 DTO。
        """
        data = card.data
        extensions = data.extensions if isinstance(data.extensions, dict) else {}

        # 提取世界书条目
        worldbook_dtos: list[WorldBookEntryDTO] = []
        char_book = getattr(data, "character_book", None)
        if isinstance(char_book, dict):
            raw_entries = char_book.get("entries", [])
            if isinstance(raw_entries, list):
                for entry in raw_entries:
                    if isinstance(entry, dict) and entry.get("content"):
                        worldbook_dtos.append(
                            WorldBookEntryDTO(
                                keys=entry.get("keys", []),
                                content=entry.get("content", ""),
                                constant=bool(entry.get("constant", False)),
                                position=entry.get("position", "after_char"),
                            )
                        )

        # 提取专属扩展字段
        prologue_html = str(extensions.get("naro_prologue_html", ""))
        prologue_title = str(extensions.get("naro_prologue_title", "序幕"))

        valid_category = category if category in ("story", "nsfw", "rpg") else "story"

        return CharacterCreateRequest(
            name=data.name or "未命名角色",
            avatar_url=avatar_url,
            category=valid_category,  # type: ignore[arg-type]
            description=data.description or data.name or "无描述",
            personality=data.personality,
            scenario=data.scenario,
            first_mes=data.first_mes or "你好！",
            alternate_greetings=data.alternate_greetings or [],
            system_prompt=data.system_prompt or "",
            post_history_instructions=data.post_history_instructions or "",
            prologue_title=prologue_title,
            prologue_html=prologue_html,
            tags=data.tags or [],
            status="published",
            worldbooks=worldbook_dtos,
        )

    @classmethod
    def export_to_st_card(
        cls,
        character_data: dict[str, Any],
        creator_name: str = "",
    ) -> STV2Card:
        """将内部角色数据转换为标准的 SillyTavern V2 角色卡。

        Args:
            character_data: 角色卡字段字典。
            creator_name: 创作者署名。

        Returns:
            STV2Card: 标准 V2 角色卡模型。
        """
        extensions: dict[str, Any] = {}
        if character_data.get("prologue_html"):
            extensions["naro_prologue_html"] = character_data["prologue_html"]
        if character_data.get("prologue_title"):
            extensions["naro_prologue_title"] = character_data["prologue_title"]

        v2_data = STV2Data(
            name=character_data.get("name", ""),
            description=character_data.get("description", ""),
            personality=character_data.get("personality", ""),
            scenario=character_data.get("scenario", ""),
            first_mes=character_data.get("first_mes", ""),
            mes_example=character_data.get("mes_example", ""),
            creator_notes=character_data.get("creator_notes", ""),
            system_prompt=character_data.get("system_prompt", ""),
            post_history_instructions=character_data.get("post_history_instructions", ""),
            alternate_greetings=character_data.get("alternate_greetings", []),
            tags=character_data.get("tags", []),
            creator=creator_name or character_data.get("creator", ""),
            character_version=character_data.get("version", "1.0.0"),
            extensions=extensions,
        )

        return STV2Card(
            spec="chara_card_v2",
            spec_version="2.0",
            data=v2_data,
        )

    @classmethod
    def _dict_to_card(cls, raw: dict[str, Any]) -> STV2Card | STV3Card:
        """内部辅助：将原始字典按协议判定转换为 STV2 或 STV3 实例。"""
        # 判断是否为 V3 规范 (带有 spec 标识且为 chara_card_v3)
        if raw.get("spec") == "chara_card_v3":
            return STV3Card.model_validate(raw)

        # 判断是否为带有 spec 的 V2 规范
        if raw.get("spec") == "chara_card_v2" and "data" in raw:
            return STV2Card.model_validate(raw)

        # 传统平铺式 V2 角色卡
        if "data" in raw and isinstance(raw["data"], dict):
            return STV2Card.model_validate(raw)

        # 最原始平铺字段，包裹为 data
        return STV2Card(data=STV2Data.model_validate(raw))
