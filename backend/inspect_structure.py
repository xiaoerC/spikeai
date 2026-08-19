import re

with open('C:/Users/spike/.gemini/antigravity/brain/88125bf2-dcf4-461b-b349-ca579b7a8233/.system_generated/steps/394/content.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 提取关键信息
lines = []
for m in re.finditer(r'layer-name="([^"]+)"', content):
    lines.append(m.group(1))

with open('creator_structure.txt', 'w', encoding='utf-8') as f:
    for l in lines:
        f.write(l + '\n')

print("Saved creator_structure.txt")
