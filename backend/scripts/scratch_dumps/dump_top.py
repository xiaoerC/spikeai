with open('C:/Users/spike/.gemini/antigravity/brain/88125bf2-dcf4-461b-b349-ca579b7a8233/.system_generated/steps/394/content.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open('creator_top_lines.txt', 'w', encoding='utf-8') as f:
    for i, line in enumerate(lines[:600]):
        f.write(f"{i+1}: {line}")

print("Saved creator_top_lines.txt")
