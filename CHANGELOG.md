# Changes between versions

This file documents all changes made between versions of the benchmark which affect the results.

In general, we follow a semantic versioning approach:
- The **major** number changes when new games are added, and hence the clemscore
  (the aggregated score across all games) becomes incomparable (or at least much harder to compare
  compared to earlier versions.
- The **minor** number changes:
    - when new *instances* within the same games are created, and hence a comparison of scores across 
      versions has to be interpreted as comparison within the same game, not the same game problems
    - scoring or parsing rules in the games have changed in such a way as to influence the scores
       (in a minor way).

Note that the dates represent the month in which the version was created. We continuously run new models and add the results to the latest version's directory (so there can be commits with a later date).


## v1.6-multimodal [June 2024]
### Summary
Started a new variant of the benchmark, for testing multimodal / language+vision models.

### Details
#### Added
- Results for multimodal reference game.
- Results for new MatchIt game.
- Results for MapWorld games.


## v1.6  [May 2024]
### Summary
Small fixes to games and scoring rules.

### Details
- Wordle: scoring is adapted to give 100 points when number of turns <= 3.
- Reference: adapted the regex (prefix + output)


## v1.5 [March 2024]
### Summary

1.5 -- **new instances for all games**, new models, improved framework code

### Details
- added new models (Claude-3, GPT-4, Llama-3, Command-R, Mixtral, QWEN-1.5, etc.)
- Game code is changed to remove language-specific implementation to instances file so that the game implementations are language-agnostic (to run multilingual experiments)
- Image game: the parsing changed to accept only matching outputs (prefix + output)
- Reference game: the parsing changed to accept only matching outputs (prefix + output)


## v1.0 [November 2023]
### Summary

Small fixes to games and scoring rules

### Details



## v0.9 [June 2023]
### Summary
Initial version

### Details





