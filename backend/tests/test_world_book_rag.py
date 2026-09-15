"""Phase 6: 世界书 (World Book) Aho-Corasick 算法与 RAG 召回单元测试。

验证多关键词扫描、次级逻辑过滤、Token 预算控制、SillyTavern JSON 互转及 RESTful API 端到端。

Usage:
    $ uv run pytest tests/test_world_book_rag.py -v
"""

import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.user import User
from app.schemas.world_book import (
    SillyTavernWorldBookImportDTO,
    WorldBookCreate,
    WorldBookEntryCreate,
)
from app.services.world_book_service import WorldBookScanner, WorldBookService
from tests.conftest import TestAsyncSessionLocal


def test_aho_corasick_keyword_scanner():
    """测试 Aho-Corasick 多关键词极速匹配算法。"""
    id_kusanagi = uuid.uuid4()
    id_jougan = uuid.uuid4()
    id_rasengan = uuid.uuid4()

    keyword_map = {
        "草薙剑": [id_kusanagi],
        "净眼": [id_jougan],
        "螺旋丸": [id_rasengan],
        "佐助": [id_kusanagi],
    }

    # 测试 1: 单词命中
    text1 = "博人握紧了腰间的草薙剑，目光冷峻。"
    hits1 = WorldBookScanner.scan_keywords(text1, keyword_map)
    assert id_kusanagi in hits1
    assert id_jougan not in hits1

    # 测试 2: 多词混合命中
    text2 = "佐助开启了轮回眼，博人则亮出了右眼的净眼。"
    hits2 = WorldBookScanner.scan_keywords(text2, keyword_map)
    assert id_kusanagi in hits2
    assert id_jougan in hits2
    assert id_rasengan not in hits2

    # 测试 3: 未命中
    text3 = "今天天气真不错，木叶村的阳光很温暖。"
    hits3 = WorldBookScanner.scan_keywords(text3, keyword_map)
    assert len(hits3) == 0


def test_secondary_keys_logic_filter():
    """测试次级关键词与逻辑过滤规则。"""
    # 0: AND ANY (包含任意一个即可)
    assert WorldBookScanner.filter_secondary_keys(
        text="佐助与博人在木叶废墟战斗",
        secondary_keys=["木叶", "雨隐"],
        selective_logic=0,
    ) is True
    assert WorldBookScanner.filter_secondary_keys(
        text="佐助与博人在砂隐废墟战斗",
        secondary_keys=["木叶", "雨隐"],
        selective_logic=0,
    ) is False

    # 2: NOT ANY (严禁包含任意一个)
    assert WorldBookScanner.filter_secondary_keys(
        text="博人独自执行S级秘密任务",
        secondary_keys=["川木", "艾达"],
        selective_logic=2,
    ) is True
    assert WorldBookScanner.filter_secondary_keys(
        text="博人遭遇了川木的拦截",
        secondary_keys=["川木", "艾达"],
        selective_logic=2,
    ) is False


@pytest.mark.asyncio
async def test_world_book_service_and_rag_match():
    """测试世界书创建、条目追加、常驻与动态 Token 截断 RAG 匹配。"""
    async with TestAsyncSessionLocal() as session:
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            email=f"wb_user_{uuid.uuid4().hex[:6]}@test.com",
            hashed_password="hashed_pw",
            invite_code=uuid.uuid4().hex[:8],
        )
        session.add(user)
        await session.commit()

        wb_in = WorldBookCreate(
            name="博人传世界观设定集",
            description="包含净眼、神树与楔的深度设定",
            is_public=False,
            scan_depth=3,
            token_budget=300,
            entries=[
                WorldBookEntryCreate(
                    keys=["净眼"],
                    content="净眼是大筒木一族最高位瞳术之一，能感知异常查克拉与时空裂缝。",
                    comment="净眼核心设定",
                    constant=False,
                    insertion_order=10,
                ),
                WorldBookEntryCreate(
                    keys=["楔"],
                    content="楔是大筒木一族用于转生的高密度数据印记，解压后能获取大筒木全部战力。",
                    comment="楔印记",
                    constant=False,
                    insertion_order=20,
                ),
                WorldBookEntryCreate(
                    keys=[],
                    content="【世界通用常识】：神术是凌驾于忍术与仙术之上的终极术式，由大筒木芝居始创。",
                    comment="神术常驻背景",
                    constant=True,
                    insertion_order=5,
                ),
            ],
        )
        wb_detail = await WorldBookService.create_world_book(session, user_id, wb_in)
        assert wb_detail.name == "博人传世界观设定集"
        assert len(wb_detail.entries) == 3

        # 执行 RAG 检索 (仅提及净眼)
        match_res = await WorldBookService.match_world_book_entries(
            db=session,
            character_id=None,
            user_id=user_id,
            user_text="博人，快发动你的净眼看穿敌人的时空忍术！",
            recent_history=[],
        )

        matched_comments = [e.comment for e in match_res.matched_entries]
        assert "神术常驻背景" in matched_comments
        assert "净眼核心设定" in matched_comments
        assert "楔印记" not in matched_comments

        assert "【核心世界观与设定集 (World Book / Lorebook)】" in match_res.formatted_prompt
        assert "净眼是大筒木一族最高位瞳术" in match_res.formatted_prompt
        assert "神术是凌驾于忍术与仙术之上" in match_res.formatted_prompt


@pytest.mark.asyncio
async def test_sillytavern_world_book_import_export():
    """测试 SillyTavern JSON 世界书双向无损互转。"""
    async with TestAsyncSessionLocal() as session:
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            email=f"st_user_{uuid.uuid4().hex[:6]}@test.com",
            hashed_password="hashed_pw",
            invite_code=uuid.uuid4().hex[:8],
        )
        session.add(user)
        await session.commit()

        st_json_data = {
            "name": "SillyTavern测试世界书",
            "description": "导自酒馆的通用世界书",
            "entries": {
                "0": {
                    "uid": 0,
                    "key": ["草薙剑", "雷遁"],
                    "keysecondary": ["佐助"],
                    "selectiveLogic": 0,
                    "content": "草薙剑可传导千鸟电流，锋利无匹。",
                    "comment": "武器设定",
                    "constant": False,
                    "enabled": True,
                    "order": 10,
                    "position": "before_char",
                },
                "1": {
                    "uid": 1,
                    "key": [],
                    "keysecondary": [],
                    "selectiveLogic": 0,
                    "content": "雨隐村终年阴雨绵绵，戒备森严。",
                    "comment": "常驻地点背景",
                    "constant": True,
                    "enabled": True,
                    "order": 5,
                    "position": "before_char",
                },
            },
        }

        import_dto = SillyTavernWorldBookImportDTO(
            name=st_json_data["name"],
            description=st_json_data["description"],
            entries=st_json_data["entries"],
        )

        imported_wb = await WorldBookService.import_sillytavern_json(session, user_id, import_dto)
        assert imported_wb.name == "SillyTavern测试世界书"
        assert len(imported_wb.entries) == 2

        # 导出并验证结构
        exported = await WorldBookService.export_sillytavern_json(session, user_id, imported_wb.id)
        assert exported["name"] == "SillyTavern测试世界书"
        
        # 按内容查找对应条目
        kusanagi_entry = next(e for e in exported["entries"].values() if "草薙剑" in e["content"])
        assert kusanagi_entry["key"] == ["草薙剑", "雷遁"]
        assert kusanagi_entry["keysecondary"] == ["佐助"]
        assert kusanagi_entry["selectiveLogic"] == 0

        rain_entry = next(e for e in exported["entries"].values() if "雨隐村" in e["content"])
        assert rain_entry["constant"] is True


@pytest.mark.asyncio
async def test_world_book_restful_api_flow():
    """测试通过 FastAPI RESTful 接口完成世界书创建、条目增删改及列表查询。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. 注册与登录
        email = f"wb_api_{uuid.uuid4().hex[:8]}@spikeai.com"
        await client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "Password123!", "username": "WBApiUser"},
        )
        login_res = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "Password123!"},
        )
        token = login_res.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. 创建世界书
        wb_res = await client.post(
            "/api/v1/world-books",
            headers=headers,
            json={
                "name": "木叶忍者秘传档案",
                "description": "木叶村各家族血继限界与秘术",
                "is_public": False,
                "scan_depth": 5,
                "token_budget": 2048,
                "entries": [
                    {
                        "keys": ["写轮眼"],
                        "secondary_keys": ["宇智波"],
                        "selective_logic": 0,
                        "content": "宇智波一族的血继限界瞳术，分为单勾玉到永恒万花筒。",
                        "comment": "宇智波瞳术",
                        "constant": False,
                    }
                ],
            },
        )
        assert wb_res.status_code == 201
        wb_data = wb_res.json()
        wb_id = wb_data["id"]
        assert wb_data["name"] == "木叶忍者秘传档案"
        assert len(wb_data["entries"]) == 1

        # 3. 添加条目
        entry_res = await client.post(
            f"/api/v1/world-books/{wb_id}/entries",
            headers=headers,
            json={
                "keys": ["白眼"],
                "secondary_keys": ["日向"],
                "selective_logic": 0,
                "content": "日向一族洞察查克拉穴道的透视眼瞳术。",
                "comment": "日向瞳术",
                "constant": False,
            },
        )
        assert entry_res.status_code == 201
        entry_data = entry_res.json()
        assert entry_data["comment"] == "日向瞳术"

        # 4. 获取世界书列表
        list_res = await client.get("/api/v1/world-books", headers=headers)
        assert list_res.status_code == 200
        assert any(b["id"] == wb_id for b in list_res.json())


@pytest.mark.asyncio
async def test_sillytavern_import_user_complex_payload():
    """测试用户报告的包含 position: 3, disable: false 等复杂原生结构的 SillyTavern JSON 导入。"""
    async with TestAsyncSessionLocal() as session:
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            email=f"complex_st_{uuid.uuid4().hex[:6]}@test.com",
            hashed_password="hashed_pw",
            invite_code=uuid.uuid4().hex[:8],
        )
        session.add(user)
        await session.commit()

        user_payload = SillyTavernWorldBookImportDTO(
            name="导入的世界书",
            description="从 SillyTavern 导入",
            character_id=None,
            entries={
                "0": {
                    "uid": 0,
                    "key": ["丝袜概述"],
                    "keysecondary": [],
                    "comment": "丝袜概述",
                    "content": "丝袜概述：\n丝袜是一种服饰用品...",
                    "constant": True,
                    "selective": True,
                    "order": 1,
                    "position": 3,
                    "excludeRecursion": False,
                    "disable": False,
                    "addMemo": True,
                    "displayIndex": 0,
                    "probability": 100,
                    "useProbability": True,
                    "depth": 4,
                    "selectiveLogic": 0,
                    "group": "",
                },
                "1": {
                    "uid": 1,
                    "key": ["根据材质分类"],
                    "keysecondary": ["尼龙", "水晶丝", "包芯丝"],
                    "comment": "根据材质分类",
                    "content": "根据材质分类：\n\n尼龙丝袜...",
                    "constant": True,
                    "selective": True,
                    "order": 2,
                    "position": 3,
                    "excludeRecursion": False,
                    "disable": False,
                    "addMemo": True,
                    "displayIndex": 1,
                    "probability": 100,
                    "useProbability": True,
                    "depth": 4,
                    "selectiveLogic": 0,
                    "group": "",
                },
            },
        )

        wb_detail = await WorldBookService.import_sillytavern_json(
            db=session,
            user_id=user_id,
            payload=user_payload,
        )

        assert wb_detail.name == "导入的世界书"
        assert len(wb_detail.entries) == 2
        assert wb_detail.entries[0].comment == "丝袜概述"
        assert wb_detail.entries[0].position == "bottom_an"
        assert wb_detail.entries[0].enabled is True
        assert wb_detail.entries[0].constant is True
        assert wb_detail.entries[1].keys == ["根据材质分类"]
        assert wb_detail.entries[1].secondary_keys == ["尼龙", "水晶丝", "包芯丝"]

