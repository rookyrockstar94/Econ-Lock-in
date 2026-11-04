# Econ Lock-In: IB Economics HL Study Guide

`Econ Lock-In.html` is a single-file study app covering the full IB Economics HL course (guide first assessed 2022, with the May 2024 assessment update): notes for every syllabus topic, 71 diagrams, HL calculations, exam technique, a glossary, flashcards, a quiz, calculation drills and essay plans.

The page is generated. To change content, edit the sources in `src/` and rebuild:

```bash
python3 src/build.py
```

- `src/content/*.md`: notes (Units 1–4), exam skills, formulas, quiz questions and essay plans, in a light markup that `build.py` parses.
- `src/diagrams_*.py`: diagram definitions, drawn by `src/diagram_engine.py` as theme-aware SVG.
- `src/app.js`, `src/app.css`, `src/shell.html`: the app.
