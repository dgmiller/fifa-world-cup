import numpy as np
import pandas as pd

def gen_csv_from_xlsx(xlfile):
    match_df = pd.read_excel(xlfile, sheet_name='matches')
    group_df = pd.read_excel(xlfile, sheet_name='groups')
    print(match_df.head())

    group_dict = dict(zip(group_df['team'].values, group_df['group'].values))

    team_arr = match_df['team'].values.copy()
    goals_for_arr = match_df['goals_for'].values.copy()
    on_target_arr = match_df['on_target'].values.copy()

    match_dict = {'group':[],
                  'team':team_arr,
                  'game':match_df['game'].values.copy(),
                  'opponent':[],
                  'attempts':match_df['attempts'].values.copy(),
                  'on_target':on_target_arr,
                  'off_target':match_df['off_target'].values.copy(),
                  'goals_for':goals_for_arr,
                  'goals_against':[],
                  'on_target_against':[]}

    for i in np.arange(1, match_df['team'].shape[0], 2):
        match_dict['opponent'].append(team_arr[i])
        match_dict['opponent'].append(team_arr[i-1])

        match_dict['goals_against'].append(goals_for_arr[i])
        match_dict['goals_against'].append(goals_for_arr[i-1])

        match_dict['on_target_against'].append(on_target_arr[i])
        match_dict['on_target_against'].append(on_target_arr[i-1])
    
    for i in range(match_df.shape[0]):
        if match_dict['game'][i] < 4:
            match_dict['group'].append(group_dict[match_dict['team'][i]])

        elif match_dict['game'][i] == 4:
            match_dict['group'].append('W')

        elif match_dict['game'][i]==5:
            match_dict['group'].append('X')

        elif match_dict['game'][i]==6:
            match_dict['group'].append('Y')

        elif match_dict['game'][i]==7:
            match_dict['group'].append('Z')

        else:
            match_dict['group'].append('?')

    return pd.DataFrame(match_dict)

if __name__ == "__main__":
    result = gen_csv_from_xlsx('./UEFA2020.xlsx')
    print(result)
    result.to_csv('UEFA2020.csv',index=False)