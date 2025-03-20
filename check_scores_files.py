import os


def count_missing_scores(root_folder):
    missing_scores_count = 0

    # Iterate over each model name folder
    for model_name in os.listdir(root_folder):
        model_path = os.path.join(root_folder, model_name)

        # Check if it's a directory
        if os.path.isdir(model_path):
            # Iterate over each game name folder
            for game_name in os.listdir(model_path):
                game_path = os.path.join(model_path, game_name)

                # Check if it's a directory
                if os.path.isdir(game_path):
                    # Iterate over each experiment name folder
                    for experiment_name in os.listdir(game_path):
                        experiment_path = os.path.join(game_path, experiment_name)

                        # Check if it's a directory
                        if os.path.isdir(experiment_path):
                            # Iterate over each episode folder
                            for episode_name in os.listdir(experiment_path):
                                episode_path = os.path.join(experiment_path, episode_name)

                                # Check if it's a directory
                                if os.path.isdir(episode_path):
                                    # Check if 'scores.json' file is missing
                                    scores_path = os.path.join(episode_path, 'scores.json')
                                    if not os.path.exists(scores_path):
                                        missing_scores_count += 1
                                        print(f"Missing 'scores.json' in episode: {episode_path}")

    return missing_scores_count


# Set the root folder path
root_folder = "v2.0"

# Call the function
missing_count = count_missing_scores(root_folder)
print(f"Total number of episode folders without 'scores.json': {missing_count}")
