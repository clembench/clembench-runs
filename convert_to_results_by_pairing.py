""" Convert the directory structure from game-based to pairing-based """

import os
import shutil

# benchmark versions:
VERSIONS = ["v0.9", "v1.0"]

for version in VERSIONS:
    # get games in a version:
    games = [game for game in os.listdir(version) if os.path.isdir(os.path.join(version, game))]
    for game in games:
        # get pairings for this game:
        cur_game_pairings = os.listdir(os.path.join(version, game, "records"))
        for pairing in cur_game_pairings:
            # get pairing/game records:
            cur_game_pairing_records = os.listdir(os.path.join(version, game, "records", pairing))
            for record in cur_game_pairing_records:
                shutil.copytree(os.path.join(version, game, "records", pairing, record),
                                os.path.join(version, pairing, game, record))
        # remove old structure:
        shutil.rmtree(os.path.join(version, game))