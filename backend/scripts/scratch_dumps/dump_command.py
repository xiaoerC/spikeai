with open('C:/Users/spike/.gemini/antigravity/brain/88125bf2-dcf4-461b-b349-ca579b7a8233/.system_generated/steps/1293/content.md', 'r', encoding='utf-8') as f:
    html1 = f.read()

with open('command_list_dump.txt', 'w', encoding='utf-8') as f:
    f.write(html1)

with open('C:/Users/spike/.gemini/antigravity/brain/88125bf2-dcf4-461b-b349-ca579b7a8233/.system_generated/steps/1295/content.md', 'r', encoding='utf-8') as f:
    html2 = f.read()

with open('command_add_dump.txt', 'w', encoding='utf-8') as f:
    f.write(html2)

print(f"Dumped command_list length: {len(html1)}, command_add length: {len(html2)}")
