![test-files workflow](https://github.com/clembench/clembench-runs/actions/workflows/test-files.yml/badge.svg)

# Benchmark Runs

# Leaderboard of all runs is available here: [Clem Leaderboard](https://huggingface.co/spaces/colab-potsdam/clem-leaderboard)

## Versions

### **v0.9** - June 2023

### **v1.0** - November 2023

### **v1.5** - March 2024

## Supported Models

The list of supported open & closed/commercial models can be found here: [model registry](https://github.com/clembench/clembench/blob/main/backends/model_registry.json)

# Game-play files

Each model has a separate folder for each game result. The outputs are organised as follows: `/model/game/experiment`. Each episode under a certain experiment includes the following files:


- instance.json : info about a certain episode including the prompt text
- interactions.json: interaction among players and game master
- requests.json: given inputs and generated outputs for the tested model 
- scores.json: generated scores for the episode and turn level
- transcript.html: transcript of the dialogue in HTML
- transcript.tex: transcript of the dialogue in LaTeX

# Results files

Each run of the benchmark generates CSV and HTML files for all tested models across all games (`results.csv` & `results.html`).
