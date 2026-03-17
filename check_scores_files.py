import os
import copy

def build_instance_dict(root_folder):
    # goes through root folder, and builds a dict of the form:
    # { 
    #   game_name: {
    #       experiment_name: [instance_name, ...],
    #       ...
    #   },
    #   ...
    # }
    instance_dict = {}
    out_of_pace_dirs = []
    for model_name in os.listdir(root_folder):
        model_path = os.path.join(root_folder, model_name)
        print(f"Processing model: {model_name}")
        if os.path.isdir(model_path):
            for game_name in os.listdir(model_path):
            # for game_name in ['codenames']:
                game_path = os.path.join(model_path, game_name)
                if os.path.isdir(game_path):
                    if game_name not in instance_dict:
                        instance_dict[game_name] = {}
                    for experiment_name in os.listdir(game_path):
                        experiment_path = os.path.join(game_path, experiment_name)
                        if os.path.isdir(experiment_path):
                            if experiment_name not in instance_dict[game_name]:
                                instance_dict[game_name][experiment_name] = []
                                print(f"Processing experiment: {experiment_name}")
                                print(f"Experiment path: {experiment_path}")
                            for episode_name in os.listdir(experiment_path):
                                episode_path = os.path.join(experiment_path, episode_name)
                                if os.path.isdir(episode_path):
                                    if not episode_name.startswith("instance_"):
                                        print(f"WARNING: {episode_path} should be an instance folder, but it doesn't start with 'instance_'!")
                                        out_of_pace_dirs.append(episode_path)
                                    elif episode_name not in instance_dict[game_name][experiment_name]:
                                        instance_dict[game_name][experiment_name].append(episode_name)
    # sort the dict and its nested dicts and lists for consistency
    instance_dict = dict(sorted(instance_dict.items()))
    for game_name in instance_dict:
        instance_dict[game_name] = dict(sorted(instance_dict[game_name].items()))
        for experiment_name in instance_dict[game_name]:
            instance_dict[game_name][experiment_name] = sorted(instance_dict[game_name][experiment_name])
    return instance_dict, out_of_pace_dirs


def count_missing_scores(root_folder, instance_dict):
    missing_interactions = {}
    missing_scores = {}
    # get working dir
    working_dir = os.getcwd()
    root_folder = os.path.join(working_dir, root_folder)

    # Iterate over each model name folder
    for model_name in os.listdir(root_folder):
        model_path = os.path.join(root_folder, model_name)
        print(f"Checking model: {model_name}")
        print(f"Model path: {model_path}")

        model_instance_dict = copy.deepcopy(instance_dict)
        missing_model_interactions = {}
        missing_model_scores = {}

        # Check if it's a directory
        if os.path.isdir(model_path):
            for game_name in model_instance_dict:
                game_path = os.path.join(model_path, game_name)
                if not os.path.isdir(game_path):
                    print(f"WARNING: {game_path} should be a directory, but it's not!")
                    # missing_model_scores[game_name] = "Game folder is missing or not a directory"
                    missing_model_interactions[game_name] = "Game folder is missing or not a directory"
                else:
                    for experiment_name in model_instance_dict[game_name]:
                        experiment_path = os.path.join(game_path, experiment_name)
                        if not os.path.isdir(experiment_path):
                            print(f"WARNING: {experiment_path} should be a directory, but it's not!")
                            if game_name not in missing_model_interactions:
                                missing_model_interactions[game_name] = {}
                            missing_model_interactions[game_name][experiment_name] = f"Experiment folder is missing or not a directory : {experiment_path}"
                            continue
                        for episode_name in model_instance_dict[game_name][experiment_name]:
                            episode_path = os.path.join(experiment_path, episode_name)
                            if not os.path.isdir(episode_path):
                                print(f"WARNING: {episode_path} should be a directory, but it's not!")
                                if game_name not in missing_model_interactions:
                                    missing_model_interactions[game_name] = {}
                                if experiment_name not in missing_model_interactions[game_name]:
                                    missing_model_interactions[game_name][experiment_name] = {}
                                missing_model_interactions[game_name][experiment_name][episode_name] = "Episode folder is missing or not a directory"
                                continue
                            interactions_path = os.path.join(episode_path, 'interactions.json')
                            if not os.path.exists(interactions_path):
                                if game_name not in missing_model_interactions:
                                    missing_model_interactions[game_name] = {}
                                if experiment_name not in missing_model_interactions[game_name]:
                                    missing_model_interactions[game_name][experiment_name] = {}
                                missing_model_interactions[game_name][experiment_name][episode_name] = "interactions.json is missing"
                                print(f"Missing 'interactions.json' in episode: {episode_path}")
                            else:
                                scores_path = os.path.join(episode_path, 'scores.json')
                                if not os.path.exists(scores_path):
                                    if game_name not in missing_model_scores:
                                        missing_model_scores[game_name] = {}
                                    if experiment_name not in missing_model_scores[game_name]:
                                        missing_model_scores[game_name][experiment_name] = {}
                                    missing_model_scores[game_name][experiment_name][episode_name] = "scores.json is missing"
                                    print(f"Missing 'scores.json' in episode: {episode_path}")
                                else:
                                    # remove the instance from the dict to keep track of which ones we've seen
                                    model_instance_dict[game_name][experiment_name].remove(episode_name)
            if missing_model_interactions:
                missing_interactions[model_name] = missing_model_interactions
            if missing_model_scores:
                missing_scores[model_name] = missing_model_scores

    return missing_interactions, missing_scores


# Set the root folder path
root_folder = "v3.0"

import json
instance_dict, out_of_place_dirs = build_instance_dict(root_folder)
with open(os.path.join(root_folder, 'instance_dict.json'), 'w') as f:
    json.dump(instance_dict, f, indent=4)

print(f"Out of place directories: {len(out_of_place_dirs)}")
for dir in out_of_place_dirs:
    print(dir)

missing_interactions, missing_scores = count_missing_scores(root_folder, instance_dict)

with open(os.path.join(root_folder, 'missing_interactions.json'), 'w') as f:
    json.dump(missing_interactions, f, indent=4)

with open(os.path.join(root_folder, 'missing_scores.json'), 'w') as f:
    json.dump(missing_scores, f, indent=4)