"""Count benchmark request tokens and estimate benchmark run costs for a model set."""

from clemcore.backends.huggingface_local_api import load_config_and_tokenizer
from clemcore.backends.model_registry import ModelRegistry
import tiktoken
import os
import json
import requests
import pandas as pd
import logging
from datetime import datetime

logging.basicConfig(filename='cost_estimator.log')

# naive estimation
def naive_tokens_high(raw_input_string) -> int:
    """
    Naively estimates high token count from high token/characters, split ratio of 3.
    :param raw_input_string: The raw input string to be 'tokenized'.
    :return: The rounded integer 'token count'.
    """
    split_count: float = len(raw_input_string) / 3
    return int(round(split_count))


def naive_tokens_low(raw_input_string) -> int:
    """
    Naively estimates low token count from low token/characters, split ratio of 5.
    :param raw_input_string: The raw input string to be 'tokenized'.
    :return: The rounded integer 'token count'.
    """
    split_count: float = len(raw_input_string) / 5
    return int(round(split_count))


class CostEstimator:
    """Combines tokenizers, estimators and token costs to estimate benchmark running costs."""
    def __init__(self, benchmark: str = "v3.0", ignore_models: list = []):
        """
        Initialize CostEstimator for a benchmark version and optionally exclude results from given models.
        :param benchmark: The benchmark version, must match the directory name/path where results of the benchmark are
            stored.
        :param ignore_models: List of model names/IDs of models to be ignored. Refer to the clemcore model registry for
            the correct names. Model result directory names in the benchmark results folder are the registry model
            names/IDs with the suffix -t0.0 added - use the name without the -t0.0 suffix for this list.
        """
        self.benchmark: str = benchmark
        self.ignore_models: list = ignore_models
        self.get_benchmark_models()
        # Tokenizers
        self.oai_tokenizer = None
        self.hf_tokenizers: dict = dict()
        self.load_tokenizers()
        # Count tokens
        self.games: list = list()
        self.get_benchmark_games()
        self.model_tkn_counts: dict = dict()
        self.average_tkn_cnt: dict = dict()
        self.get_average_token_counts()
        # OpenRouter pricing
        self.openrouter_models: list = list()
        # self.get_openrouter_models_from_file()
        self.openrouter_prices: dict = dict()
        # self.get_current_openrouter_pricing()
        # Calculate costs
        self.estimated_costs: dict = dict()
        # self.estimate_benchmark_costs()

    def get_benchmark_models(self):
        """Get model directories in benchmark and remove ignored models from cost estimation.        """
        self.models = [model.replace("-t0.0", "") for model in os.listdir(f"{self.benchmark}")]
        # Remove ignored models
        for ignore_model in self.ignore_models:
            if ignore_model.endswith("-t0.0"):
                ignore_model = ignore_model.replace("-t0.0", "")  # Laziness safety
            self.models.remove(ignore_model)

    def load_tokenizers(self):
        """Loads tiktoken tokenizer and HuggingFace tokenizers for the models in the targeted benchmark directory."""
        # Load tiktoken tokenizer for OpenAI models
        self.oai_tokenizer = tiktoken.get_encoding("o200k_base")  # o200k_base should cover october 2025 models
        # Load HF tokenizers for given open models
        model_registry = ModelRegistry.from_packaged_and_cwd_files()
        for results_model in self.models:
            model_spec = model_registry.get_first_model_spec_that_unify_with(results_model)
            if not model_spec:
                logging.error(f"No model registry entry found for {results_model}, please make sure that the clemcore "
                              f"model registry that was used to run this benchmark version or a newer equivalent is "
                              f"available.")
            elif model_spec.backend == "huggingface_local":  # only do this for models that used HF-local backend
                self.hf_tokenizers[results_model] = load_config_and_tokenizer(model_spec)[0]
            else:
                logging.info(f"Model {model_spec.model_name} uses {model_spec.backend} backend, which is not covered "
                             f"by the cost estimator due to uncertain tokenization and will thus not have native token "
                             f"counts.")

    def get_benchmark_games(self):
        """Get games in benchmark from first model results directory and warn about game set mismatches."""
        self.games = [game for game in os.listdir(f"{self.benchmark}{os.sep}{self.models[0]}-t0.0")
                      if not game.endswith(".json")]
        # Check for mismatch/missing games
        for model in self.models:
            model_games = [game for game in os.listdir(f"{self.benchmark}{os.sep}{model}-t0.0")
                           if not game.endswith(".json")]
            if not model_games == self.games:
                for game in model_games:
                    if game not in self.games:
                        logging.error(f"{model} directory contains results for {game}, while the first found model "
                                      f"results directory does not! Please assure that the benchmark model directories "
                                      f"all contain the full game set for this benchmark version.")
                for game in self.games:
                    if game not in model_games:
                        logging.error(f"{model} directory does not contain results for {game}, while the first found "
                                      f"model results directory does! Please assure that the benchmark model "
                                      f"directories all contain the full game set for this benchmark version.")

    def count_benchmark_tokens(self):
        """Counts native tokens, tiktoken tokens and naive estimates for entire benchmark."""
        for model in self.models:
            all_games_tkn_counts: list = list()
            for game in self.games:
                model_game_path = f"{self.benchmark}{os.sep}{model}-t0.0{os.sep}{game}"
                game_experiments = os.listdir(model_game_path)
                game_exp_tkns: list = list()
                for game_experiment in game_experiments:
                    game_experiment_path = f"{model_game_path}{os.sep}{game_experiment}"
                    episodes = [episode for episode in os.listdir(game_experiment_path)
                                if not episode.endswith(".json")]
                    experiment_ep_req_sums: list = list()
                    for episode in episodes:
                        ep_reqs_counts: list = list()
                        # Get requests content
                        ep_requests = self.get_episode_requests(f"{game_experiment_path}{os.sep}{episode}")
                        # Count individual request tokens
                        for request in ep_requests:
                            req_counts: dict = dict()
                            if model in self.hf_tokenizers:
                                # Get native token counts
                                native_input_tokens = self.hf_tokenizers[model].encode(request['input'])
                                req_counts['native_input_tokens'] = len(native_input_tokens)
                                native_output_tokens = self.hf_tokenizers[model].encode(request['output'])
                                req_counts['native_output_tokens'] = len(native_output_tokens)
                            else:
                                # Counting as 0 if no native HF tokenizer is available
                                # NOTE: Token count averaging divides by the number of HF tokenizers for native counts
                                req_counts['native_input_tokens'] = 0
                                req_counts['native_output_tokens'] = 0
                            # Get tiktoken counts
                            tiktoken_input_tokens = self.oai_tokenizer.encode(request['input'])
                            req_counts['tiktoken_input_tokens'] = len(tiktoken_input_tokens)
                            tiktoken_output_tokens = self.oai_tokenizer.encode(request['output'])
                            req_counts['tiktoken_output_tokens'] = len(tiktoken_output_tokens)
                            # Get naive token estimates
                            naive_low_input_tokens = naive_tokens_low(request['input'])
                            req_counts['naive_low_input_tokens'] = naive_low_input_tokens
                            naive_low_output_tokens = naive_tokens_low(request['output'])
                            req_counts['naive_low_output_tokens'] = naive_low_output_tokens

                            naive_high_input_tokens = naive_tokens_high(request['input'])
                            req_counts['naive_high_input_tokens'] = naive_high_input_tokens
                            naive_high_output_tokens = naive_tokens_high(request['output'])
                            req_counts['naive_high_output_tokens'] = naive_high_output_tokens

                            ep_reqs_counts.append(req_counts)
                        # Sum episode token counts
                        ep_counts_summed: dict = dict()

                        native_input_sum = sum([req['native_input_tokens'] for req in ep_reqs_counts])
                        ep_counts_summed['native_input'] = native_input_sum
                        native_output_sum = sum([req['native_output_tokens'] for req in ep_reqs_counts])
                        ep_counts_summed['native_output'] = native_output_sum

                        tiktoken_input_sum = sum([req['tiktoken_input_tokens'] for req in ep_reqs_counts])
                        ep_counts_summed['tiktoken_input'] = tiktoken_input_sum
                        tiktoken_output_sum = sum([req['tiktoken_output_tokens'] for req in ep_reqs_counts])
                        ep_counts_summed['tiktoken_output'] = tiktoken_output_sum

                        naive_low_input_sum = sum([req['naive_low_input_tokens'] for req in ep_reqs_counts])
                        ep_counts_summed['naive_low_input'] = naive_low_input_sum
                        naive_low_output_sum = sum([req['naive_low_output_tokens'] for req in ep_reqs_counts])
                        ep_counts_summed['naive_low_output'] = naive_low_output_sum

                        naive_high_input_sum = sum([req['naive_high_input_tokens'] for req in ep_reqs_counts])
                        ep_counts_summed['naive_high_input'] = naive_high_input_sum
                        naive_high_output_sum = sum([req['naive_high_output_tokens'] for req in ep_reqs_counts])
                        ep_counts_summed['naive_high_output'] = naive_high_output_sum

                        experiment_ep_req_sums.append(ep_counts_summed)

                    experiment_sums: dict = {'native_input': 0,
                                             'native_output': 0,
                                             'tiktoken_input': 0,
                                             'tiktoken_output': 0,
                                             'naive_low_input': 0,
                                             'naive_low_output': 0,
                                             'naive_high_input': 0,
                                             'naive_high_output': 0}
                    for experiment_ep_req_sum in experiment_ep_req_sums:
                        for tkn_sum in experiment_ep_req_sum:
                            experiment_sums[tkn_sum] += experiment_ep_req_sum[tkn_sum]
                    game_exp_tkns.append(experiment_sums)

                game_tkn_sums: dict = {'native_input': 0,
                                       'native_output': 0,
                                       'tiktoken_input': 0,
                                       'tiktoken_output': 0,
                                       'naive_low_input': 0,
                                       'naive_low_output': 0,
                                       'naive_high_input': 0,
                                       'naive_high_output': 0}
                for game_exp_tkns_ in game_exp_tkns:
                    for tkn_sum in game_exp_tkns_:
                        game_tkn_sums[tkn_sum] += game_exp_tkns_[tkn_sum]
                all_games_tkn_counts.append(game_tkn_sums)

            model_tkn_sums: dict = {'native_input': 0,
                                   'native_output': 0,
                                   'tiktoken_input': 0,
                                   'tiktoken_output': 0,
                                   'naive_low_input': 0,
                                   'naive_low_output': 0,
                                   'naive_high_input': 0,
                                   'naive_high_output': 0}
            for game_tkns in all_games_tkn_counts:
                for tkn_sum in game_tkns:
                    model_tkn_sums[tkn_sum] += game_tkns[tkn_sum]

            self.model_tkn_counts[model] = model_tkn_sums

    def get_episode_requests(self, episode_path: str):
        """Get raw requests contents for an episode."""
        # Load episode requests.json
        with open(f"{episode_path}{os.sep}requests.json", encoding='utf-8') as requests_file:
            raw_episode_requests = json.load(requests_file)
        episode_requests: list = list()
        for request in raw_episode_requests:
            if 'inputs' not in request['manipulated_prompt_obj']:
                # Skip programmatic and similar non-LLM responses
                continue
            input_context = request['manipulated_prompt_obj']['inputs']
            output = request['raw_response_obj']['response']
            # Remove input context from output
            output_cleaned = output.replace(input_context, "")
            request_content: dict = {'input': input_context, 'output': output_cleaned}
            episode_requests.append(request_content)
        return episode_requests

    def get_average_token_counts(self):
        self.count_benchmark_tokens()
        model_count = len(self.model_tkn_counts)
        native_tokenizer_count = len(self.hf_tokenizers)
        all_model_tkn_totals: dict = {'native_input': 0,
                                      'native_output': 0,
                                      'tiktoken_input': 0,
                                      'tiktoken_output': 0,
                                      'naive_low_input': 0,
                                      'naive_low_output': 0,
                                      'naive_high_input': 0,
                                      'naive_high_output': 0}
        for model, counts in self.model_tkn_counts.items():
            for count in counts:
                all_model_tkn_totals[count] += counts[count]

        for count in all_model_tkn_totals:
            if count == 'native_input' or count == 'native_output':
                self.average_tkn_cnt[count] = round(all_model_tkn_totals[count] / native_tokenizer_count)
            else:
                self.average_tkn_cnt[count] = round(all_model_tkn_totals[count] / model_count)

    def set_openrouter_models(self, openrouter_models: list):
        """
        Set which models to get current OpenRouter pricing for.
        :param openrouter_models: List of OpenRouter model IDs.
        :return: Nothing, sets class attribute.
        """
        self.openrouter_models = openrouter_models

    def get_openrouter_models_from_file(self, filename: str = "cost_estimator_target_models.json"):
        """
        Gets target OpenRouter model IDs from premade file.
        :param filename: The file name of the JSON file holding the list of target OpenRouter model IOs.
        :return: None, sets class instance attribute.
        """
        with open(filename, 'r', encoding='utf-8') as target_models_file:
            models_from_file = json.load(target_models_file)
        self.set_openrouter_models(models_from_file)

    def get_current_openrouter_pricing(self):
        openrouter_url = "https://openrouter.ai/api/v1/models"
        available_models_response = requests.get(openrouter_url)
        available_models = available_models_response.json()
        found_models: list = list()
        for model_entry in available_models['data']:
            if model_entry['id'] in self.openrouter_models:
                model_pricing: dict = dict()
                model_pricing['input'] = model_entry['pricing']['prompt']
                model_pricing['output'] = model_entry['pricing']['completion']
                self.openrouter_prices[model_entry['id']] = model_pricing
                found_models.append(model_entry['id'])
        # Log models to estimate price for that are not currently offered on OpenRouter
        unavailable_models: list = [model_id for model_id in self.openrouter_models if model_id not in found_models]
        logging.info(f"The following models that were given to estimate price for are not available on OpenRouter "
                     f"currently: {', '.join(unavailable_models)}")

    def estimate_benchmark_costs(self, print_costs: bool = False) -> dict:
        """
        Use pricing information and average benchmark tokens to estimate costs to run benchmark for static model set
        and set openrouter models.
        :return: Cost estimate dict.
        """
        estimated_costs: dict = dict()
        # Calculate openrouter models costs estimate
        for openrouter_model in self.openrouter_models:
            estimated_costs[openrouter_model] = dict()
            for count_type in self.average_tkn_cnt:
                if "input" in count_type:
                    estimated_costs[openrouter_model][count_type] = self.average_tkn_cnt[count_type] * \
                                                                float(self.openrouter_prices[openrouter_model]['input'])
                if "output" in count_type:
                    estimated_costs[openrouter_model][count_type] = self.average_tkn_cnt[count_type] * \
                                                                float(self.openrouter_prices[openrouter_model]['output'])
        # Calculate total cost estimate for benchmark and model set
        total_cost: dict = {'native_input': 0,
                            'native_output': 0,
                            'tiktoken_input': 0,
                            'tiktoken_output': 0,
                            'naive_low_input': 0,
                            'naive_low_output': 0,
                            'naive_high_input': 0,
                            'naive_high_output': 0}
        for model, costs in estimated_costs.items():
            for cost in costs:
                total_cost[cost] += costs[cost]
        estimated_costs['total'] = total_cost
        logging.info(f"Estimated costs: {estimated_costs}")
        if print_costs:
            for model, costs in estimated_costs.items():
                print("model:", model)
                print(costs)

        self.estimated_costs = estimated_costs

        return self.estimated_costs

    def estimate_to_csv(self):
        """
        Convert cost estimate dict to CSV and save it to file.
        :return: None, file saved.
        """
        estimate_df = pd.DataFrame.from_dict(self.estimated_costs)
        csv_filename = f"{self.benchmark}_cost_estimate_{datetime.now().strftime('%Y-%m-%d_%H%M')}.csv"
        estimate_df.to_csv(csv_filename)


if __name__ == "__main__":
    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument('-b', '--benchmark', help="Set the benchmark version/directory to estimate with. Defaults to 'v3.0'.")
    argparser.add_argument('-i', '--ignore', help="Set the benchmark models with existing results to ignore for the estimation. Takes a comma-separated list.")
    argparser.add_argument('-t', '--target_models', help="Set the models to estimate costs for directly. Takes a comma-separated list.")
    argparser.add_argument('-f', '--target_models_file', help="Set the JSON file with model list to estimate costs for.")
    argparser.add_argument('-v', '--verbose', action='store_true', help="Print the cost estimation to console.")
    argparser.add_argument('-c', '--csv_skip', action='store_true', help="Do not save the cost estimate as a CSV file.")
    args = argparser.parse_args()
    extra_args: dict = dict()
    if args.benchmark:
        extra_args['benchmark'] = args.benchmark
    if args.ignore:
        extra_args['ignore_models'] = args.ignore.split(",")

    costimator = CostEstimator(**extra_args)

    if args.target_models:
        costimator.set_openrouter_models(args.target_models.split(","))
    if args.target_models_file:
        costimator.get_openrouter_models_from_file(args.target_models_file)

    costimator.get_current_openrouter_pricing()

    if args.verbose:
        costimator.estimate_benchmark_costs(print_costs=True)
    else:
        costimator.estimate_benchmark_costs()

    if not args.csv_skip:
        costimator.estimate_to_csv()
