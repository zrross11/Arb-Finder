import os
import requests
import json
import pandas as pd
from dotenv import load_dotenv


load_dotenv()
ODDS_API_KEY = os.getenv("ODDS_API_KEY")


# Get upcoming NBA odds

def get_nba_odds():
    sports_response = requests.get('https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?regions=us&markets=h2h', params={
        'api_key': ODDS_API_KEY
    })

    nba_upcoming_odds_json = json.loads(sports_response.text)

    df = pd.DataFrame(nba_upcoming_odds_json)

    # EST Commence Time
    df['commence_time'] = pd.to_datetime(df['commence_time'])
    df['commence_time'] = df['commence_time'].dt.tz_convert('US/Eastern')
    df['commence_time'] = df['commence_time'].dt.strftime('%Y-%m-%d %I:%M:%S %p')

        
    rows = []
    for game in df['bookmakers']:
        for i in range(len(game)):
            bookmaker_name = game[i]['title']
            team1 = game[i]['markets'][0]['outcomes'][0]['name']
            team2 = game[i]['markets'][0]['outcomes'][1]['name']
            odds_team1 = game[i]['markets'][0]['outcomes'][0]['price']
            odds_team2 = game[i]['markets'][0]['outcomes'][1]['price']
            rows.append([bookmaker_name, team1, odds_team1, team2, odds_team2])

    df_odds = pd.DataFrame(rows, columns=['Bookmaker', 'Team1', 'Odds_Team1', 'Team2', 'Odds_Team2'])
    print(df_odds)

    merged_df1 = pd.merge(df, df_odds, left_on=['away_team', 'home_team'], right_on=['Team1', 'Team2'], how='left')
    merged_df2 = pd.merge(df, df_odds, left_on=['home_team', 'away_team'], right_on=['Team1', 'Team2'], how='left')
    merged_df = pd.concat([merged_df1, merged_df2], ignore_index=True)


    merged_df.dropna(subset=['Team1', 'Team2'], inplace=True)


    return merged_df

# Get upcoming NBA odds
print(get_nba_odds())