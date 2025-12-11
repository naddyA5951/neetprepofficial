#!/usr/bin/env python3
"""Generate placeholder questions (200 per chapter) based on data/manifest.json

This script will load the manifest, iterate all chapters, and write a JSON
array of 200 generated question objects to each chapter file path.
"""
import json
import random
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'data' / 'manifest.json'

def slug(s: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

def make_id(subject, chapter, i):
    return f"{slug(subject)}-{slug(chapter)}-{i+1}"

def generate_question(subject, chapter, topic, i):
    qid = make_id(subject, chapter, i)
    qtext = f"Placeholder Q{i+1}: Sample question for {chapter} ({subject})"
    options = [f"Option {c} for Q{i+1}" for c in ('A','B','C','D')]
    ans = random.randint(0,3)
    return {
        "id": qid,
        "subject": subject,
        "chapter": chapter,
        "topic": topic or "",
        "q": qtext,
        "options": options,
        "ans": ans,
        "exp": "This is a placeholder explanation.",
        "source": "generated"
    }

def main():
    with open(MANIFEST, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    total_files = 0
    for subject, chapters in manifest.items():
        for chapter, meta in chapters.items():
            path = ROOT / meta['file']
            path.parent.mkdir(parents=True, exist_ok=True)
            topic = (meta.get('topics') or [None])[0] if meta.get('topics') else ''
            arr = [generate_question(subject, chapter, topic, i) for i in range(200)]
            with open(path, 'w', encoding='utf-8') as out:
                json.dump(arr, out, indent=2, ensure_ascii=False)
            total_files += 1
    print(f"Wrote {total_files} chapter files with 200 questions each.")

if __name__ == '__main__':
    main()
