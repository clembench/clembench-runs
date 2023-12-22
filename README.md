# Benchmark Runs

# Leaderboard of all runs is available here: [Clem Leaderboard](https://huggingface.co/spaces/colab-potsdam/clem-leaderboard)

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

## **v1.0** - November 2023

Evaluated Models:
### OpenAI models:
- GPT-4-1106-preview
- GPT-4-0613
- GPT-4-0313  
- GPT-3.5-turbo-1106
- GPT-3.5-turbo-0613

### Anthropic models:
- Claude-2.1
- Claude-2
- Claude-v1.3
- Claude-instant-1.2

### Cohere models:
- Command

### Open-weight models:
- CodeLlama-34b-Instruct-hf
- deepseek-llm-67b-chat
- Falcon-7b-instruct
- Koala-13B-HF
- Llama-2-7b-chat-hf
- Llama-2-13b-chat-hf
- Llama-2-70b-chat-hf
- Mistral-7B-Instruct-v0.1
- Mixtral-8x7B-Instruct-v0.1
- Openassistant-sft-4-pythia-12b-epoch-3.5
- Openchat-3.5
- Sheep-duck-llama-2-13b
- Sheep-duck-llama-2-70b-v1.1
- tulu-2-dpo-70b
- tulu-2-dpo-7b
- Vicuna-13b-v1.5
- Vicuna-33b-v1.3
- Vicuna-7b-v1.5
- Wizard-Vicuna-13B-Uncensored-HF
- WizardLM-70b-v1.0
- Yi-34B-Chat
- Zephyr-7b-alpha
- Zephyr-7b-beta

# Game-play files

Each game has a separate folder for each model result. The outputs are organised as follows: `game/model/experiment`. Each episode under a certain experiment includes the following files:


- instance.json : info about a certain episode including the prompt text
- interactions.json: interaction among players and game master
- requests.json: given inputs and generated outputs for the tested model 
- scores.json: generated scores for the episode and turn level
- transcript.html: transcript of the dialogue in HTML
- transcript.tex: transcript of the dialogue in LaTeX

# Results files

Each run of the benchmark generates CSV and HTML files for all tested models across all games (`results.csv` & `results.html`).
