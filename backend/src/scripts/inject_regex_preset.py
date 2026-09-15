"""将 9 项预设正则脚本注入出厂预置 hamster_god_preset.json 中。

Usage:
    uv run python src/scripts/inject_regex_preset.py
"""

import json
import os

PRESET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "app",
    "data",
    "hamster_god_preset.json",
)

REGEX_SCRIPTS = [
    {
        "id": "51b3f4a5-ee72-4980-abda-8d8fb67479be",
        "scriptName": "【云瑾】包裹最新指示",
        "findRegex": r"^([\s\S]*)$",
        "replaceString": "<最新互动>\n$1\n</最新互动>",
        "trimStrings": [],
        "placement": [1],
        "disabled": False,
        "markdownOnly": False,
        "promptOnly": True,
        "runOnEdit": True,
        "substituteRegex": 0,
        "minDepth": None,
        "maxDepth": 1,
    },
    {
        "id": "d0939a86-4170-44d8-8968-b6148a5c2ed6",
        "scriptName": "【云瑾】移除额外tag_1.5",
        "findRegex": r"/^[\s\S]*(<-begin-response->|我将进行符合需求的创作：)|(<!--[\s\S]*?-->\s?)|<content>\s*##[\s\S]*?---|<thinking>[\s\S]*?</thinking>|<正文>|</正文>|<-end-response->/g",
        "replaceString": "",
        "trimStrings": [],
        "placement": [2],
        "disabled": False,
        "markdownOnly": True,
        "promptOnly": True,
        "runOnEdit": True,
        "substituteRegex": 0,
        "minDepth": None,
        "maxDepth": None,
    },
    {
        "id": "b713fbff-47ae-4616-8d7a-655c4ba407e2",
        "scriptName": "【云瑾】八股抹除 - 4.24",
        "findRegex": r"/而(?=是)|(?<=[，”。\s])不是[\S]*?[，, 。]|(个动作|个反应|个认知|个笑容)|突然|忽然|一(丝+)|(、?)不容置疑([的地]?)|(、?)(不易|难以)(觉察|察觉)([的地]?)|(微|几)不可(查|察|闻)([的地]?)|[，,]([^，,]*?)指(关节|节|尖)([^，,。]*?)白([^，,]*?)(?=[。，,])|(?<=[\\s”。])([^，”]*?)(一抹|弧度)([^，]*?)[。，]|[，,]([^，,”]*?)(一抹|弧度)([^，]*?)(?=[。，,])|(?<=[\\s”。])(.*?)(语气|话像)([^。]*?)[。，]/g",
        "replaceString": "",
        "trimStrings": [],
        "placement": [2],
        "disabled": False,
        "markdownOnly": True,
        "promptOnly": True,
        "runOnEdit": True,
        "substituteRegex": 0,
        "minDepth": None,
        "maxDepth": None,
    },
    {
        "id": "30c53ab4-0c58-4df8-8d3c-e1ba24abcb92",
        "scriptName": "【云瑾】切除10楼以内小总结",
        "findRegex": r"/<scene>(.*?)<\/details>/gs",
        "replaceString": "",
        "trimStrings": [],
        "placement": [2],
        "disabled": False,
        "markdownOnly": False,
        "promptOnly": True,
        "runOnEdit": True,
        "substituteRegex": 0,
        "minDepth": None,
        "maxDepth": 9,
    },
    {
        "id": "4c56b336-bfb1-4766-a053-6f072bfd57c9",
        "scriptName": "【云瑾】切除10楼以上正文&仅保留小总结",
        "findRegex": r"/[\s\S]*<scene>|<\/scene>|<summary>摘要<\/summary>|<details>|<\/details>[\s\S]*/gs",
        "replaceString": "",
        "trimStrings": [],
        "placement": [2],
        "disabled": False,
        "markdownOnly": False,
        "promptOnly": True,
        "runOnEdit": True,
        "substituteRegex": 0,
        "minDepth": 10,
        "maxDepth": None,
    },
    {
        "id": "14c836a8-2b8c-40ee-a476-83f17a7b8772",
        "scriptName": "【夏瑾】底部正则",
        "findRegex": r"/(.*)/s",
        "replaceString": "</补充资料>$1<补充资料>",
        "trimStrings": [],
        "placement": [1, 2],
        "disabled": True,
        "markdownOnly": False,
        "promptOnly": True,
        "runOnEdit": True,
        "substituteRegex": 0,
        "minDepth": None,
        "maxDepth": None,
    },
    {
        "id": "7861fbe0-ed5f-40af-91c1-17f6a3a1a690",
        "scriptName": "【夏瑾】语气正则",
        "findRegex": r"/(?<=(语气|语调|声音)([\u4e00-\u9fa5]+?))([,，]?)(得?)(如同|像|仿佛).*?(?=[。，,])/g",
        "replaceString": "",
        "trimStrings": [],
        "placement": [2],
        "disabled": False,
        "markdownOnly": True,
        "promptOnly": True,
        "runOnEdit": True,
        "substituteRegex": 0,
        "minDepth": None,
        "maxDepth": None,
    },
    {
        "id": "2112de1c-3a68-45bb-a389-1fd17dc09931",
        "scriptName": "【夏瑾】破折号处理",
        "findRegex": r"/(?<=[\u4e00-\u9fa5])——(?=[\u4e00-\u9fa5])/g",
        "replaceString": "，",
        "trimStrings": [],
        "placement": [2],
        "disabled": False,
        "markdownOnly": True,
        "promptOnly": True,
        "runOnEdit": True,
        "substituteRegex": 0,
        "minDepth": None,
        "maxDepth": None,
    },
    {
        "id": "85b2b65a-3762-4006-965c-69eda41ea80b",
        "scriptName": "【夏瑾】比喻正则",
        "findRegex": r"/(?<=[\s”。])([^。，,]*?)(话(像|如同|仿佛))(.*?)。/g",
        "replaceString": "\n",
        "trimStrings": [],
        "placement": [2],
        "disabled": False,
        "markdownOnly": True,
        "promptOnly": True,
        "runOnEdit": True,
        "substituteRegex": 0,
        "minDepth": None,
        "maxDepth": None,
    },
]


def main() -> None:
    with open(PRESET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    data["regex_scripts"] = REGEX_SCRIPTS
    if "extensions" not in data:
        data["extensions"] = {}
    data["extensions"]["regex_scripts"] = REGEX_SCRIPTS
    if "SPreset" not in data["extensions"]:
        data["extensions"]["SPreset"] = {}
    if "RegexBinding" not in data["extensions"]["SPreset"]:
        data["extensions"]["SPreset"]["RegexBinding"] = {}
    data["extensions"]["SPreset"]["RegexBinding"]["regexes"] = REGEX_SCRIPTS

    with open(PRESET_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"成功注入 9 项正则脚本到 {PRESET_PATH}！")


if __name__ == "__main__":
    main()
