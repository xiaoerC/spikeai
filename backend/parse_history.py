from html.parser import HTMLParser
import json

with open('C:/Users/spike/.gemini/antigravity/brain/88125bf2-dcf4-461b-b349-ca579b7a8233/.system_generated/steps/559/content.md', 'r', encoding='utf-8') as f:
    content = f.read()

class HistoryParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.texts = []
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
            self.texts.append((layer, text))

parser = HistoryParser()
parser.feed(content)

with open('history_texts.json', 'w', encoding='utf-8') as f:
    json.dump(parser.texts, f, ensure_ascii=False, indent=2)

print(f"Extracted {len(parser.texts)} texts to history_texts.json")
