import re

with open('C:/Users/spike/.gemini/antigravity/brain/88125bf2-dcf4-461b-b349-ca579b7a8233/.system_generated/steps/394/content.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 找出所有的顶层或者主要 div
print("Content Length:", len(content))

# 提取所有包含作者名称、等级、粉丝、关注按钮的模块
user_blocks = re.findall(r'(\b\w+\b)\s*(Lv\d+)\s*(粉丝\s*[\d\.]+[KMkm]?)\s*(互动\s*[\d\.]+[KMkm]?)', content)
print("User blocks matched:", user_blocks)

# 提取卡片标题
card_titles = re.findall(r'layer-name="Heading 3"[^>]*><div[^>]*>(.*?)</div>', content)
print(f"Card titles ({len(card_titles)}):", card_titles[:10])

# 提取作者信息
authors = re.findall(r'layer-name="Button"[^>]*>.*?@(.*?)<', content)
print("Authors:", set(authors[:15]))
