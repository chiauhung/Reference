# NLP News Tagger (2019)

A Flask web app that tags news articles using SpaCy named entity recognition. Articles are navigable by tag — click a tag to see all related articles.

![demo](output.gif)

> **Note:** Built around 2019. SpaCy has gone through major version changes since then (v2 → v3 → v4). The code is not maintained and may not run without dependency fixes.

## What It Does

- Reads a set of travel articles
- Runs SpaCy NER to extract entities (people, places, organisations, etc.) as tags
- Serves a Flask app where articles are browsable by tag

## Stack

`Python` · `Flask` · `SpaCy` · `Pandas` · `Gensim`

## Run

```bash
python run.py
```
