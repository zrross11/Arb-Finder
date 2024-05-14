import os
import requests
import json
from dotenv import load_dotenv
import pandas as pd

def get_odds(sport):
    load_dotenv()
    ODDS_API_KEY = os.getenv("ODDS_API_KEY")

    sports_response = requests.get(f'https://api.the-odds-api.com/v4/sports/{sport}/odds/?regions=us&markets=h2h', params={
        'api_key': ODDS_API_KEY
    })

    upcoming_odds = json.loads(sports_response.text)

    df = pd.DataFrame(upcoming_odds)

    # EST Commence Time
    df['commence_time'] = pd.to_datetime(df['commence_time'])
    df['commence_time'] = df['commence_time'].dt.tz_convert('US/Eastern')
    df['commence_time'] = df['commence_time'].dt.strftime('%Y-%m-%d %I:%M:%S %p')
        
    rows = []
    g = 0
    for game in df['bookmakers']:
        for i in range(len(game)):
            bookmaker_name = game[i]['title']
            team1 = game[i]['markets'][0]['outcomes'][0]['name']
            team2 = game[i]['markets'][0]['outcomes'][1]['name']
            odds_team1 = game[i]['markets'][0]['outcomes'][0]['price']
            odds_team2 = game[i]['markets'][0]['outcomes'][1]['price']
            last_update = game[i]['last_update']
            rows.append([bookmaker_name, team1, odds_team1, team2, odds_team2, last_update, df['commence_time'][g]])
        g += 1
        
    print(rows)

    df_odds = pd.DataFrame(rows, columns=['Bookmaker', 'Team1', 'Odds_Team1', 'Team2', 'Odds_Team2', 'Last_Updated', 'commence_time'])

    merged_df1 = pd.merge(df, df_odds, left_on=['away_team', 'home_team', 'commence_time'], right_on=['Team1', 'Team2', 'commence_time'], how='left')
    merged_df2 = pd.merge(df, df_odds, left_on=['home_team', 'away_team', 'commence_time'], right_on=['Team1', 'Team2', 'commence_time'], how='left')
    merged_df = pd.concat([merged_df1, merged_df2], ignore_index=True)

    
    merged_df.dropna(subset=['Team1', 'Team2'], inplace=True)
    merged_df.drop(['id', 'bookmakers'], axis=1, inplace=True)

    #EST Last Updated
    merged_df['Last_Updated'] = pd.to_datetime(merged_df['Last_Updated'])
    merged_df['Last_Updated'] = merged_df['Last_Updated'].dt.tz_convert('US/Eastern')
    merged_df['Last_Updated'] = merged_df['Last_Updated'].dt.strftime('%Y-%m-%d %I:%M:%S %p')

    sorted_df = merged_df.sort_values(by='commence_time')

    return sorted_df


def calculate_margins(dataframe):
    # Group the dataframe by game
    grouped = dataframe.groupby(['commence_time', 'home_team', 'away_team'])
    
    # Initialize an empty list to store the results
    results = []
    
    # Iterate over each group
    for _, group in grouped:
        # Calculate the total probability for each matchup
        margins = []
        
        # Iterate over each row in the group
        for i in range(len(group)):
            for j in range(len(group)):
                # Calculate the total probability for each bookmaker pair
                margin = (1 / group.iloc[i]['Odds_Team1']) + (1 / group.iloc[j]['Odds_Team2'])
                margins.append({
                    'market_margin': margin,
                    'Odds_Team1': group.iloc[i]['Odds_Team1'],
                    'Odds_Team2': group.iloc[j]['Odds_Team2'],
                    'Bookmaker1': group.iloc[i]['Bookmaker'],
                    'Bookmaker1_LastUpdated': group.iloc[i]['Last_Updated'],
                    'Bookmaker2': group.iloc[j]['Bookmaker'],
                    'Bookmaker2_LastUpdated': group.iloc[j]['Last_Updated'], # Added 'Last_Updated' to 'Bookmaker2_LastUpdated``
                    # 'Home Team': group.iloc[i]['home_team'],
                    # 'Away Team': group.iloc[j]['away_team'],
                    'Commence Time': group.iloc[i]['commence_time'],
                    'Team1': group.iloc[i]['Team1'],
                    'Team2': group.iloc[j]['Team2']
                })        
        # Append the results to the list
        results.extend(margins)

    # Convert the results to a dataframe
    results_df = pd.DataFrame(results)
    
    # Sort the dataframe by the smallest total probability
    sorted_df = results_df.sort_values(by='market_margin')
    top_5 = sorted_df.head(5)

    return top_5