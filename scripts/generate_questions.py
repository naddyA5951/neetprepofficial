#!/usr/bin/env python3
"""Generate placeholder questions (200 per chapter) based on data/manifest.json

This script will load the manifest, iterate all chapters, and write a JSON
array of 200 generated question objects to each chapter file path.
"""
import json
import random
import pathlib
import re
from math import isclose

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'data' / 'manifest.json'


def slug(s: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def make_id(subject, chapter, i):
    return f"{slug(subject)}-{slug(chapter)}-{i+1}"


def choice_shuffle(correct, distractors):
    opts = distractors[:]
    opts.append(correct)
    random.shuffle(opts)
    return opts, opts.index(correct)


def gen_physics_question(subject, chapter, i):
    # Mix conceptual and numeric templates
    if random.random() < 0.45:
        # numerical kinematics style
        v = random.randint(5, 40)
        t = random.randint(1, 10)
        s = v * t
        q = f"A particle moves with constant speed {v} m/s for {t} s. What distance does it cover?"
        correct = f"{s} m"
        distractors = [f"{s + random.randint(1,10)} m", f"{max(1, s - random.randint(1,10))} m", f"{s/2} m"]
        opts, ans = choice_shuffle(correct, distractors)
        exp = f"Distance = speed × time = {v}×{t} = {s} m."
    else:
        q = f"Which statement about Newton's third law is correct?"
        correct = "For every action there is an equal and opposite reaction."
        distractors = [
            "Action and reaction act on the same body.",
            "Action and reaction do not occur simultaneously.",
            "Action is greater than reaction when bodies are accelerating."
        ]
        opts, ans = choice_shuffle(correct, distractors)
        exp = "Newton's third law: action and reaction are equal in magnitude, opposite in direction, and act on different bodies."
    return q, opts, ans, exp


def gen_chemistry_question(subject, chapter, i):
    if random.random() < 0.5:
        # conceptual periodicity / bonding
        q = f"Which factor primarily determines the chemical reactivity of an element in a period?"
        correct = "Effective nuclear charge and valence electron configuration"
        distractors = [
            "Atomic mass alone",
            "Number of neutrons",
            "Melting point"
        ]
        opts, ans = choice_shuffle(correct, distractors)
        exp = "Reactivity across a period is governed by effective nuclear charge and valence electrons, affecting electron affinity/ionization."
    else:
        # simple stoichiometry numeric
        n = random.randint(1,5)
        q = f"How many moles of water are produced when {n} moles of hydrogen gas react completely with oxygen? (2H2 + O2 → 2H2O)"
        correct = f"{n} moles"
        distractors = [f"{n*2} moles", f"{n/2} moles", f"{n+1} moles"]
        opts, ans = choice_shuffle(correct, distractors)
        exp = "Reaction stoichiometry: 2 moles H2 produce 2 moles H2O, so moles of water equal moles of H2 reacted."
    return q, opts, ans, exp


def gen_biology_question(subject, chapter, i):
    if random.random() < 0.5:
        q = f"Which cellular organelle is primarily responsible for ATP production?"
        correct = "Mitochondrion"
        distractors = ["Ribosome", "Golgi apparatus", "Lysosome"]
        opts, ans = choice_shuffle(correct, distractors)
        exp = "Mitochondria generate ATP via oxidative phosphorylation in eukaryotic cells."
    else:
        q = f"In which phase of meiosis does crossing over occur?"
        correct = "Prophase I"
        distractors = ["Metaphase I", "Anaphase II", "Telophase I"]
        opts, ans = choice_shuffle(correct, distractors)
        exp = "Crossing over occurs during Prophase I when homologous chromosomes pair and exchange segments."
    return q, opts, ans, exp


def generate_question(subject, chapter, topic, i):
    qid = make_id(subject, chapter, i)
    if subject.lower().startswith('phys'):
        q, opts, ans, exp = gen_physics_question(subject, chapter, i)
    elif subject.lower().startswith('chem'):
        q, opts, ans, exp = gen_chemistry_question(subject, chapter, i)
    else:
        q, opts, ans, exp = gen_biology_question(subject, chapter, i)

    return {
        "id": qid,
        "subject": subject,
        "chapter": chapter,
        "topic": topic or "",
        "q": q,
        "options": opts,
        "ans": ans,
        "exp": exp,
        "source": "generated-original"
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
            arr = [generate_question(subject, chapter, topic, i) for i in range(300)]
            with open(path, 'w', encoding='utf-8') as out:
                json.dump(arr, out, indent=2, ensure_ascii=False)
            total_files += 1
    print(f"Wrote {total_files} chapter files with 300 NEET-style questions each.")


if __name__ == '__main__':
    main()
