"""SillyTavern 预设管理与 Prompt 流水线动态装配服务 (调音台中枢增强版)。

负责:
1. 酒馆预设库管理 (内置三大官方预设 + 用户无限自定义预设另存/删除/切换);
2. 高级宏变量替换与状态变量展开 ({{char}}, {{user}}, {{setvar}}, {{getvar}}, 注释剥离);
3. 动态多锚点 Mod 优先级插桩 (system_prefix, before_char, after_char, bottom_an, user_suffix);
4. 按照 78 项流水线严格动态装配 Messages 与提取采样物理超参数。

Usage:
    >>> from app.services.tavern_service import TavernService
    >>> presets = await TavernService.list_user_presets(user_id)
    >>> messages, params = TavernService.assemble_tavern_messages_and_params(preset, context)
"""

import json
import logging
import os
import re
import uuid
from typing import Any, Callable

import regex as re_engine
from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.tavern import SystemTavernPreset
from app.schemas.tavern import (
    TavernAdvancedFormatting,
    TavernPresetConfig,
    TavernPromptItem,
    TavernPromptOrderItem,
    TavernRegexScript,
)

logger = logging.getLogger(__name__)

# 内存与全局持久化缓存
_CACHED_SYSTEM_PRESET: TavernPresetConfig | None = None
_USER_ACTIVE_PRESETS: dict[str, TavernPresetConfig] = {}
_USER_CUSTOM_PRESETS: dict[str, dict[str, TavernPresetConfig]] = {}
_DEFAULT_PRESET: TavernPresetConfig | None = None
_BUILTIN_PRESETS_CACHE: dict[str, TavernPresetConfig] = {}


class TavernService:
    """酒馆调音台领域服务。"""

    @classmethod
    def get_default_preset(cls) -> TavernPresetConfig:
        """加载原生仓鼠之神V2默认预设。"""
        global _DEFAULT_PRESET
        if _DEFAULT_PRESET is not None:
            return _DEFAULT_PRESET.model_copy(deep=True)

        json_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "hamster_god_preset.json",
        )
        if not os.path.exists(json_path):
            logger.warning("未找到 hamster_god_preset.json，使用备用基础预设")
            _DEFAULT_PRESET = TavernPresetConfig()
            return _DEFAULT_PRESET.model_copy(deep=True)

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

            # 解析 prompts
            prompts = []
            for p in raw_data.get("prompts", []):
                prompts.append(
                    TavernPromptItem(
                        identifier=str(p.get("identifier", "")),
                        name=str(p.get("name", "")),
                        role=str(p.get("role", "system")),
                        content=str(p.get("content", "")),
                        system_prompt=bool(p.get("system_prompt", True)),
                        marker=bool(p.get("marker", False)),
                        enabled=bool(p.get("enabled", True)),
                        injection_position=int(p.get("injection_position", 0)),
                        injection_depth=int(p.get("injection_depth", 4)),
                        injection_trigger=list(p.get("injection_trigger", []) or []),
                        forbid_overrides=bool(p.get("forbid_overrides", False)),
                    )
                )

            # 解析 prompt_order
            prompt_order = []
            raw_order = raw_data.get("prompt_order", [])
            if raw_order and isinstance(raw_order, list):
                if isinstance(raw_order[0], dict) and "order" in raw_order[0]:
                    for item in raw_order[0]["order"]:
                        prompt_order.append(
                            TavernPromptOrderItem(
                                identifier=str(item.get("identifier", "")),
                                enabled=bool(item.get("enabled", True)),
                            )
                        )
                else:
                    for item in raw_order:
                        if isinstance(item, dict):
                            prompt_order.append(
                                TavernPromptOrderItem(
                                    identifier=str(item.get("identifier", "")),
                                    enabled=bool(item.get("enabled", True)),
                                )
                            )
                        else:
                            prompt_order.append(
                                TavernPromptOrderItem(
                                    identifier=str(item),
                                    enabled=True,
                                )
                            )

            # 补齐未在 prompt_order 中的 prompts 条目作为备选 (enabled=False, is_unordered_backup=True)
            ordered_ids = {item.identifier for item in prompt_order}
            for p in prompts:
                if p.identifier not in ordered_ids:
                    prompt_order.append(
                        TavernPromptOrderItem(
                            identifier=p.identifier,
                            enabled=False,
                            is_unordered_backup=True,
                        )
                    )
                    ordered_ids.add(p.identifier)

            # 解析 regex_scripts (兼容根节点、extensions.regex_scripts 或 extensions.SPreset.RegexBinding.regexes)
            raw_regex = raw_data.get("regex_scripts")
            if not raw_regex and isinstance(raw_data.get("extensions"), dict):
                raw_regex = raw_data["extensions"].get("regex_scripts")
                if not raw_regex and isinstance(raw_data["extensions"].get("SPreset"), dict):
                    raw_regex = raw_data["extensions"]["SPreset"].get("RegexBinding", {}).get("regexes")

            regex_scripts = []
            if raw_regex and isinstance(raw_regex, list):
                for r in raw_regex:
                    if isinstance(r, dict):
                        regex_scripts.append(
                            TavernRegexScript(
                                id=str(r.get("id", uuid.uuid4())),
                                scriptName=str(r.get("scriptName", "未命名正则")),
                                findRegex=str(r.get("findRegex", "")),
                                replaceString=str(r.get("replaceString", "")),
                                trimStrings=list(r.get("trimStrings", []) or []),
                                placement=list(r.get("placement", [2]) or [2]),
                                disabled=bool(r.get("disabled", False)),
                                markdownOnly=bool(r.get("markdownOnly", False)),
                                promptOnly=bool(r.get("promptOnly", True)),
                                runOnEdit=bool(r.get("runOnEdit", True)),
                                substituteRegex=int(r.get("substituteRegex", 0)),
                                minDepth=r.get("minDepth"),
                                maxDepth=r.get("maxDepth"),
                            )
                        )

            # 解析 advanced_formatting 高级格式化配置
            adv_fmt_raw = raw_data.get("advanced_formatting")
            if isinstance(adv_fmt_raw, dict):
                adv_fmt = TavernAdvancedFormatting.model_validate(adv_fmt_raw)
            else:
                adv_fmt = TavernAdvancedFormatting()

            _DEFAULT_PRESET = TavernPresetConfig(
                preset_name=raw_data.get("preset_name", "仓鼠之神V2"),
                temperature=float(raw_data.get("temperature", 1.0)),
                frequency_penalty=float(raw_data.get("frequency_penalty", 0.0)),
                presence_penalty=float(raw_data.get("presence_penalty", 0.0)),
                top_p=float(raw_data.get("top_p", 1.0)),
                openai_max_context=int(raw_data.get("openai_max_context", 2000000)),
                openai_max_tokens=int(raw_data.get("openai_max_tokens", 32000)),
                stream_openai=bool(raw_data.get("stream_openai", True)),
                seed=int(raw_data.get("seed", -1)),
                reasoning_effort=raw_data.get("reasoning_effort", "high"),
                prompts=prompts,
                prompt_order=prompt_order,
                regex_scripts=regex_scripts,
                advanced_formatting=adv_fmt,
                is_active=True,
            )
            return _DEFAULT_PRESET.model_copy(deep=True)
        except Exception as e:
            logger.exception("解析默认仓鼠之神预设异常: %s", e)
            _DEFAULT_PRESET = TavernPresetConfig()
            return _DEFAULT_PRESET.model_copy(deep=True)

    @classmethod
    def get_builtin_presets(cls) -> dict[str, TavernPresetConfig]:
        """获取三大官方原生预设字典。"""
        global _BUILTIN_PRESETS_CACHE
        if _BUILTIN_PRESETS_CACHE:
            return {k: v.model_copy(deep=True) for k, v in _BUILTIN_PRESETS_CACHE.items()}

        base = cls.get_default_preset()

        # 1. 仓鼠之神V2
        p_hamster = base.model_copy(deep=True)
        p_hamster.preset_name = "仓鼠之神V2"

        # 2. 文学沉浸创作版
        p_lit = base.model_copy(deep=True)
        p_lit.preset_name = "文学沉浸创作版"
        p_lit.temperature = 0.72
        p_lit.top_p = 0.92
        p_lit.frequency_penalty = 0.25
        p_lit.presence_penalty = 0.15
        p_lit.reasoning_effort = "medium"

        # 3. 高自由度脑洞版
        p_wild = base.model_copy(deep=True)
        p_wild.preset_name = "高自由度脑洞版"
        p_wild.temperature = 1.25
        p_wild.top_p = 0.98
        p_wild.frequency_penalty = 0.1
        p_wild.presence_penalty = 0.35
        p_wild.reasoning_effort = "high"

        _BUILTIN_PRESETS_CACHE = {
            "仓鼠之神V2": p_hamster,
            "文学沉浸创作版": p_lit,
            "高自由度脑洞版": p_wild,
        }
        return {k: v.model_copy(deep=True) for k, v in _BUILTIN_PRESETS_CACHE.items()}

    @classmethod
    async def list_user_presets(cls, user_id: uuid.UUID) -> list[dict[str, Any]]:
        """获取用户可见的所有预设列表（官方预设 + 用户自定义保存预设）。"""
        builtins = cls.get_builtin_presets()
        results: list[dict[str, Any]] = []

        for name, p in builtins.items():
            results.append({
                "preset_name": name,
                "is_builtin": True,
                "temperature": p.temperature,
                "top_p": p.top_p,
                "prompts_count": len(p.prompts),
                "active_prompts_count": sum(1 for item in p.prompt_order if item.enabled),
            })

        uid_str = str(user_id)
        if uid_str in _USER_CUSTOM_PRESETS:
            for name, p in _USER_CUSTOM_PRESETS[uid_str].items():
                results.append({
                    "preset_name": name,
                    "is_builtin": False,
                    "temperature": p.temperature,
                    "top_p": p.top_p,
                    "prompts_count": len(p.prompts),
                    "active_prompts_count": sum(1 for item in p.prompt_order if item.enabled),
                })

        return results

    @classmethod
    def normalize_prompt_order(cls, config: TavernPresetConfig) -> TavernPresetConfig:
        """确保 config.prompt_order 包含 prompts 中的所有条目。

        将未在原 prompt_order 中的备选条目自动追加至末尾并置为 enabled=False, is_unordered_backup=True。

        Usage:
            >>> TavernService.normalize_prompt_order(preset_config)
        """
        ordered_ids = {item.identifier for item in config.prompt_order}
        for p in config.prompts:
            if p.identifier not in ordered_ids:
                config.prompt_order.append(
                    TavernPromptOrderItem(
                        identifier=p.identifier,
                        enabled=False,
                        is_unordered_backup=True,
                    )
                )
                ordered_ids.add(p.identifier)
        return config

    @classmethod
    async def get_user_preset(
        cls,
        user_id: uuid.UUID | str,
        db: AsyncSession | None = None,
    ) -> TavernPresetConfig:
        """获取用户当前生效的酒馆调音台预设。

        优先返回用户内存/独立缓存配置；未定制时平滑回退读取全平台系统激活的基准预设。

        Args:
            user_id: 用户唯一标识符。
            db: 可选的异步数据库会话对象。

        Returns:
            TavernPresetConfig: 酒馆调音预设配置对象。

        Usage:
            >>> preset = await TavernService.get_user_preset(user_id, db)
        """
        uid_str = str(user_id)
        if uid_str in _USER_ACTIVE_PRESETS:
            return _USER_ACTIVE_PRESETS[uid_str].model_copy(deep=True)
        return await cls.get_system_preset(db)

    @classmethod
    async def get_system_preset(cls, db: AsyncSession | None = None) -> TavernPresetConfig:
        """获取当前全平台全局生效的酒馆预设配置。

        优先读取内存/Redis缓存；未命中时从数据库查询；若数据库未初始化则落库默认仓鼠之神V2。

        Usage:
            >>> preset = await TavernService.get_system_preset(db)
        """
        global _CACHED_SYSTEM_PRESET
        if _CACHED_SYSTEM_PRESET is not None:
            return _CACHED_SYSTEM_PRESET.model_copy(deep=True)

        async def _query(session: AsyncSession) -> TavernPresetConfig:
            stmt = (
                select(SystemTavernPreset)
                .where(SystemTavernPreset.is_active.is_(True))
                .order_by(SystemTavernPreset.updated_at.desc())
                .limit(1)
            )
            res = await session.execute(stmt)
            preset_row = res.scalar_one_or_none()

            if preset_row and isinstance(preset_row.config, dict):
                loaded = TavernPresetConfig.model_validate(preset_row.config)
                loaded.preset_name = preset_row.preset_name
                loaded.is_active = bool(preset_row.is_active)
                if not loaded.regex_scripts:
                    loaded.regex_scripts = cls.get_default_preset().regex_scripts
                cls.normalize_prompt_order(loaded)
                return loaded

            # 首次运行：写入系统默认预设到数据库
            default_config = cls.get_default_preset()
            new_preset = SystemTavernPreset(
                preset_name=default_config.preset_name,
                is_active=True,
                config=default_config.model_dump(),
                description="官方出厂默认全平台预设",
                updated_by="system",
            )
            session.add(new_preset)
            try:
                await session.commit()
                await session.refresh(new_preset)
            except Exception as e:
                logger.warning("落库系统默认预设冲突或跳过: %s", e)
                await session.rollback()
            return default_config

        try:
            if db is not None:
                config = await _query(db)
            else:
                async with AsyncSessionLocal() as session:
                    config = await _query(session)
        except Exception as err:
            logger.warning("从数据库读取全局酒馆预设失败，回退至文件默认: %s", err)
            config = cls.get_default_preset()

        cls.normalize_prompt_order(config)
        _CACHED_SYSTEM_PRESET = config.model_copy(deep=True)
        return config

    @classmethod
    async def update_system_preset(
        cls,
        db: AsyncSession,
        updated: TavernPresetConfig,
        admin_user: str | None = None,
        description: str | None = None,
    ) -> TavernPresetConfig:
        """更新并热发布全平台全局生效的酒馆预设。

        Usage:
            >>> fresh = await TavernService.update_system_preset(db, new_config, "admin")
        """
        global _CACHED_SYSTEM_PRESET
        cls.normalize_prompt_order(updated)

        # 1. 停用旧的激活状态
        await db.execute(
            update(SystemTavernPreset)
            .where(SystemTavernPreset.is_active.is_(True))
            .values(is_active=False)
        )

        # 2. 插入新的激活版本
        new_row = SystemTavernPreset(
            preset_name=updated.preset_name,
            is_active=updated.is_active,
            config=updated.model_dump(),
            description=description or "Admin 管理员热发布全局预设",
            updated_by=admin_user or "admin",
        )
        db.add(new_row)
        await db.commit()
        await db.refresh(new_row)

        # 3. 刷新全平台内存缓存
        _CACHED_SYSTEM_PRESET = updated.model_copy(deep=True)
        logger.info(
            "管理员 [%s] 已成功更新并发布全平台全局酒馆预设: %s (激活状态: %s)",
            admin_user,
            updated.preset_name,
            updated.is_active,
        )
        return updated

    @classmethod
    async def reset_system_preset(
        cls,
        db: AsyncSession,
        admin_user: str | None = None,
    ) -> TavernPresetConfig:
        """重置全平台预设为官方出厂原版「仓鼠之神V2」。"""
        fresh_default = cls.get_default_preset()
        return await cls.update_system_preset(
            db=db,
            updated=fresh_default,
            admin_user=admin_user,
            description="管理员恢复官方出厂默认全量 78 项预设",
        )

    @classmethod
    async def list_presets(cls, db: AsyncSession) -> list[dict[str, Any]]:
        """获取管理端预设库中所有已保存预设列表。

        完全从数据库读取管理员自主导入与保存的预设，彻底杜绝硬编码假官方预设。
        若数据库为空，则初始化第一条默认预设入库。
        """
        stmt = select(SystemTavernPreset).order_by(SystemTavernPreset.updated_at.desc())
        res = await db.execute(stmt)
        rows = res.scalars().all()

        if not rows:
            default_config = cls.get_default_preset()
            new_preset = SystemTavernPreset(
                preset_name=default_config.preset_name,
                is_active=True,
                config=default_config.model_dump(),
                description="系统初始基准预设",
                updated_by="system",
            )
            db.add(new_preset)
            await db.commit()
            await db.refresh(new_preset)
            rows = [new_preset]

        results: list[dict[str, Any]] = []
        for r in rows:
            cfg = r.config if isinstance(r.config, dict) else {}
            prompts = cfg.get("prompts", [])
            prompt_order = cfg.get("prompt_order", [])
            regex_scripts = cfg.get("regex_scripts", [])
            results.append({
                "id": str(r.id),
                "preset_name": r.preset_name,
                "is_active": r.is_active,
                "temperature": cfg.get("temperature", 1.0),
                "top_p": cfg.get("top_p", 1.0),
                "prompts_count": len(prompts),
                "active_prompts_count": sum(1 for item in prompt_order if item.get("enabled", True)),
                "regex_count": len(regex_scripts),
                "updated_at": r.updated_at.isoformat() if r.updated_at else None,
                "updated_by": r.updated_by,
                "description": r.description,
            })
        return results

    # 兼容原调用
    list_system_presets = list_presets

    @classmethod
    async def get_preset_by_id(
        cls, db: AsyncSession, preset_id: uuid.UUID
    ) -> TavernPresetConfig:
        """获取指定 ID 的预设完整配置详情。"""
        stmt = select(SystemTavernPreset).where(SystemTavernPreset.id == preset_id)
        res = await db.execute(stmt)
        row = res.scalar_one_or_none()
        if not row:
            raise HTTPException(status_code=404, detail=f"未找到 ID 为 {preset_id} 的预设配置")

        cfg = row.config if isinstance(row.config, dict) else {}
        config = TavernPresetConfig.model_validate(cfg)
        config.preset_name = row.preset_name
        config.is_active = row.is_active
        if not config.regex_scripts:
            config.regex_scripts = cls.get_default_preset().regex_scripts
        cls.normalize_prompt_order(config)
        return config

    @classmethod
    async def create_preset(
        cls,
        db: AsyncSession,
        preset: TavernPresetConfig,
        admin_user: str | None = None,
        is_active: bool = False,
        description: str | None = None,
    ) -> dict[str, Any]:
        """创建/导入一个全新的预设实体并持久化入库。"""
        global _CACHED_SYSTEM_PRESET
        cls.normalize_prompt_order(preset)

        if is_active:
            await db.execute(
                update(SystemTavernPreset)
                .where(SystemTavernPreset.is_active.is_(True))
                .values(is_active=False)
            )

        new_row = SystemTavernPreset(
            preset_name=preset.preset_name,
            is_active=is_active,
            config=preset.model_dump(),
            description=description or f"由 [{admin_user or 'admin'}] 导入/创建",
            updated_by=admin_user or "admin",
        )
        db.add(new_row)
        await db.commit()
        await db.refresh(new_row)

        if is_active:
            _CACHED_SYSTEM_PRESET = preset.model_copy(deep=True)

        logger.info("已创建新预设: ID=%s, 名称=%s, 激活=%s", new_row.id, new_row.preset_name, is_active)
        return {
            "id": str(new_row.id),
            "preset_name": new_row.preset_name,
            "is_active": new_row.is_active,
            "description": new_row.description,
            "updated_at": new_row.updated_at.isoformat() if new_row.updated_at else None,
            "updated_by": new_row.updated_by,
        }

    @classmethod
    async def update_preset_by_id(
        cls,
        db: AsyncSession,
        preset_id: uuid.UUID,
        updated: TavernPresetConfig,
        admin_user: str | None = None,
    ) -> dict[str, Any]:
        """更新指定 ID 的已有预设配置（覆盖原记录，不产生冗余副本）。"""
        global _CACHED_SYSTEM_PRESET
        cls.normalize_prompt_order(updated)

        stmt = select(SystemTavernPreset).where(SystemTavernPreset.id == preset_id)
        res = await db.execute(stmt)
        row = res.scalar_one_or_none()
        if not row:
            raise HTTPException(status_code=404, detail=f"未找到 ID 为 {preset_id} 的预设配置")

        if updated.is_active and not row.is_active:
            await db.execute(
                update(SystemTavernPreset)
                .where(SystemTavernPreset.is_active.is_(True))
                .values(is_active=False)
            )

        row.preset_name = updated.preset_name
        row.is_active = updated.is_active
        row.config = updated.model_dump()
        row.updated_by = admin_user or "admin"

        await db.commit()
        await db.refresh(row)

        if row.is_active:
            _CACHED_SYSTEM_PRESET = updated.model_copy(deep=True)

        logger.info("已更新预设: ID=%s, 名称=%s", row.id, row.preset_name)
        return {
            "id": str(row.id),
            "preset_name": row.preset_name,
            "is_active": row.is_active,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
            "updated_by": row.updated_by,
        }

    @classmethod
    async def activate_preset(
        cls,
        db: AsyncSession,
        preset_id: uuid.UUID,
        admin_user: str | None = None,
    ) -> TavernPresetConfig:
        """将指定 ID 的预设激活为当前全平台全局生效预设。"""
        global _CACHED_SYSTEM_PRESET

        stmt = select(SystemTavernPreset).where(SystemTavernPreset.id == preset_id)
        res = await db.execute(stmt)
        row = res.scalar_one_or_none()
        if not row:
            raise HTTPException(status_code=404, detail=f"未找到 ID 为 {preset_id} 的预设配置")

        # 1. 停用所有其他预设
        await db.execute(
            update(SystemTavernPreset)
            .where(SystemTavernPreset.is_active.is_(True))
            .values(is_active=False)
        )

        # 2. 激活目标预设
        row.is_active = True
        row.updated_by = admin_user or "admin"
        await db.commit()
        await db.refresh(row)

        cfg = row.config if isinstance(row.config, dict) else {}
        config = TavernPresetConfig.model_validate(cfg)
        config.preset_name = row.preset_name
        config.is_active = True
        if not config.regex_scripts:
            config.regex_scripts = cls.get_default_preset().regex_scripts

        _CACHED_SYSTEM_PRESET = config.model_copy(deep=True)
        logger.info("管理员 [%s] 已激活全平台全局生效预设: %s (%s)", admin_user, row.preset_name, row.id)
        return config

    @classmethod
    async def delete_preset(
        cls,
        db: AsyncSession,
        preset_id: uuid.UUID,
    ) -> bool:
        """删除指定预设（正在作为全平台生效的预设禁止删除）。"""
        stmt = select(SystemTavernPreset).where(SystemTavernPreset.id == preset_id)
        res = await db.execute(stmt)
        row = res.scalar_one_or_none()
        if not row:
            raise HTTPException(status_code=404, detail=f"未找到 ID 为 {preset_id} 的预设")

        if row.is_active:
            raise HTTPException(
                status_code=400,
                detail="无法删除当前正在全平台生效中的预设！请先将其他预设设为生效后再删除此预设。",
            )

        await db.delete(row)
        await db.commit()
        logger.info("已删除预设: ID=%s, 名称=%s", preset_id, row.preset_name)
        return True

    @classmethod
    async def rename_preset(
        cls,
        db: AsyncSession,
        preset_id: uuid.UUID,
        new_name: str,
        admin_user: str | None = None,
    ) -> dict[str, Any]:
        """重命名指定预设。"""
        global _CACHED_SYSTEM_PRESET

        new_name = new_name.strip()
        if not new_name:
            raise HTTPException(status_code=400, detail="预设名称不能为空")

        stmt = select(SystemTavernPreset).where(SystemTavernPreset.id == preset_id)
        res = await db.execute(stmt)
        row = res.scalar_one_or_none()
        if not row:
            raise HTTPException(status_code=404, detail=f"未找到 ID 为 {preset_id} 的预设")

        row.preset_name = new_name
        row.updated_by = admin_user or "admin"
        if isinstance(row.config, dict):
            row.config["preset_name"] = new_name
            row.config = dict(row.config)

        await db.commit()
        await db.refresh(row)

        if row.is_active and _CACHED_SYSTEM_PRESET:
            _CACHED_SYSTEM_PRESET.preset_name = new_name

        logger.info("已重命名预设: ID=%s 为 %s", preset_id, new_name)
        return {
            "id": str(row.id),
            "preset_name": row.preset_name,
        }

    @classmethod
    async def get_user_preset(
        cls,
        user_id: uuid.UUID,
        db: AsyncSession | None = None,
    ) -> TavernPresetConfig:
        """获取当前用户正在生效的预设（遵从方案 B：全站用户统一遵从 Admin 全局预设）。"""
        return await cls.get_system_preset(db=db)

    @classmethod
    async def update_user_preset(
        cls, user_id: uuid.UUID, updated: TavernPresetConfig
    ) -> TavernPresetConfig:
        """用户级更新预设（兼容保留）。"""
        uid_str = str(user_id)
        _USER_ACTIVE_PRESETS[uid_str] = updated
        logger.info("用户 %s 已更新酒馆调音台配置: %s", user_id, updated.preset_name)
        return updated

    @classmethod
    async def save_named_preset(
        cls, user_id: uuid.UUID, preset: TavernPresetConfig
    ) -> TavernPresetConfig:
        """另存为或覆盖自定义预设（兼容保留）。"""
        uid_str = str(user_id)
        if uid_str not in _USER_CUSTOM_PRESETS:
            _USER_CUSTOM_PRESETS[uid_str] = {}
        _USER_CUSTOM_PRESETS[uid_str][preset.preset_name] = preset.model_copy(deep=True)
        _USER_ACTIVE_PRESETS[uid_str] = preset.model_copy(deep=True)
        logger.info("用户 %s 另存自定义预设: %s", user_id, preset.preset_name)
        return preset

    @classmethod
    async def delete_named_preset(cls, user_id: uuid.UUID, preset_name: str) -> bool:
        """删除自建预设（兼容保留）。"""
        builtins = cls.get_builtin_presets()
        if preset_name in builtins:
            return False
        uid_str = str(user_id)
        if uid_str in _USER_CUSTOM_PRESETS and preset_name in _USER_CUSTOM_PRESETS[uid_str]:
            del _USER_CUSTOM_PRESETS[uid_str][preset_name]
            logger.info("用户 %s 已删除自定义预设: %s", user_id, preset_name)
            return True
        return False

    @classmethod
    async def reset_user_preset(cls, user_id: uuid.UUID) -> TavernPresetConfig:
        """重置回官方原版配置。"""
        uid_str = str(user_id)
        fresh_default = cls.get_default_preset()
        _USER_ACTIVE_PRESETS[uid_str] = fresh_default
        logger.info("用户 %s 已重置酒馆配置为默认原版", user_id)
        return fresh_default

    @classmethod
    def apply_macros(cls, text: str, context: dict[str, Any]) -> str:
        """高级酒馆宏替换与状态变量展开引擎。

        支持:
        - 基础宏: {{char}}, {{user}}, {{scenario}}, {{personality}}
        - 叙梦 38 变量矩阵: {{player_hp}}, {{location}}, {{time}} 等
        - 酒馆动态变量: {{setvar::k::v}}, {{getvar::k}}
        - 注释剥离: {{// 注释内容}} -> 彻底剔除
        - {{trim}} -> 去除空白
        """
        if not text:
            return ""

        # 1. 彻底剔除酒馆注释 {{// ... }}
        text = re.sub(r"\{\{//.*?\}\}", "", text, flags=re.DOTALL)

        # 2. 基础上下文替换
        char_name = str(context.get("character_name", "AI角色"))
        user_name = str(context.get("user_name", "你"))
        scenario = str(context.get("scenario", ""))
        personality = str(context.get("character_personality", ""))

        text = text.replace("{{char}}", char_name).replace("{{user}}", user_name)
        text = text.replace("{{scenario}}", scenario).replace("{{personality}}", personality)

        # 3. 提取与处理 {{setvar::key::val}} (保持 context['variables'] 跨 Prompt 共享持久)
        if "variables" not in context or not isinstance(context["variables"], dict):
            context["variables"] = {}
        local_vars: dict[str, str] = context["variables"]

        def setvar_repl(match: re.Match[str]) -> str:
            k = match.group(1).strip()
            v = match.group(2).strip()
            local_vars[k] = v
            return ""

        text = re.sub(r"\{\{setvar::([^:]+)::(.*?)\}\}", setvar_repl, text, flags=re.DOTALL)

        # 4. 替换 {{getvar::key}} 与 {{key}}
        def getvar_repl(match: re.Match[str]) -> str:
            k = match.group(1).strip()
            return local_vars.get(k, "")

        text = re.sub(r"\{\{getvar::([^}]+)\}\}", getvar_repl, text)

        for k, v in list(local_vars.items()):
            text = text.replace(f"{{{{{k}}}}}", str(v))

        # 5. {{trim}}
        text = text.replace("{{trim}}", "").strip()
        return text

    @classmethod
    def parse_js_regex(
        cls, find_regex: str, replace_string: str
    ) -> tuple[Any, str] | None:
        """解析酒馆 JS 风格正则（/pattern/flags）与反向引用代换。

        Usage:
            >>> compiled, repl = TavernService.parse_js_regex(r"^([\s\S]*)$", "<tag>\\n$1\\n</tag>")
            >>> result = compiled.sub(repl, "hello")
        """
        if not find_regex:
            return None

        pattern = find_regex
        flags = 0
        if find_regex.startswith("/"):
            m = re_engine.match(r"^/(.*)/([a-z]*)$", find_regex, flags=re_engine.DOTALL)
            if m:
                pattern = m.group(1)
                flags_str = m.group(2)
                if "i" in flags_str:
                    flags |= re_engine.IGNORECASE
                if "m" in flags_str:
                    flags |= re_engine.MULTILINE
                if "s" in flags_str:
                    flags |= re_engine.DOTALL

        # 转换 JS 反向引用 $1, $2 为 Python \g<1>, \g<2>
        py_repl = replace_string.replace("$$", "\x00")
        py_repl = re_engine.sub(r"\$([0-9]+)", r"\\g<\1>", py_repl)
        py_repl = py_repl.replace("\x00", "$")

        try:
            compiled = re_engine.compile(pattern, flags=flags)
            return compiled, py_repl
        except Exception as err:
            logger.warning("SillyTavern 正则编译异常: %s | 原始表达式: %s", err, find_regex)
            return None

    @classmethod
    def make_js_replacer(
        cls, replace_string: str, trim_strings: list[str] | None = None
    ) -> Callable[[Any], str]:
        """构造兼容 JS String.prototype.replace 规范的替换函数。

        仅解析 $$, $&, $1..$99 反向引用，对其它所有反斜杠转义 (如 \\s, \\d 等) 均保持 100% 字面量。
        若指定了 trim_strings，严格遵循 SillyTavern 规范：仅从捕获组 ($1, $2, $&...) 中修剪对应子串，绝不全局误杀。

        Usage:
            >>> repl_func = TavernService.make_js_replacer("hello $1 \\s", ["<"])
            >>> compiled = re_engine.compile(r"h(.*)o")
            >>> result = compiled.sub(repl_func, "h<ell>o")
        """
        trim_list = [ts for ts in (trim_strings or []) if ts]

        def replacer(match: Any) -> str:
            def token_sub(m: Any) -> str:
                tok = m.group(0)
                if tok == "$$":
                    return "$"
                if tok == "$&":
                    val = match.group(0)
                    for ts in trim_list:
                        val = val.replace(ts, "")
                    return val
                if tok.startswith("$") and tok[1:].isdigit():
                    group_idx = int(tok[1:])
                    try:
                        val = match.group(group_idx)
                        if val is None:
                            return ""
                        for ts in trim_list:
                            val = val.replace(ts, "")
                        return val
                    except (IndexError, Exception):
                        return tok
                return tok

            # 兼容 {{match}} 宏代换为 $0 / $&
            raw = replace_string.replace("{{match}}", "$&")
            return re_engine.sub(r"\$\$|\$&|\$[0-9]+", token_sub, raw)

        return replacer

    @classmethod
    def execute_regex_scripts(
        cls,
        text: str,
        scripts: list[TavernRegexScript],
        placement: int,
        depth: int | None = None,
        is_prompt: bool = False,
    ) -> str:
        """按顺序严格执行指定时机与深度的酒馆正则脚本。

        严格遵循 SillyTavern 规范：
        1. promptOnly: 仅在拼装提示词 (is_prompt=True) 时执行，AI 最终输出渲染展示时绝对跳过。
        2. markdownOnly: 仅在 Markdown 渲染阶段执行，拼装提示词阶段绝对跳过。
        3. trimStrings: 仅从正则表达式命中的捕获组中剔除对应子串，严禁全局字符串粗暴 replace 造成 HTML 标签误杀。

        Args:
            text: 输入文本
            scripts: 正则脚本清单
            placement: 生效时机 (1=用户输入/提示词, 2=AI输出回复清洗, 3=快捷命令, 4=世界书, 5=推理)
            depth: 消息在聊天历史中的深度 (如最新消息 depth=1)
            is_prompt: 是否处于上下文提示词拼装流程中

        Returns:
            经过正则处理与修剪后的文本
        """
        if not text or not scripts:
            return text

        current = text
        for s in scripts:
            if s.disabled:
                continue

            # 严格遵循 SillyTavern promptOnly 与 markdownOnly 作用域隔离
            if not is_prompt and s.promptOnly:
                continue
            if is_prompt and s.markdownOnly:
                continue

            # 作用范围时机判定:
            # 1. 精确匹配 placement in s.placement
            # 2. 当 placement=2 (AI输出清洗) 或 999 时，兼容酒馆卡片生态中常用的 999 (Tavern Helper / 渲染层输出清洗钩子)
            # 3. 若 s.placement 为空列表，默认视为全局生效
            match_placement = (
                placement in s.placement
                or ((placement == 2 or placement == 999) and 999 in s.placement)
                or (not s.placement)
            )
            if not match_placement:
                continue

            if depth is not None:
                if s.minDepth is not None and depth < s.minDepth:
                    continue
                if s.maxDepth is not None and depth > s.maxDepth:
                    continue

            parsed = cls.parse_js_regex(s.findRegex, s.replaceString)
            if not parsed:
                continue
            compiled, _ = parsed

            try:
                repl_func = cls.make_js_replacer(s.replaceString, s.trimStrings)
                current = compiled.sub(repl_func, current)
            except Exception as err:
                logger.warning("执行正则脚本 [%s] 异常: %s", s.scriptName, err)

        return current

    @classmethod
    def clean_output_text(
        cls,
        text: str,
        formatting: TavernAdvancedFormatting | None = None,
    ) -> str:
        """根据酒馆高级格式化配置清洗大模型输出文本。

        包含:
        - 折叠 3 个以上多余换行符收敛为双换行
        - 消除末尾因物理截断造成的不完整半句话（回退至最后一个完整标点）
        - 首尾空白字符修剪

        Usage:
            >>> from app.schemas.tavern import TavernAdvancedFormatting
            >>> fmt = TavernAdvancedFormatting(collapse_newlines=True, trim_incomplete_sentences=True)
            >>> cleaned = TavernService.clean_output_text("你好！\\n\\n\\n今天天气真好，我们一起", fmt)
            >>> print(cleaned)
            你好！\\n\\n今天天气真好
        """
        if not text:
            return ""
        if formatting is None:
            formatting = TavernAdvancedFormatting()

        cleaned = text

        # 1. 折叠连续换行符 (3个或更多换行收敛为2个)
        if formatting.collapse_newlines:
            cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

        # 2. 修剪未闭合的不完整句子
        if formatting.trim_incomplete_sentences:
            stripped = cleaned.rstrip()
            valid_endings = ("。", "！", "？", "…", ".", "!", "?", "”", "’", "\"", "'", "』", "」", ")", "）", "*", "—")
            if stripped and not stripped.endswith(valid_endings):
                # 寻找最靠后的终结标点
                matches = list(re.finditer(r"[。！？…!?.]+[”’\"'」』）\)]?|\*+", stripped))
                if matches:
                    last_match = matches[-1]
                    end_pos = last_match.end()
                    # 避免标点靠前导致裁剪过多（保留至少一部分内容）
                    if end_pos > 0:
                        cleaned = stripped[:end_pos]

        # 3. 修剪首尾空白
        if formatting.trim_whitespace:
            cleaned = cleaned.strip()

        return cleaned

    @classmethod
    def assemble_tavern_messages_and_params(
        cls,
        preset: TavernPresetConfig,
        context: dict[str, Any],
    ) -> tuple[list[dict[str, str]], dict[str, Any]]:
        """按照酒馆 Prompt Order 严格动态装配 Messages 与提取采样物理超参数。

        包含:
        - Phase 7: Mod 优先级动态插桩 (system_prefix, before_char, after_char, bottom_an, user_suffix)
        - 高级格式化: 思考链回传轮数限制 (reasoning_history_depth)
        - 高级格式化: 历史后置强化指令 (post_history_instruction)
        - 高级格式化: 自定义终止词与角色名/用户名终止词聚合 (stop)
        - 高级格式化: 回复引导前缀 (reply_prefix)
        """
        adv_fmt = preset.advanced_formatting or TavernAdvancedFormatting()

        # 1. 建立条目查找表
        prompt_map = {p.identifier: p for p in preset.prompts}
        enabled_order = [item for item in preset.prompt_order if item.enabled]

        if not enabled_order:
            ordered_prompts = [p for p in preset.prompts if p.enabled]
        else:
            ordered_prompts = []
            for o in enabled_order:
                if o.identifier in prompt_map:
                    p = prompt_map[o.identifier]
                    if p.enabled:
                        ordered_prompts.append(p)

        messages_for_llm: list[dict[str, str]] = []

        # 提取 Mod 插桩数据
        raw_mod = context.get("mod_patches") or {}
        if hasattr(raw_mod, "model_dump"):
            raw_mod = raw_mod.model_dump()

        system_prefix_list: list[str] = raw_mod.get("system_prefix", [])
        before_char_list: list[str] = raw_mod.get("before_char", [])
        after_char_list: list[str] = raw_mod.get("after_char", [])
        top_an_list: list[str] = raw_mod.get("top_an", [])
        bottom_an_list: list[str] = raw_mod.get("bottom_an", [])
        user_suffix_list: list[str] = raw_mod.get("user_suffix", [])

        system_chunks: list[str] = []

        # 槽位 1: Mod 系统置顶前置 (system_prefix)
        if system_prefix_list:
            system_chunks.extend(system_prefix_list)

        # 遍历排版流水线装配
        for p in ordered_prompts:
            ident = p.identifier.lower()

            if "personadescription" in ident:
                persona_txt = context.get("user_persona", "")
                if persona_txt:
                    system_chunks.append("【用户人设设定】：\n" + persona_txt)
            elif "chardescription" in ident:
                # 槽位 2: Mod 角色前置 (before_char, 如画师串/分镜基调)
                if before_char_list:
                    system_chunks.extend(before_char_list)

                desc_txt = context.get("character_desc", "")
                if desc_txt:
                    system_chunks.append("【角色外貌与基本设定】：\n" + desc_txt)

                # 槽位 3: Mod 角色后置 (after_char, 如语气/性格微调)
                if after_char_list:
                    system_chunks.extend(after_char_list)

            elif "charpersonality" in ident:
                personality_txt = context.get("character_personality", "")
                if personality_txt:
                    system_chunks.append("【性格特征】：\n" + personality_txt)
            elif "worldinfobefore" in ident:
                wi_before = context.get("world_info_before", "")
                if wi_before:
                    system_chunks.append("【前置世界书背景】：\n" + wi_before)
            elif "worldinfoafter" in ident:
                wi_after = context.get("world_info_after", "")
                if wi_after:
                    system_chunks.append("【后置世界书设定】：\n" + wi_after)
            elif "scenario" in ident:
                scen_txt = context.get("scenario", "")
                if scen_txt:
                    system_chunks.append("【当前开场情境】：\n" + scen_txt)
            elif "dialogueexamples" in ident:
                examples = context.get("chat_examples", [])
                if examples:
                    if system_chunks:
                        messages_for_llm.append({"role": "system", "content": "\n\n".join(system_chunks)})
                        system_chunks = []
                    for ex in examples:
                        messages_for_llm.append({
                            "role": ex.get("role", "user"),
                            "content": cls.apply_macros(ex.get("content", ""), context)
                        })
            elif "chathistory" in ident:
                # 槽位 4: Mod Top AN
                if top_an_list:
                    system_chunks.extend(top_an_list)

                if system_chunks:
                    messages_for_llm.append({"role": "system", "content": "\n\n".join(system_chunks)})
                    system_chunks = []

                history = context.get("history_messages", [])
                history_len = len(history)

                # 统计各 assistant 消息在历史中的反向位次（用于思考链保留限制）
                assistant_msgs_from_end = 0
                for idx, h in enumerate(history):
                    h_role = h.get("role", "user")
                    h_content = cls.apply_macros(h.get("content", ""), context)
                    # 计算消息深度: 倒数第一条为 depth 1
                    depth = history_len - idx
                    if h_role == "user" and preset.regex_scripts:
                        h_content = cls.execute_regex_scripts(
                            text=h_content,
                            scripts=preset.regex_scripts,
                            placement=1,
                            depth=depth,
                            is_prompt=True,
                        )
                    elif h_role == "assistant" and preset.regex_scripts:
                        h_content = cls.execute_regex_scripts(
                            text=h_content,
                            scripts=preset.regex_scripts,
                            placement=2,
                            depth=depth,
                            is_prompt=True,
                        )

                    # 思考链治理：根据 reasoning_history_depth 控制是否回传历史思考
                    if h_role == "assistant" and adv_fmt.parse_think_tags:
                        assistant_idx_from_end = sum(
                            1 for item in history[idx:] if item.get("role") == "assistant"
                        )
                        if assistant_idx_from_end > adv_fmt.reasoning_history_depth:
                            # 剥离历史思考链，保留纯正文以节省 Token
                            h_content = re.sub(r"<think>[\s\S]*?</think>", "", h_content)
                            h_content = re.sub(r"<thinking>[\s\S]*?</thinking>", "", h_content).strip()

                    messages_for_llm.append({
                        "role": h_role,
                        "content": h_content,
                    })

                # 槽位 5: Mod Bottom AN (微表情与环境音描写增强)
                if bottom_an_list:
                    messages_for_llm.append({
                        "role": "system",
                        "content": "\n".join(bottom_an_list)
                    })
            else:
                content = cls.apply_macros(p.content.strip(), context)
                if content:
                    if p.role == "system":
                        system_chunks.append(content)
                    else:
                        if system_chunks:
                            messages_for_llm.append({"role": "system", "content": "\n\n".join(system_chunks)})
                            system_chunks = []
                        messages_for_llm.append({"role": p.role, "content": content})

        # 收尾剩余系统提示
        if system_chunks:
            messages_for_llm.append({"role": "system", "content": "\n\n".join(system_chunks)})

        # 槽位 6: Mod 用户输入后置增强 (user_suffix)
        if user_suffix_list:
            last_user_idx = -1
            for i in range(len(messages_for_llm) - 1, -1, -1):
                if messages_for_llm[i]["role"] == "user":
                    last_user_idx = i
                    break
            if last_user_idx != -1:
                messages_for_llm[last_user_idx]["content"] += (
                    "\n\n" + "\n".join(user_suffix_list)
                )
            else:
                messages_for_llm.append({
                    "role": "user",
                    "content": "\n".join(user_suffix_list),
                })

        # 槽位 7: 高级格式化之历史后置强化指令 (Post-History Instruction)
        if adv_fmt.enable_post_history_instruction and adv_fmt.post_history_instruction.strip():
            post_inst_text = cls.apply_macros(adv_fmt.post_history_instruction.strip(), context)
            if post_inst_text:
                post_msg = {"role": "system", "content": post_inst_text}
                depth = adv_fmt.post_history_depth
                if depth <= 0 or depth >= len(messages_for_llm):
                    messages_for_llm.append(post_msg)
                else:
                    insert_idx = max(0, len(messages_for_llm) - depth)
                    messages_for_llm.insert(insert_idx, post_msg)

        # 聚合终止词 (Stop Sequences)
        stop_list: list[str] = list(adv_fmt.stop_sequences)
        char_name = context.get("character_name")
        if adv_fmt.char_name_as_stop and char_name:
            stop_list.extend([f"\n{char_name}:", f"\n{char_name}："])
        user_name = context.get("user_name")
        if adv_fmt.user_name_as_stop and user_name:
            stop_list.extend([f"\n{user_name}:", f"\n{user_name}："])

        deduped_stops = list(dict.fromkeys(stop_list))

        # 提取物理超参数
        sampling_params: dict[str, Any] = {
            "temperature": preset.temperature,
            "frequency_penalty": preset.frequency_penalty,
            "presence_penalty": preset.presence_penalty,
            "top_p": preset.top_p,
            "max_tokens": min(preset.openai_max_tokens, 8192),
            "seed": preset.seed if preset.seed >= 0 else None,
            "reasoning_effort": preset.reasoning_effort,
            "stream": preset.stream_openai,
        }

        if deduped_stops:
            sampling_params["stop"] = deduped_stops

        if adv_fmt.reply_prefix.strip():
            sampling_params["reply_prefix"] = adv_fmt.reply_prefix.strip()
            sampling_params["show_reply_prefix"] = adv_fmt.show_reply_prefix

        return messages_for_llm, sampling_params
