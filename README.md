# Benchmark Runs

## **v0.9** - June 2023

Evaluated Models:
- GPT-4  
- GPT-3.5-turbo
- Text-davinci-003
- Claude v1.3
- Luminous-supreme
- Falcon-40B
- Koala-13B
- Open-assistant-12B
- Vicuna-13B


# Leaderboard of all runs is available here: [Clem Leaderboard](https://huggingface.co/spaces/colab-potsdam/clem-leaderboard)

# Game-play files

Each game has a separate folder for each model result. The outputs are organised as follows: `game/model/experiment`. Each episode under a certain experiment includes the following files:


- instance.json : info about a certain episode including the prompt text- interactions.json: interaction among players and game master- requests.json: given inputs and generated outputs for the tested model - scores.json: generated scores for the episode and turn level- transcript.html: transcript of the dialogue in HTML- transcript.tex: transcript of the dialogue in LaTeX

# Results files

Each run of the benchmark generates CSV and HTML files for all tested models across all games (`results.csv` & `results.html`).