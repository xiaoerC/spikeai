with open('C:/Users/spike/.gemini/antigravity/brain/88125bf2-dcf4-461b-b349-ca579b7a8233/.system_generated/steps/1909/content.md', 'r', encoding='utf-8') as f:
    collection_tab_html = f.read()

with open('C:/Users/spike/.gemini/antigravity/brain/88125bf2-dcf4-461b-b349-ca579b7a8233/.system_generated/steps/1911/content.md', 'r', encoding='utf-8') as f:
    collection_detail_html = f.read()

with open('collection_tab_dump.txt', 'w', encoding='utf-8') as f:
    f.write(collection_tab_html)

with open('collection_detail_dump.txt', 'w', encoding='utf-8') as f:
    f.write(collection_detail_html)

print(f"Dumped collection_tab length: {len(collection_tab_html)}, collection_detail length: {len(collection_detail_html)}")
