import asyncio
import json
import sys
sys.path.insert(0, 'src')

from app.core.database import AsyncSessionLocal
from app.models.character import Character
from sqlalchemy import select

async def main():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Character).where(Character.name.ilike('%火影之祸害%')))
        chars = res.scalars().all()
        print(f"Found {len(chars)} characters.")
        for c in chars:
            print(f"=== Character ID: {c.id}, Name: {c.name} ===")
            print(f"first_mes (first 200 chars): {c.first_mes[:200]}")
            ext = c.extensions or {}
            print(f"Extensions keys: {list(ext.keys())}")
            regex_scripts = ext.get('regex_scripts', [])
            print(f"regex_scripts count: {len(regex_scripts)}")
            for idx, r in enumerate(regex_scripts):
                print(f"[{idx}] scriptName: {r.get('scriptName')}, placement: {r.get('placement')}, disabled: {r.get('disabled')}, find: {r.get('findRegex')}, replace: {r.get('replaceString')}")

if __name__ == '__main__':
    asyncio.run(main())
