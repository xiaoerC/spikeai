---
name: sillytavern-card-spec
description: SillyTavern V2 与 V3 角色卡与世界书 (Character Book) 规范及 PNG 元数据无损编解码指南。用于前后端角色卡解析、导出及格式转换。
license: MIT
file_patterns:
  - "**/*card*"
  - "**/*png_parser*"
  - "**/*character*"
triggers:
  - "SillyTavern card"
  - "PNG tEXt iTXt"
  - "Character Book"
  - "V2 V3 spec"
---

# SillyTavern V2 / V3 角色卡与世界书规范及编解码标准

本项目（Narratium / Naro）需 1:1 兼容酒馆（SillyTavern）角色卡生态。在进行卡片解析、生成或导出时必须严格遵循以下标准。

---

## 一、 SillyTavern V2 vs V3 数据结构规范

### 1. V2 规范（传统标准格式）
V2 顶层直接为角色卡字段：
```json
{
  "name": "角色名称",
  "description": "角色人设描述",
  "personality": "性格摘要",
  "scenario": "当前场景与世界观设定",
  "first_mes": "首条问候语 (开场白)",
  "mes_example": "<START>\n{{user}}: 你好\n{{char}}: 很高兴见到你",
  "creator_notes": "创作者提示与作者留言",
  "system_prompt": "自定义系统提示词 (可选)",
  "post_history_instructions": "历史后插入指令 (可选)",
  "alternate_greetings": [
    "备用开场白 1",
    "备用开场白 2"
  ],
  "character_book": {
    "name": "内嵌世界书",
    "entries": [
      {
        "keys": ["关键词1", "关键词2"],
        "content": "世界书设定条目内容",
        "enabled": true,
        "insertion_order": 100,
        "constant": false,
        "selective": true
      }
    ]
  },
  "tags": ["奇幻", "冒险"],
  "creator": "作者署名",
  "character_version": "1.0.0",
  "extensions": {}
}
```

### 2. V3 规范（现代化包装层）
V3 使用规范外壳包裹 `data`，解析时必须先判断外层 `spec` 标识：
```json
{
  "spec": "chara_card_v3",
  "spec_version": "3.0",
  "data": {
    "name": "角色名称",
    "description": "角色描述",
    "tags": ["剧情"],
    "creator": "作者",
    "character_version": "3.0.0",
    "mes_example": "",
    "extensions": {},
    "system_prompt": "",
    "post_history_instructions": "",
    "first_mes": "开场白",
    "alternate_greetings": [],
    "personality": "",
    "scenario": "",
    "creator_notes": "",
    "character_book": null,
    "assets": []
  }
}
```

---

## 二、 PNG 元数据编解码标准 (PNG Chunk Spec)

SillyTavern 角色卡将上述 JSON 经过 **Base64** 编码后写入 PNG 格式的 `tEXt` 或 `iTXt` 数据块中，Keyword 固定为 `chara`。

### 1. 后端 Pillow (Python 3.12) 标准编解码实现
```python
import base64
import json
from io import BytesIO
from typing import Any, Dict
from PIL import Image, PngImagePlugin

def extract_character_json(image_bytes: bytes) -> Dict[str, Any]:
    """从 PNG 二进制字节流中提取 SillyTavern 角色卡 JSON 数据
    
    Args:
        image_bytes: PNG 图像原始字节流
        
    Returns:
        解析出的角色卡字典 (标准 Python dict)
        
    Raises:
        ValueError: 当未找到 'chara' 元数据或 JSON 格式损坏时抛出
    """
    with Image.open(BytesIO(image_bytes)) as img:
        # 优先读取 tEXt / iTXt 中的 'chara' 键
        raw_b64 = img.text.get("chara") if hasattr(img, "text") else None
        if not raw_b64:
            # 兼容读取 info
            raw_b64 = img.info.get("chara")
            
        if not raw_b64:
            raise ValueError("PNG 文件中未包含 SillyTavern 'chara' 元数据块")
            
        try:
            json_bytes = base64.b64decode(raw_b64)
            return json.loads(json_bytes.decode("utf-8"))
        except Exception as e:
            raise ValueError(f"解析角色卡 Base64/JSON 失败: {str(e)}") from e

def embed_character_json(image_bytes: bytes, character_data: Dict[str, Any]) -> bytes:
    """将角色卡 JSON 注入到 PNG 图像的 'chara' tEXt 元数据块中
    
    Args:
        image_bytes: 原始图像字节流
        character_data: 角色卡 JSON 数据对象
        
    Returns:
        包含隐写元数据的无损 PNG 字节流
    """
    json_str = json.dumps(character_data, ensure_ascii=False)
    b64_str = base64.b64encode(json_str.encode("utf-8")).decode("ascii")
    
    with Image.open(BytesIO(image_bytes)) as img:
        pnginfo = PngImagePlugin.PngInfo()
        # 保留原有的非 chara 元数据
        if hasattr(img, "text"):
            for k, v in img.text.items():
                if k != "chara":
                    pnginfo.add_text(k, v)
                    
        pnginfo.add_text("chara", b64_str)
        
        output = BytesIO()
        img.save(output, format="PNG", pnginfo=pnginfo)
        return output.getvalue()
```

### 2. 前端 (TypeScript) 标准 Chunk 提取逻辑
前端在纯客户端环境可直接使用 `ArrayBuffer` 与 `DataView` 扫描 PNG 8 字节文件头（`89 50 4E 47 0D 0A 1A 0A`）及后续 `tEXt` / `iTXt` 块，获取 `chara` 字段后执行 `atob()` 和 `decodeURIComponent(escape())` 还原中文字符。
