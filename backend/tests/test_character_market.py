"""角色市场、详情指标与世界书 RAG 自动化测试用例。

Usage:
    $ uv run pytest tests/test_character_market.py -v
"""

import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.character import CharacterWorldBook
from app.services.worldbook_service import WorldBookService


@pytest.mark.asyncio
async def test_character_market_seed_and_list() -> None:
    """测试角色市场列表查询、自动种子数据初始化与标签过滤。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. 查询全部角色列表
        resp = await client.get("/api/v1/characters?page=1&page_size=10")
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert data["data"]["total"] >= 4
        items = data["data"]["items"]
        assert len(items) >= 4

        first_char = items[0]
        assert "name" in first_char
        assert "avatar_url" in first_char
        assert "metrics" in first_char
        assert "hotness" in first_char["metrics"]
        assert "author" in first_char

        # 2. 标签过滤 (如 "奇幻")
        tag_resp = await client.get("/api/v1/characters?tag=奇幻")
        assert tag_resp.status_code == 200
        tag_data = tag_resp.json()["data"]
        assert tag_data["total"] >= 1
        assert any("奇幻" in c["tags"] for c in tag_data["items"])

        # 3. 关键词搜索
        kw_resp = await client.get("/api/v1/characters?keyword=Dolce")
        assert kw_resp.status_code == 200
        kw_data = kw_resp.json()["data"]
        assert kw_data["total"] >= 1
        assert "Dolce" in kw_data["items"][0]["name"]


@pytest.mark.asyncio
async def test_character_detail_and_interaction() -> None:
    """测试角色卡全量详情、10 项指标、点赞与评论互动。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. 获取列表第一项的 ID
        list_resp = await client.get("/api/v1/characters")
        first_char = list_resp.json()["data"]["items"][0]
        char_id = first_char["id"]

        # 2. 获取详情
        detail_resp = await client.get(f"/api/v1/characters/{char_id}")
        assert detail_resp.status_code == 200
        detail = detail_resp.json()["data"]
        assert detail["id"] == char_id
        assert "first_mes" in detail
        assert "prologue_html" in detail
        assert "metrics" in detail
        assert "worldbooks" in detail

        # 3. 注册新用户用于互动
        test_email = f"market_tester_{uuid.uuid4().hex[:6]}@naro.ai"
        reg_resp = await client.post(
            "/api/v1/auth/register",
            json={"email": test_email, "password": "Password123!", "username": "MarketTester"},
        )
        token = reg_resp.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 4. 点赞
        like_resp = await client.post(f"/api/v1/characters/{char_id}/like", headers=headers)
        assert like_resp.status_code == 200
        like_data = like_resp.json()["data"]
        assert like_data["is_liked"] is True
        assert like_data["like_count"] >= 1

        # 5. 发表评论
        comment_resp = await client.post(
            f"/api/v1/characters/{char_id}/comments",
            headers=headers,
            json={"content": "太棒了！这个角色的序幕和立绘非常惊艳！"},
        )
        assert comment_resp.status_code == 200
        comment_data = comment_resp.json()["data"]
        assert comment_data["content"] == "太棒了！这个角色的序幕和立绘非常惊艳！"
        assert "market_tester" in comment_data["username"].lower()

        # 6. 获取评论列表
        comments_list_resp = await client.get(f"/api/v1/characters/{char_id}/comments")
        assert comments_list_resp.status_code == 200
        assert comments_list_resp.json()["data"]["total"] >= 1


def test_worldbook_keyword_scanner() -> None:
    """测试世界书关键词与常驻条目扫描算法。"""
    c_id = uuid.uuid4()
    entry1 = CharacterWorldBook(
        id=uuid.uuid4(),
        character_id=c_id,
        keys=["镜花水月", "斩魄刀"],
        content="镜花水月是幻觉系斩魄刀",
        constant=False,
    )
    entry2 = CharacterWorldBook(
        id=uuid.uuid4(),
        character_id=c_id,
        keys=["尸魂界"],
        content="死神居住的世界",
        constant=True,
    )
    entry3 = CharacterWorldBook(
        id=uuid.uuid4(),
        character_id=c_id,
        keys=["虚圈"],
        content="虚生活的大沙漠",
        constant=False,
    )

    all_entries = [entry1, entry2, entry3]

    # 1. 触发关键词 "斩魄刀"
    hits = WorldBookService.scan_keywords("他在战斗中召唤了斩魄刀", all_entries)
    # 常驻条目 + 命中的条目
    assert entry2 in hits  # constant
    assert entry1 in hits  # matched
    assert entry3 not in hits  # not matched

    # 2. 空文本只返回常驻条目
    empty_hits = WorldBookService.scan_keywords("", all_entries)
    assert len(empty_hits) == 1
    assert empty_hits[0] == entry2


@pytest.mark.asyncio
async def test_character_create_full_flow() -> None:
    """测试完整创建角色卡（包含作者的话、序幕、世界书条目、备选开场白等全部参数）。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. 注册创作者用户
        reg_resp = await client.post(
            "/api/v1/auth/register",
            json={"email": "creator_pro@naro.ai", "password": "password123"},
        )
        token = reg_resp.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. 模拟图片上传
        file_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        files = {"file": ("avatar.png", file_content, "image/png")}
        upload_resp = await client.post("/api/v1/upload/image", files=files, data={"folder": "avatars"})
        assert upload_resp.status_code == 200
        avatar_url = upload_resp.json()["data"]["url"]
        assert avatar_url.endswith(".png")

        # 3. 提交全量创建角色请求
        create_payload = {
            "name": "星穹列车长 · 帕姆",
            "avatar_url": avatar_url,
            "banner_url": avatar_url,
            "category": "story",
            "description": "星穹列车的列车长，负责照料列车内外的一切事务。",
            "personality": "认真负责、偶尔傲娇、非常关心乘客安全。",
            "scenario": "在穿梭于星海的星穹列车观景车厢内。",
            "first_mes": "欢迎登车，帕姆！请不要在车厢里乱扔垃圾帕姆！",
            "alternate_greetings": ["今天列车即将进入新的星系，请大家做好准备帕姆！"],
            "system_prompt": "你将扮演星穹列车长帕姆，说话句尾常带'帕姆'。",
            "post_history_instructions": "保持列车长热情可爱的语气。",
            "prologue_title": "序幕 · 星海启程",
            "prologue_html": "<div>列车轰鸣，破晓前行</div>",
            "creator_notes": "这是根据崩铁帕姆设定的角色卡，欢迎大家游玩！",
            "tags": ["星铁", "可爱", "科幻", "治愈"],
            "status": "published",
            "worldbooks": [
                {
                    "keys": ["星穹列车", "列车"],
                    "content": "阿基维利创造的星际列车，能够在银河星轨中穿梭。",
                    "constant": True,
                    "position": "after_char",
                }
            ],
        }

        create_resp = await client.post("/api/v1/characters", headers=headers, json=create_payload)
        assert create_resp.status_code == 200
        char_data = create_resp.json()["data"]
        assert char_data["name"] == "星穹列车长 · 帕姆"
        assert char_data["creator_notes"] == "这是根据崩铁帕姆设定的角色卡，欢迎大家游玩！"
        assert len(char_data["worldbooks"]) == 1
        assert char_data["worldbooks"][0]["keys"] == ["星穹列车", "列车"]
        assert len(char_data["alternate_greetings"]) == 1
        char_id = char_data["id"]

        # 4. 获取详情核对
        detail_resp = await client.get(f"/api/v1/characters/{char_id}")
        assert detail_resp.status_code == 200
        assert detail_resp.json()["data"]["name"] == "星穹列车长 · 帕姆"


@pytest.mark.asyncio
async def test_character_create_with_st_positions_and_normalization() -> None:
    """测试酒馆标准整型 position (0, 1, 2...) 及缺省值的自动清洗与创建。"""
    from app.schemas.character import WorldBookEntryDTO, CharacterCreateRequest

    # 1. 验证 WorldBookEntryDTO 对整型与特殊 position 的清洗
    entry0 = WorldBookEntryDTO(keys=["测试"], content="内容0", position=0)  # type: ignore[arg-type]
    assert entry0.position == "before_char"

    entry1 = WorldBookEntryDTO(keys=["测试"], content="内容1", position=1)  # type: ignore[arg-type]
    assert entry1.position == "after_char"

    entry2 = WorldBookEntryDTO(keys="关键词1,关键词2", content="内容2", position="2")  # type: ignore[arg-type]
    assert entry2.position == "top_an"
    assert entry2.keys == ["关键词1", "关键词2"]

    # 2. 验证端到端 API 创建
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        reg_resp = await client.post(
            "/api/v1/auth/register",
            json={"email": f"st_tester_{uuid.uuid4().hex[:6]}@naro.ai", "password": "password123"},
        )
        token = reg_resp.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        payload = {
            "name": "火影之祸害 · 叙事测试卡",
            "avatar_url": "https://example.com/avatar.png",
            "category": "story",
            "description": "测试整型 position 的世界书",
            "first_mes": "欢迎来到木叶！",
            "worldbooks": [
                {
                    "keys": ["写轮眼"],
                    "content": "宇智波一族的血继限界",
                    "position": 1,  # 酒馆导出的数字 1
                },
                {
                    "keys": ["千手柱间"],
                    "content": "初代火影",
                    "position": 0,  # 酒馆导出的数字 0
                },
            ],
        }

        resp = await client.post("/api/v1/characters", headers=headers, json=payload)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data["worldbooks"]) == 2
        positions = [wb["position"] for wb in data["worldbooks"]]
        assert "after_char" in positions
        assert "before_char" in positions
