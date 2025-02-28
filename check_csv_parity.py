import os
from typing import Tuple, List


def check_csv_parity(root_folder) -> Tuple[List, List, List, List]:
    model_directories: list = [directory for directory in os.listdir(root_folder)
                               if os.path.isdir(os.path.join(root_folder, directory))]
    # checking raw.csv:
    raw_csv_models: list = list()
    raw_csv_models_without_directory: list = list()
    raw_csv_path = os.path.join(root_folder, "raw.csv")
    with open(raw_csv_path, 'r', encoding='utf-8') as raw_csv_file:
        raw_csv = raw_csv_file.read()
    raw_csv_lines = raw_csv.split("\n")
    for line in raw_csv_lines[1:]:
        if not line:
            continue
        cur_model = line.split(",")[2]
        if cur_model not in raw_csv_models:
            raw_csv_models.append(cur_model)
        if cur_model not in model_directories:
            print(f"{cur_model} in raw.csv, but has no directory for {root_folder}!")
            if cur_model not in raw_csv_models_without_directory:
                raw_csv_models_without_directory.append(cur_model)
    # checking results.csv:
    results_csv_models: list = list()
    results_csv_models_without_directory: list = list()
    results_csv_path = os.path.join(root_folder, "results.csv")
    with open(results_csv_path, 'r', encoding='utf-8') as results_csv_file:
        results_csv = results_csv_file.read()
    results_csv_lines = results_csv.split("\n")
    for line in results_csv_lines[1:]:
        if not line:
            continue
        cur_model = line.split(",")[0]
        if cur_model not in results_csv_models:
            results_csv_models.append(cur_model)
        if cur_model not in model_directories:
            print(f"{cur_model} in results.csv, but has no directory for {root_folder}!")
            if cur_model not in results_csv_models_without_directory:
                results_csv_models_without_directory.append(cur_model)
    # check for model directories that are not covered in the CSVs:
    model_directories_not_in_raw_csv: list = list()
    model_directories_not_in_results_csv: list = list()
    for model_id in model_directories:
        if model_id not in raw_csv_models:
            print(f"{cur_model} has directory, but is missing in raw.csv for {root_folder}!")
            if model_id not in model_directories_not_in_raw_csv:
                model_directories_not_in_raw_csv.append(model_id)
        if model_id not in results_csv_models:
            print(f"{cur_model} has directory, but is missing in results.csv for {root_folder}!")
            if model_id not in model_directories_not_in_results_csv:
                model_directories_not_in_results_csv.append(model_id)

    issue: bool = False
    if raw_csv_models_without_directory:
        print(f"{len(raw_csv_models_without_directory)} models in raw.csv without directory for {root_folder}.")
        issue = True
    if results_csv_models_without_directory:
        print(f"{len(results_csv_models_without_directory)} models in results.csv without directory for {root_folder}.")
        issue = True
    if model_directories_not_in_raw_csv:
        print(f"{len(model_directories_not_in_raw_csv)} models with directory missing in raw.csv for {root_folder}.")
        issue = True
    if model_directories_not_in_raw_csv:
        print(f"{len(model_directories_not_in_results_csv)} models with directory missing in results.csv for {root_folder}.")
        issue = True
    if not issue:
        print(f"Full parity of model directories and CSVs for {root_folder}!")

    return raw_csv_models_without_directory, results_csv_models_without_directory, model_directories_not_in_raw_csv, model_directories_not_in_results_csv


if __name__ == "__main__":
    v1_6_csv_parity = check_csv_parity("v1.6")
    print(v1_6_csv_parity)

    v1_6_backends_csv_parity = check_csv_parity("v1.6_backends")
    print(v1_6_backends_csv_parity)

    v1_6_multimodal_csv_parity = check_csv_parity("v1.6_multimodal")
    print(v1_6_multimodal_csv_parity)

    v1_6_quantized_csv_parity = check_csv_parity("v1.6_quantized")
    print(v1_6_quantized_csv_parity)

    v2_0_quantized_csv_parity = check_csv_parity("v2.0")
    print(v2_0_quantized_csv_parity)