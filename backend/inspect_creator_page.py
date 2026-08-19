import re

with open('C:/Users/spike/.gemini/antigravity/brain/88125bf2-dcf4-461b-b349-ca579b7a8233/.system_generated/steps/394/content.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找所有 layer-name 和关键文本
matches = re.findall(r'layer-name="([^"]+)"[^>]*>(.*?)<', content)
print(f"Found {len(matches)} matches")

# 打印独特的 layer-names
layer_names = set(m[0] for m in matches)
for ln in sorted(layer_names):
    print("Layer:", ln)

# 打印前 30 个包含文本的匹配
for m in matches[:60]:
    txt = m[1].strip()
    if txt and not txt.startswith('<'):
        print(f"{m[0]}: {txt}")
