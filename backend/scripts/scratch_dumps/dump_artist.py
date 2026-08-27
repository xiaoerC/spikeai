with open('C:/Users/spike/.gemini/antigravity/brain/88125bf2-dcf4-461b-b349-ca579b7a8233/.system_generated/steps/1420/content.md', 'r', encoding='utf-8') as f:
    html1 = f.read()

with open('artist_list_dump.txt', 'w', encoding='utf-8') as f:
    f.write(html1)

with open('C:/Users/spike/.gemini/antigravity/brain/88125bf2-dcf4-461b-b349-ca579b7a8233/.system_generated/steps/1422/content.md', 'r', encoding='utf-8') as f:
    html2 = f.read()

with open('artist_modal_dump.txt', 'w', encoding='utf-8') as f:
    f.write(html2)

print(f"Dumped artist_list length: {len(html1)}, artist_modal length: {len(html2)}")
