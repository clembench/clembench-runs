import os
import pandas as pd
import json
from tqdm import tqdm
from datetime import datetime
import logging

logging.basicConfig(filename='latency.log', level=logging.INFO)

root_dirs = os.listdir()
versions = [ver for ver in root_dirs if ver.startswith('v')]


for version in versions:
    latencies = {}
    models = os.listdir(version)
    models = [m for m in models if os.path.isdir(os.path.join(version, m))]
    for model in tqdm(models, desc=f"Calculating latencies for version - {version}"):
        # Split model names - for Player 1 and Player 2
        # Note - Skip one of the players when programmatic
        model1_name = model.split('--')[0].split('-t')[0] # Split by -t to handle different temperatures
        model2_name = model.split('--')[1].split('-t')[0]
        if model1_name not in latencies:
            latencies[model1_name] = {'time': 0.0, 'turns': 0}
        if model2_name not in latencies:
            latencies[model2_name] = {'time': 0.0, 'turns': 0}

        games = os.listdir(os.path.join(version, model))
        games = [g for g in games if os.path.isdir(os.path.join(version, model, g))]
        
        for game in games:
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
                        # Skip latency calculation for this player
                        # Check for "Player_1" or "Player 1" keys
                        if "Player_1" in players.keys():
                            if "programmatic" in players['Player_1'].lower():
                                player1 = False
                            if "programmatic" in players['Player_2'].lower():
                                player2 = False
                        else:
                            if "programmatic" in players['Player 1'].lower():
                                player1 = False
                            if "programmatic" in players['Player 2'].lower():
                                player2 = False 

                        turns = json_data['turns']
                          
                        for turn in turns:
                            for t in turn:
                                if t['from'] == "GM" and ("1" in t['to'] or "2" in t['to']):
                                    #Most recent message from GM to Player 1 or Player 2
                                    start_time = datetime.fromisoformat(t['timestamp'])
                                elif "1" in t['from'] and t['to'] == "GM":
                                    # Message from Player 1 to GM
                                    end_time = datetime.fromisoformat(t['timestamp'])
                                    # Check if Player 1 is programmatic or not
                                    if player1:
                                        latency = end_time - start_time
                                        # latency_ms = latency.total_seconds()*1000
                                        # Save latency in seconds
                                        latency = latency.total_seconds()
                                        latencies[model1_name]['time'] += latency
                                        latencies[model1_name]['turns'] += 1
                                elif "2" in t['from'] and t['to'] == "GM":
                                    # Message from Player 2 to GM
                                    end_time = datetime.fromisoformat(t['timestamp'])
                                    # Check if Player 2 is programmatic or not
                                    if player2:
                                        latency = end_time - start_time
                                        # latency_ms = latency.total_seconds()*1000
                                        # Save latency in seconds
                                        latency = latency.total_seconds()
                                        latencies[model2_name]['time'] += latency
                                        latencies[model2_name]['turns'] += 1
                    else:
                        logging.warning(f"Interaction file missing for {interaction_json_path}")
                        
    
    model_name = []
    model_latency = []
    model_keys = latencies.keys()

    for k in model_keys:
        model_name.append(k)
        model_latency.append(latencies[k]['time']/latencies[k]['turns'])
    csv_data = {
        'model': model_name,
        'latency': model_latency    
        }
    latecy_df = pd.DataFrame(csv_data)
    latecy_df.to_csv(os.path.join(version, 'latency.csv'), index=False)
    logging.info(f"Saved latency.csv for version : {version}")                                
    
