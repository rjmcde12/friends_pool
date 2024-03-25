# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
import pandas as pd
import numpy as np
import requests
import json
import time
import random
import gspread
from google.oauth2.service_account import Credentials
from dash import Dash, dcc, html, Input, Output, State, Patch, MATCH, ALLSMALLER, callback, dash_table
import dash_bootstrap_components as dbc
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

scopes = [
    'https://www.googleapis.com/auth/spreadsheets'
]

creds = Credentials.from_service_account_file('credentials.json', scopes=scopes)
client = gspread.authorize(creds)


# # team_standings
# team_standings_id = '1SxyZPqzDTHG0C24GsF5htjU9Yad_EOohg0Md12DcLsc'
# team_standings_sheet = client.open_by_key(team_standings_id)
# team_standings_google = team_standings_sheet.sheet1

# +
default_table_style = {
    'overflowX': 'auto',
    'border': '1px solid #dee2e6',
    'borderCollapse': 'collapse',
    'width': '100%',
    'marginBottom': '0'
}

default_header_style = {
    'backgroundColor': '#f8f9fa',
    'fontWeight': 'bold',
    'border': '1px solid #dee2e6',
    'textAlign': 'center'
}

default_cell_style = {
    'textAlign': 'left',
    'padding': '8px',
    'border': '1px solid #dee2e6'
}

default_conditional_style = [
    {
        'if': {'row_index': 'odd'},
        'backgroundColor': 'rgba(248, 248, 248, 0.8)'
    },
    {
        'if': {'row_index': 'even'},
        'backgroundColor': 'rgba(255, 255, 255, 0.8)'
    }
]

default_styles = {
    'style_table': default_table_style,
    'style_header': default_header_style,
    'style_cell': default_cell_style,
    'style_data_conditional': default_conditional_style
}

# +
# # draft_df
# draft_id = '1emw0Sbeqtju8YihrprA65MnsR0Yjdc-MyF-NnmI4vj4'
# draft_sheet = client.open_by_key(draft_id)
# draft_google = draft_sheet.sheet1

# final_results_df
final_results_id = '1BH96Cwdj1aW8v8PEjGE3Qb6F0ndo6TfdVbTS7RAq4qk'
final_results_sheet = client.open_by_key(final_results_id)
final_results_google = final_results_sheet.sheet1


# +
draft_df = pd.read_csv('draft_results.csv', index_col=None)
# draft_data = draft_google.get_all_values()
# draft_df = pd.DataFrame(draft_data[1:], columns=draft_data[0])

final_results_data = final_results_google.get_all_values()
final_results_df = pd.DataFrame(final_results_data[1:], columns=final_results_data[0])
final_results_df.loc[:,'result'] = final_results_df['result'].astype(int)
final_results_df.loc[:,'seed'] = final_results_df['seed'].astype(int)
final_results_df.loc[:,'round'] = final_results_df['round'].astype(int)


# -

def pull_today_scores():
    url = 'https://ncaa-api.henrygd.me/scoreboard/basketball-men/d1'
    try:
        response = requests.get(url)
    
        if response.status_code == 200:
            score_data = response.json()
    
        else:
            print('Failed to fetch data from the NCAA website:', response.status_code)
    except Exception as e:
        print('An error occurred:', e)

    return score_data


def create_today_scores_dfs(score_data):
    game_list = score_data['games']

    full_game_results = []
    team_game_results = []
    for i, game in enumerate(game_list):
        game_id = game['game']['gameID']
        away_team = game['game']['away']['names']['short']
        away_score = game['game']['away']['score']
        away_seed = game['game']['away']['seed']
        away_result = game['game']['away']['winner']
        game_status = game['game']['gameState']
        bracket_id = game['game']['bracketId']
        region = game['game']['bracketRegion']
        game_round = game['game']['bracketRound']
        home_team = game['game']['home']['names']['short']
        home_score = game['game']['home']['score']
        home_seed = game['game']['home']['seed']
        home_result = game['game']['home']['winner']
    
        full_game_dict = {
            'game_id':game_id, 'bracket_id':bracket_id, 'region':region, 'round':game_round, 'game_status':game_status,
            'away_team':away_team, 'away_seed':away_seed,'away_score':away_score,'away_result':away_result,
            'home_team':home_team, 'home_seed':home_seed,'home_score':home_score,'home_result':home_result
        }
        away_game_dict = {
            'game_id':game_id, 'bracket_id':bracket_id, 'region':region, 'round':game_round, 'game_status':game_status,
            'team':away_team, 'seed':away_seed,'score':away_score,'result':away_result
        }
        home_game_dict = {
            'game_id':game_id, 'bracket_id':bracket_id, 'region':region, 'round':game_round, 'game_status':game_status,
            'team':home_team, 'seed':home_seed,'score':home_score,'result':home_result
        }
        full_game_results.append(full_game_dict)
        team_game_results.append(away_game_dict)
        team_game_results.append(home_game_dict)
    
    today_by_game_df = pd.DataFrame(full_game_results)
    today_by_team_df = pd.DataFrame(team_game_results)
    today_by_team_df = today_by_team_df[today_by_team_df['seed'] !='']
    
    return today_by_game_df, today_by_team_df


def update_final_results_df(today_by_team_df, final_results_df):
    final_results_df = final_results_df.copy()
    today_final_team_df = today_by_team_df[today_by_team_df['game_status'] == 'final']
    updated_final_results_df = today_final_team_df[~today_final_team_df['game_id'].isin(final_results_df['game_id'].tolist())]
    round_map = {'First Round':1, 'Second Round':2, 'Sweet 16':3, 'Elite Eight':4, 'Final Four':5, 'Championship':6}
    updated_final_results_df.loc[:,'round'] = updated_final_results_df['round'].map(round_map)
    updated_final_results_df.loc[:,'seed'] = updated_final_results_df['seed'].astype(int)
    updated_final_results_df.loc[:,'round'] = updated_final_results_df['round'].astype(int)
    updated_final_results_df.loc[:,'result'] = updated_final_results_df['result'].apply(lambda x: 1 if x == True else 0)
    updated_final_results_df.loc[:,'result'] = updated_final_results_df['result'].astype(int)
    updated_final_results_df.loc[:,'pool_points'] = (
        updated_final_results_df['round']* updated_final_results_df['result'] * updated_final_results_df['seed']
    )
    final_results_df = pd.concat([final_results_df, updated_final_results_df], axis=0)
    final_results_df.loc[:,'result'] = final_results_df['result'].astype(int)
    final_results_df.loc[:,'seed'] = final_results_df['seed'].astype(int)
    final_results_df.loc[:,'round'] = final_results_df['round'].astype(int)
    return final_results_df


def create_team_standings(final_results_df, draft_df):
    final_results_df['pool_points'] = final_results_df['pool_points'].astype(int)
    team_standings = pd.DataFrame(final_results_df.groupby('team')['pool_points'].sum())
    eliminated_teams = final_results_df.groupby('team')['result'].apply(lambda x: (x == 0).any())
    team_standings['eliminated'] = eliminated_teams
    team_standings = pd.merge(team_standings, draft_df, on='team')
    team_standings = team_standings[['friend','team','seed','pool_points','eliminated', 'overall']]
    team_standings.reset_index(drop=True, inplace=True)
    return team_standings


def create_friend_standings(draft_df, team_standings, pts_left):
    draft_df = draft_df.drop(columns='friend')
    friend_team_results = pd.merge(draft_df, team_standings, on='team')
    friend_team_results.loc[:,'pool_points'] = friend_team_results['pool_points'].astype(int)
    friend_team_results.loc[:,'eliminated'] = friend_team_results['eliminated'].astype(int)
    friend_standings = pd.DataFrame(friend_team_results.groupby('friend')[['pool_points', 'eliminated']].sum())
    friend_standings['Teams Left'] = 8 - friend_standings['eliminated']
    friend_standings.drop(columns='eliminated', inplace=True)
    friend_standings.loc[:,'pool_points'] = friend_standings['pool_points'].astype(int)
    friend_standings = pd.merge(friend_standings, pts_left, on='friend')
    friend_standings['pts_left'] = friend_standings['pts_left'] + friend_standings['pool_points']
    friend_standings.sort_values(by=['pool_points', 'pts_left'], ascending=False, inplace=True)
    friend_standings.reset_index(drop=True, inplace=True)
    friend_standings.index = friend_standings.index + 1
    friend_standings.index.name = 'Place'
    friend_standings = friend_standings.rename(columns = {'pool_points':'Total Points', 'friend':'Friend*', 'pts_left':'Max Points'})
    friend_standings.reset_index(inplace=True)
    return friend_standings


def create_pts_left_df(final_results_df, draft_df):
    team_last_round = final_results_df.groupby('team').agg({'round':'max','pool_points':'sum'}).reset_index()
    possible_points = pd.merge(draft_df, team_last_round, on='team')
    possible_points.drop(columns='round_x', inplace=True)
    possible_points.rename(columns={'round_y':'round'}, inplace=True)
    eliminated = team_standings[['team', 'eliminated']]
    possible_points = pd.merge(possible_points, eliminated, on='team')
    
    friends_list = draft_df['friend'].unique().tolist()
    pts_left_list = []
    for friend in friends_list:
        poss_pts = possible_points[possible_points['friend']==friend].reset_index(drop=True)
        poss_pts = poss_pts[poss_pts['eliminated']==False]
        
        if len(poss_pts) != 0:
            max_round = poss_pts['round'].max()
            pre_tourney = poss_pts[poss_pts['round']=='']
            pre_tourney_pts = pre_tourney['r1'].sum()
            pre_tourney_pts = poss_pts_1 = poss_pts_2 = poss_pts_3 = poss_pts_4 = post_r5_pts = 0
        
            poss_pts_1 = poss_pts[poss_pts['round']==1]
            if len(poss_pts_1) != 0:
                rd_df = poss_pts_1.groupby(poss_pts_1['matchup_id'].str[1:])['r2'].max()
                post_r1_pts = poss_pts_1['r2'].sum()
            else:
                post_r1_pts = 0
        
            poss_pts_2 = poss_pts[poss_pts['round']==2]
            if len(poss_pts_2) != 0:
                rd_df = poss_pts_2.groupby(poss_pts_2['matchup_id'].str[2:])['r3'].max()
                post_r2_pts = poss_pts_2['r3'].sum()
            else:
                post_r2_pts = 0
        
            poss_pts_3 = poss_pts[poss_pts['round']==3]
            if len(poss_pts_3) != 0:
                rd_df = poss_pts_3.groupby(poss_pts_3['matchup_id'].str[3:])['r4'].max()
                post_r3_pts = poss_pts_3['r4'].sum()
            else:
                post_r3_pts = 0
        
            poss_pts_4 = poss_pts[poss_pts['round']==4]
            if len(poss_pts_4) != 0:
                rd_df = poss_pts_4.groupby(poss_pts_4['matchup_id'].str[4:5])['r5'].max()
                post_r4_pts = poss_pts_4['r5'].sum()
            else:
                post_r4_pts = 0
            
            poss_pts_5 = poss_pts[poss_pts['round']==5]
            if len(poss_pts_5) != 0:
                rd_df = poss_pts_5.groupby(poss_pts_5['matchup_id'].str[4:5])['r5'].max()
                post_r5_pts = poss_pts_5['r6'].max()
            else:
                post_r5_pts = 0
        
            total_pts_left = pre_tourney_pts + post_r1_pts + post_r2_pts + post_r3_pts + post_r4_pts + post_r5_pts
            
            pts_left_dict = {'friend':friend, 'pts_left':total_pts_left}
            
            pts_left_list.append(pts_left_dict)
            
    pts_left_df = pd.DataFrame(pts_left_list)
    return pts_left_df


def format_final_tables(team_standings, final_results_df):
    formatted_team_standings = team_standings.copy()
    formatted_team_standings['eliminated'] = formatted_team_standings['eliminated'].apply(lambda x: 'Yes' if x == False else 'No')
    formatted_team_standings = formatted_team_standings.sort_values(by='overall', ascending = True)
    formatted_team_standings = formatted_team_standings.rename(columns={
        'friend':'Friend*','team':'Team','seed':'Seed','pool_points':'Total Points',
        'eliminated':'Active', 'overall':'Pick #'
    })
    
    formatted_final_results = final_results_df.copy()
    formatted_final_results['round'] = formatted_final_results['round'].astype('int')
    formatted_final_results = formatted_final_results.sort_values(by=['round' ,'game_id','result'], ascending=False)
    formatted_final_results = formatted_final_results.iloc[:,:8]
    formatted_final_results = formatted_final_results.rename(columns={'region':'Region','round':'Round','team':'Team','seed':'Seed',
                                        'score':'Final Score','result':'Result','pool_points':'Pool Points'})
    formatted_final_results['Result'] = formatted_final_results['Result'].apply(lambda x: 'Win' if x == 1 else 'Loss')
    formatted_final_results = formatted_final_results.drop(columns='game_status')
    return formatted_final_results, formatted_team_standings


score_data = pull_today_scores()
today_by_game_df, today_by_team_df = create_today_scores_dfs(score_data)
final_results_df = update_final_results_df(today_by_team_df, final_results_df)
team_standings = create_team_standings(final_results_df, draft_df)
pts_left = create_pts_left_df(final_results_df, draft_df)
friend_standings = create_friend_standings(draft_df, team_standings, pts_left)
formatted_final_results, formatted_team_standings = format_final_tables(team_standings, final_results_df)

# +
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css])
server = app.server

app.layout = html.Div(className='dbc', children=[
    dbc.Container(children = [
    html.H1('Friendly* Pool Standings', style={'textAlign':'center'}),
    html.Div(children='*Alexander is obviously not our friend', style={'textAlign':'right'}),
    dbc.Row([
            dbc.Card(
                dbc.Table.from_dataframe(friend_standings, striped=True, bordered=True, hover=True,
                                        style={'size':'auto','overflow':'auto'})
            ),
            html.Div(children=[
                dbc.Tabs(
                        [
                            dbc.Tab(label='Game Results', tab_id='game-results'),
                            dbc.Tab(label='School Results', tab_id='school-results')
                        ],
                id='tab-chosen',
                active_tab='game-results'
            ),
                html.Div(id='tab-table', style={'size':'auto','overflow':'auto'})
            ]),
    ])
    ])
    
])

@app.callback(
    Output('tab-table', 'children'),
    [Input('tab-chosen', 'active_tab')]
)

def table_shown(tab_chosen):
    if tab_chosen == 'game-results':
        table_df = formatted_final_results
        # table_df['round'] = table_df['round'].astype('int')
        # table_df = table_df.sort_values(by=['round' ,'game_id','result'], ascending=False)
        # table_df = table_df.iloc[:,:8]
        # table_df = table_df.rename(columns={'region':'Region','round':'Round','team':'Team','seed':'Seed',
        #                          'score':'Final Score','result':'Result','pool_points':'Pool Points'})
        # table_df = table_df.drop(columns='game_status')

    else:
        table_df = formatted_team_standings
        # table_df['eliminated'] = table_df['eliminated'].apply(lambda x: 'Yes' if x == False else 'No')
        # table_df = table_df.sort_values(by='overall', ascending = True)
        # table_df = table_df.rename(columns={
        #     'friend':'Friend*','team':'Team','seed':'Seed','pool_points':'Total Points',
        #     'eliminated':'Active', 'overall':'Pick #'
        # })

    table_shown = dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in table_df.columns],
        data=table_df.to_dict('records'),
        page_size=16,
        # style_table={'overflowX': 'auto'},
        style_data={'whiteSpace': 'normal', 'height': 'auto'},
        filter_action='native',  
        sort_action='native',    
        sort_mode='multi',
        **default_styles
    )

    return table_shown
        
final_results_google.clear()
final_results_google.update(range_name='A1', values=[final_results_df.columns.tolist()])
final_results_to_google = final_results_df.values.tolist()
final_results_google.update(range_name='A2', values=final_results_to_google)

if __name__ == '__main__':
    app.run_server(debug=True)
    # app.run_server(debug=True, port=8051)
