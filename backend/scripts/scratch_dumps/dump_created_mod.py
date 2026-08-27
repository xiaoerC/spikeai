with open('C:/Users/spike/.gemini/antigravity/brain/88125bf2-dcf4-461b-b349-ca579b7a8233/.system_generated/steps/1787/content.md', 'r', encoding='utf-8') as f:
    created_html = f.read()

with open('C:/Users/spike/.gemini/antigravity/brain/88125bf2-dcf4-461b-b349-ca579b7a8233/.system_generated/steps/1789/content.md', 'r', encoding='utf-8') as f:
    add_html = f.read()

with open('my_created_dump.txt', 'w', encoding='utf-8') as f:
    f.write(created_html)

with open('add_mod_dump.txt', 'w', encoding='utf-8') as f:
    f.write(add_html)

print(f"Dumped my_created length: {len(created_html)}, add_mod length: {len(add_html)}")
