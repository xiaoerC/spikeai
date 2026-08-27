from html.parser import HTMLParser
import json

with open('C:/Users/spike/.gemini/antigravity/brain/88125bf2-dcf4-461b-b349-ca579b7a8233/.system_generated/steps/207/content.md', 'r', encoding='utf-8') as f:
    content = f.read()

class FigmaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.headings = []
        self.labels = []
        self.buttons = []
        self.all_texts = []
        self.stack = []
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        layer_name = attrs_dict.get('layer-name', '')
        self.stack.append((tag, layer_name))
        
    def handle_endtag(self, tag):
        if self.stack:
            self.stack.pop()
            
    def handle_data(self, data):
        text = data.strip()
        if text:
            layer = self.stack[-1][1] if self.stack else ''
            self.all_texts.append((layer, text))
            if 'Heading' in layer or any(h in layer for h in ['原创角色卡', '作者的话', '角色卡信息', '设定集', '基础设置', '角色问候语', '世界书', '对话示例', '高级设置']):
                self.headings.append((layer, text))
            if 'Button' in layer:
                self.buttons.append((layer, text))

parser = FigmaParser()
parser.feed(content)

print(f"Total texts: {len(parser.all_texts)}")
print("\n=== HEADINGS & SECTIONS ===")
for h in parser.headings:
    print(f"  {h[0]} -> {h[1]}")

print("\n=== BUTTONS ===")
for b in set(parser.buttons):
    print(f"  {b[0]} -> {b[1]}")

with open('creator_texts.json', 'w', encoding='utf-8') as f:
    json.dump(parser.all_texts, f, ensure_ascii=False, indent=2)

print("\nSaved creator_texts.json")
