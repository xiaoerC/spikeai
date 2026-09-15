import os
import sys
import glob

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

temp_handoff = os.path.join(os.environ.get("TEMP", ""), "naro_handoff_phase4.md")
print("=== Checking Temp Handoff ===")
if os.path.exists(temp_handoff):
    print("Found temp handoff:", temp_handoff)
    with open(temp_handoff, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        print(f"Read {len(content)} chars from handoff.")
        # Save to workspace docs/
        os.makedirs("docs", exist_ok=True)
        with open("docs/handoff_phase4.md", "w", encoding="utf-8") as out:
            out.write(content)
        print("Saved to docs/handoff_phase4.md")

print("\n=== Searching for roadmaps and handoffs ===")
search_paths = [
    r"C:\Users\spike\.gemini\antigravity\brain\**\*roadmap*.md",
    r"C:\Users\spike\.gemini\antigravity-ide\brain\**\*roadmap*.md",
    r"C:\Users\spike\.gemini\**\*handoff*.md",
]

for sp in search_paths:
    for f in glob.glob(sp, recursive=True):
        print(f"File: {f} ({os.path.getsize(f)} bytes)")
        if "roadmap" in f.lower():
            try:
                with open(f, "r", encoding="utf-8", errors="ignore") as rf:
                    rm_content = rf.read()
                dest = os.path.join("docs", os.path.basename(f))
                with open(dest, "w", encoding="utf-8") as out:
                    out.write(rm_content)
                print(f"  -> Copied to {dest}")
            except Exception as e:
                print(f"  -> Error copying: {e}")
