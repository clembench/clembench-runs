import pandas as pd
file_path = '../../v1.6_multimodal/results.csv'
short_model_names = {'idefics-9b-instruct':'idefics-9B', 'idefics-80b-instruct':'idefics-80B',  'claude-3-opus-20240229': 'claude-3', 'gpt-4o-2024-05-13': 'gpt-4o', 'gemini-1.5-flash-latest': 'gemini-1.5', 'gpt-4-1106-vision-preview': 'gpt-4v-1106', 'llava-1.5-13b-hf': 'llv-1.5-13b', 'llava-v1.6-34b-hf': 'llv-v1.6-34b', 'llava-v1.6-vicuna-13b-hf': 'llv-v1.6-13b'}

df = pd.read_csv(file_path)

# add label 'model' to the first column
df = df.rename(columns={'Unnamed: 0': 'model'})

# loop over each row and change the model name to the short name
# delete the row with the model name if it is not in the short_model_names
for index, row in df.iterrows():
    model_name = row['model'].split('--')[0].replace('-t0.0', '')
    if model_name in short_model_names:
        df.at[index, 'model'] = short_model_names[model_name]
    else:
        df = df.drop(index)



# ROW index to Column name
# 1 - clemscore
# 2 - played
# 3 - quality score
# 4 - matchit played
# 5 - matchit quality score
# 7 - matchit_1q played
# 8 - matchit_1q quality score
# 10 - matchit_5q played
# 11 - matchit_5q quality score
# 25 - matchit_info played
# 26 - matchit_info quality score
# 28 - ee played
# 29 - ee quality score
# 31 - ee_gr played
# 32 - ee_gr quality score
# 34 - ee_qa played
# 35 - ee_qa quality score
# 37 - g2x played
# 38 - g2x quality score
# 40 - reference played
# 41 - reference quality score

# order the rows by the value in the column with the name '-, clemscore'
df = df.sort_values(by='-, clemscore', ascending=False)

# replace the values in cells with the character '/' if they are equal to nan
df = df.fillna('/')


# loop over each row and print the model name and column with the index 2
for index, row in df.iterrows():
    print(f"\multirow[t]{{2}}{{*}}{{{row['model']}}} & \% played & {row[2]} & {row[40]} & {row[4]}  & {row[7]}  & {row[10]}  & {row[25]}  & {row[37]}  & {row[28]} & {row[34]} & {row[31]} "
          f"\\\\ {row[1]} & qlty score & {row[3]} & {row[41]} & {row[5]}  & {row[8]}  & {row[11]}  & {row[26]}  & {row[38]}  & {row[29]} & {row[35]} & {row[32]} \\\\ \midrule")
    # print(row['model'], row[1])

