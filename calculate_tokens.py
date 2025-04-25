import os
import pandas as pd
import json
from tqdm import tqdm
import logging
import re  
from transformers import LlamaTokenizer

HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
tokenizer = LlamaTokenizer.from_pretrained("meta-llama/Llama-2-7b-chat-hf", use_auth_token=HUGGINGFACE_TOKEN)

logging.basicConfig(filename='tokens.log', level=logging.INFO)


def count_tokens(turn: dict) -> int:
    """
    Count tokens of a given turn/message using LlamaTokenizer

    Args:
        turn: The text context for a given turn, either GM->Player or Player->GM
    Return:
        tokens: count of tokens in the text message
    """
    if type(turn['action']['content']) == dict:
        text_content = turn['action']['content']['content'] # multimodal_referencegame format
    elif type(turn['action']['content']) == str :
        text_content = turn['action']['content']
    else:
        raise TypeError(f"Expected the turn content in either str or dict format, but received {type(text_content)} for turn : {turn}")

    tokens = tokenizer(text_content) 
    return len(tokens["input_ids"])


root_dirs = os.listdir()
versions = [ver for ver in root_dirs if ver.startswith('v')]

for version in versions:
    tokens = {}
    models = os.listdir(version)
    models = [m for m in models if os.path.isdir(os.path.join(version, m))]
    for model in tqdm(models, desc=f"Calculating Tokens for models in benchmark version - {version}"):
        # Use regex to split model names and handle temperature values
        match = re.match(r"(.+?)-t\d\.\d--(.+?)-t\d\.\d", model)
        if match:
            model1_name = match.group(1)
            model2_name = match.group(2)
        if model1_name not in tokens:
            tokens[model1_name] = {'input_tokens': 0.0, 'output_tokens': 0.0, 'input_message_count':0, 'output_message_count':0}
        if model2_name not in tokens:
            tokens[model2_name] = {'input_tokens': 0.0, 'output_tokens': 0.0, 'input_message_count':0, 'output_message_count':0}

        games = os.listdir(os.path.join(version, model))
        games = [g for g in games if os.path.isdir(os.path.join(version, model, g))]
        for game in games:
            logging.info(f"Calculating Tokens for model1 = {model1_name} and model2 = {model2_name} for game = {game}")

            experiments = os.listdir(os.path.join(version, model, game))
            experiments = [e for e in experiments if os.path.isdir(os.path.join(version, model, game, e))]
            
            for exp in experiments:
                episodes = os.listdir(os.path.join(version, model, game, exp))
                episodes = [e for e in episodes if os.path.isdir(os.path.join(version, model, game, exp, e))]
                for episode in episodes:
                   # Get the interactions.json path for each episode
                    interaction_json_path = os.path.join(version, model, game, exp, episode, 'interactions.json')
                   
                    if os.path.exists(interaction_json_path):
                        with open(interaction_json_path, 'r') as file:
                            json_data = json.load(file)
                        players = json_data['players']
    
                        player1 = True
                        player2 = True
                        # Set a false flag when a player is Programmatic
                        # Check for "Player_1" or "Player 1" keys
                        if "Player_1" in players:
                            if "programmatic" in players['Player_1'].lower():
                                player1 = False
                        elif "Player 1" in players:
                            if "programmatic" in players['Player 1'].lower():
                                player1 = False

                        if "Player_2" in players:
                            if "programmatic" in players['Player_2'].lower():
                                player2 = False
                        elif "Player 2" in players:
                            if "programmatic" in players['Player 2'].lower():
                                player2 = False 

                        turns = json_data['turns']

                        last_input_tokens = 0
                        for turn in turns:
                            for t in turn:
                                if t['from'] == "GM" and ("1" in t['to'] or "2" in t['to']):
                                    # Most recent message from GM to Player 1 or Player 2
                                    input_tokens = count_tokens(t)
                                    last_input_tokens += input_tokens
                                    tokens[model1_name]['input_tokens'] += last_input_tokens
                                    tokens[model2_name]['input_message_count'] += 1
                                elif "1" in t['from'] and t['to'] == "GM" and player1:
                                    # Message from Player 1 to GM
                                    output_tokens = count_tokens(t)
                                    last_input_tokens += output_tokens
                                    tokens[model1_name]['output_tokens'] += output_tokens
                                    tokens[model1_name]['output_message_count'] += 1
                                     
                                elif "2" in t['from'] and t['to'] == "GM" and player2:
                                    # Message from Player 2 to GM
                                    output_tokens = count_tokens(t)
                                    last_input_tokens += output_tokens
                                    tokens[model2_name]['output_tokens'] += output_tokens
                                    tokens[model2_name]['output_message_count'] += 1
                    else:
                        logging.warning(f"Interaction file missing for {interaction_json_path}")
                        
    
    model_name = []
    model_avg_input_tokens = []
    model_avg_output_tokens = []
    model_total_input_tokens = []
    model_total_output_tokens = []
    model_keys = tokens.keys()

    avg_input_tokens = 0
    avg_output_tokens = 0
    for k in model_keys:
        model_name.append(k)
        try:
            avg_input_tokens = int(tokens[k]['input_tokens'] / tokens[k]['input_message_count'])
            avg_output_tokens = int(tokens[k]['output_tokens'] / tokens[k]['output_message_count'])
        except ZeroDivisionError:
            print(f"ZeroDivisionError for model {k} - input_message_count: {tokens[k]['input_message_count']}, output_message_count: {tokens[k]['output_message_count']}")

        model_avg_input_tokens.append(avg_input_tokens)
        model_avg_output_tokens.append(avg_output_tokens)
        model_total_input_tokens.append(round(tokens[k]['input_tokens']/1000000,2))
        model_total_output_tokens.append(round(tokens[k]['output_tokens']/1000000, 2))


    csv_data = {
        'model': model_name,
        'avg_in (per turn)': model_avg_input_tokens,
        'avg_out (per turn)': model_avg_output_tokens,
        'total_in (M token)': model_total_input_tokens,
        'total_out (M token)': model_total_output_tokens
    }
    tokens_df = pd.DataFrame(csv_data)
    if not os.path.exists(os.path.join('Addenda', 'Tokens')):
        os.makedirs(os.path.join('Addenda', 'Tokens'))
    tokens_df.to_csv(os.path.join('Addenda', 'Tokens', version+'_tokens.csv'), index=False)
    logging.info(f"Saved tokens.csv for version : {version}")                                
    