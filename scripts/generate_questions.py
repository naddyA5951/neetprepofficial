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


def gen_physics_question(subject, chapter, difficulty, i):
    # Difficulty-aware physics question generator
    if difficulty == 'easy':
        v = random.randint(5, 20)
        t = random.randint(1, 10)
        s = v * t
        q = f"A particle moves with constant speed {v} m/s for {t} s. What distance does it cover?"
        correct = f"{s} m"
        distractors = [f"{s + random.randint(1,6)} m", f"{max(1, s - random.randint(1,6))} m", f"{round(s/2,1)} m"]
        opts, ans = choice_shuffle(correct, distractors)
        exp = f"Step 1: Distance = speed × time.\nStep 2: {v} × {t} = {s} m.\nAnswer: {s} m."
    elif difficulty == 'medium':
        v = random.randint(10, 30)
        t = random.randint(2, 12)
        # convert km/h scenario for medium difficulty
        q = f"A car travels at {v} km/h for {t} minutes. (1 km = 1000 m) What is the distance in meters?"
        speed_ms = v * (1000/3600)
        s_m = round(speed_ms * (t * 60))
        correct = f"{s_m} m"
        distractors = [f"{max(1,s_m - random.randint(10,100))} m", f"{s_m + random.randint(10,100)} m", f"{int(s_m/60)} m"]
        opts, ans = choice_shuffle(correct, distractors)
        exp = f"Convert speed: {v} km/h = {round(speed_ms,2)} m/s. Time = {t} min = {t*60} s. Distance = speed × time = {round(speed_ms,2)}×{t*60} ≈ {s_m} m."
    else:
        a = random.randint(1,4)
        u = random.randint(0,10)
        t = random.randint(2,6)
        s = u * t + 0.5 * a * t * t
        q = f"A body starts with initial velocity {u} m/s and accelerates uniformly at {a} m/s² for {t} s. What is the displacement? (use s=ut+1/2at²)"
        correct = f"{round(s,2)} m"
        distractors = [f"{round(s + random.uniform(1,5),2)} m", f"{round(abs(s - random.uniform(1,5)),2)} m", f"{round(s/2,2)} m"]
        opts, ans = choice_shuffle(correct, distractors)
        exp = f"Use s = ut + 1/2 a t².\nCompute: {u}×{t} + 0.5×{a}×{t}² = {round(s,2)} m."
    return q, opts, ans, exp


def gen_chemistry_question(subject, chapter, difficulty, i):
    if difficulty == 'easy':
        q = f"Which factor primarily determines the chemical reactivity of an element in a period?"
        correct = "Effective nuclear charge and valence electron configuration"
        distractors = ["Atomic mass alone", "Number of neutrons", "Melting point"]
        opts, ans = choice_shuffle(correct, distractors)
        exp = "Reactivity across a period depends on effective nuclear charge and valence electrons, influencing ionization energy and electron affinity."
    elif difficulty == 'medium':
        n = random.randint(1,5)
        q = f"How many moles of water are produced when {n} moles of hydrogen gas react completely with oxygen? (2H2 + O2 → 2H2O)"
        correct = f"{n} moles"
        distractors = [f"{n*2} moles", f"{n/2} moles", f"{n+1} moles"]
        opts, ans = choice_shuffle(correct, distractors)
        exp = f"Reaction stoichiometry: 2H2 + O2 → 2H2O. 2 moles H2 produce 2 moles H2O, so {n} moles H2 produce {n} moles H2O."
    else:
        Ka = round(random.uniform(1e-5,1e-3),6)
        c = round(random.uniform(0.01,0.1),3)
        h = round((Ka*c)**0.5,6)
        q = f"A weak acid HA has Ka = {Ka} and initial concentration {c} M. Using approximation, what is the hydrogen ion concentration [H+]?"
        correct = f"{h} M"
        distractors = [f"{round(h*10,6)} M", f"{round(h/10,6)} M", f"{round((Ka*c)/2,6)} M"]
        opts, ans = choice_shuffle(correct, distractors)
        exp = f"For weak acid HA, [H+] ≈ sqrt(Ka×c) = sqrt({Ka}×{c}) ≈ {h} M."
    return q, opts, ans, exp


def gen_biology_question(subject, chapter, difficulty, i):
    if difficulty == 'easy':
        q = f"Which cellular organelle is primarily responsible for ATP production?"
        correct = "Mitochondrion"
        distractors = ["Ribosome", "Golgi apparatus", "Lysosome"]
        opts, ans = choice_shuffle(correct, distractors)
        exp = "Mitochondria produce ATP by oxidative phosphorylation in the inner mitochondrial membrane via the electron transport chain and ATP synthase."
    elif difficulty == 'medium':
        q = f"In which phase of meiosis does crossing over occur?"
        correct = "Prophase I"
        distractors = ["Metaphase I", "Anaphase II", "Telophase I"]
        opts, ans = choice_shuffle(correct, distractors)
        exp = "Crossing over occurs in Prophase I during synapsis when homologous chromosomes exchange segments, increasing genetic variation."
    else:
        q = "A mutation in a mitochondrial gene reduces ATP production. Which cellular process will be most directly affected?"
        correct = "Active transport requiring ATP"
        distractors = ["Passive diffusion across membrane", "Translation at ribosomes", "DNA replication"]
        opts, ans = choice_shuffle(correct, distractors)
        exp = "Processes that directly consume ATP such as active transport (e.g., Na+/K+ pump) will be affected when mitochondrial ATP production falls."
    return q, opts, ans, exp


def generate_question(subject, chapter, topic, i):
    qid = make_id(subject, chapter, i)
    # assign difficulty probabilistically first
    r = random.random()
    if r < 0.45:
        difficulty = 'easy'
    elif r < 0.85:
        difficulty = 'medium'
    else:
        difficulty = 'hard'

    if subject.lower().startswith('phys'):
        q, opts, ans, exp = gen_physics_question(subject, chapter, difficulty, i)
    elif subject.lower().startswith('chem'):
        q, opts, ans, exp = gen_chemistry_question(subject, chapter, difficulty, i)
    else:
        q, opts, ans, exp = gen_biology_question(subject, chapter, difficulty, i)

    topic_tags = [t.strip() for t in (topic.split(',') if topic else []) if t.strip()]

    return {
        "id": qid,
        "subject": subject,
        "chapter": chapter,
        "topic": topic or "",
        "topicTags": topic_tags,
        "difficulty": difficulty,
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
