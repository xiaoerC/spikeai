with open('C:/Users/spike/.gemini/antigravity/brain/88125bf2-dcf4-461b-b349-ca579b7a8233/.system_generated/steps/1687/content.md', 'r', encoding='utf-8') as f:
    html = f.read()

with open('mod_page_dump.txt', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Dumped mod_page length: {len(html)}")
