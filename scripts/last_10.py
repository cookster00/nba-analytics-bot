from nba_api.stats.endpoints import leaguedashplayerstats, playergamelog
import pandas as pd
import logging
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from difflib import get_close_matches

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure retry strategy
retry_strategy = Retry(
    total=5,  # Increase the total number of retries
    backoff_factor=2,  # Increase the backoff factor for exponential backoff
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)

# Prompt for player selection
player_name = input("Enter the name of the player for detailed analysis: ")

# Directory to save CSV files
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# Fetch player ID for the selected player
def get_player_id(player_name):
    player_stats = leaguedashplayerstats.LeagueDashPlayerStats(season="2024-25").get_data_frames()[0]
    player = player_stats[player_stats['PLAYER_NAME'] == player_name]
    if not player.empty:
        return player.iloc[0]['PLAYER_ID']
    else:
        # Provide suggestions for similar player names
        all_player_names = player_stats['PLAYER_NAME'].tolist()
        suggestions = get_close_matches(player_name, all_player_names, n=5, cutoff=0.6)
        if suggestions:
            logging.error(f"Player {player_name} not found. Did you mean: {', '.join(suggestions)}?")
        else:
            logging.error(f"Player {player_name} not found and no similar names were found.")
        return None

# Fetch last 10 games and calculate various statistics for the player
def get_last_10_games_stats(player_id, player_name):
    try:
        logging.info(f"Fetching last 10 games stats for {player_name} (ID: {player_id})")
        gamelog = playergamelog.PlayerGameLog(player_id=player_id, season="2024-25", timeout=120).get_data_frames()[0]  # Increase timeout
        gamelog['PTS'] = pd.to_numeric(gamelog['PTS'])
        gamelog['REB'] = pd.to_numeric(gamelog['REB'])
        gamelog['AST'] = pd.to_numeric(gamelog['AST'])
        gamelog['STL'] = pd.to_numeric(gamelog['STL'])
        gamelog['BLK'] = pd.to_numeric(gamelog['BLK'])
        gamelog['MIN'] = pd.to_numeric(gamelog['MIN'])
        gamelog['FGM'] = pd.to_numeric(gamelog['FGM'])
        gamelog['FGA'] = pd.to_numeric(gamelog['FGA'])
        gamelog['FG3M'] = pd.to_numeric(gamelog['FG3M'])
        gamelog['FG3A'] = pd.to_numeric(gamelog['FG3A'])
        gamelog['FTM'] = pd.to_numeric(gamelog['FTM'])
        gamelog['FTA'] = pd.to_numeric(gamelog['FTA'])
        gamelog['TO'] = pd.to_numeric(gamelog['TOV'])
        gamelog['PF'] = pd.to_numeric(gamelog['PF'])

        avg_points = gamelog['PTS'].head(10).mean()
        avg_rebounds = gamelog['REB'].head(10).mean()
        avg_assists = gamelog['AST'].head(10).mean()
        avg_steals = gamelog['STL'].head(10).mean()
        avg_blocks = gamelog['BLK'].head(10).mean()
        avg_minutes = gamelog['MIN'].head(10).mean()
        avg_fgm = gamelog['FGM'].head(10).mean()
        avg_fga = gamelog['FGA'].head(10).mean()
        avg_fg3m = gamelog['FG3M'].head(10).mean()
        avg_fg3a = gamelog['FG3A'].head(10).mean()
        avg_ftm = gamelog['FTM'].head(10).mean()
        avg_fta = gamelog['FTA'].head(10).mean()
        avg_turnovers = gamelog['TO'].head(10).mean()
        avg_fouls = gamelog['PF'].head(10).mean()

        return {
            "Player": player_name,
            "Last 10 Games PPG": round(avg_points, 1),
            "Last 10 Games RPG": round(avg_rebounds, 1),
            "Last 10 Games APG": round(avg_assists, 1),
            "Last 10 Games SPG": round(avg_steals, 1),
            "Last 10 Games BPG": round(avg_blocks, 1),
            "Last 10 Games MPG": round(avg_minutes, 1),
            "Last 10 Games FGM": round(avg_fgm, 1),
            "Last 10 Games FGA": round(avg_fga, 1),
            "Last 10 Games FG3M": round(avg_fg3m, 1),
            "Last 10 Games FG3A": round(avg_fg3a, 1),
            "Last 10 Games FTM": round(avg_ftm, 1),
            "Last 10 Games FTA": round(avg_fta, 1),
            "Last 10 Games TO": round(avg_turnovers, 1),
            "Last 10 Games PF": round(avg_fouls, 1)
        }
    except Exception as e:
        logging.error(f"Error fetching {player_name}: {e}")
        return None

# Main execution
player_id = get_player_id(player_name)
if player_id:
    detailed_stats = get_last_10_games_stats(player_id, player_name)
    if detailed_stats:
        logging.info(f"Detailed stats for {player_name}: {detailed_stats}")
        # Save detailed stats to CSV
        output_file = os.path.join(output_dir, f'{player_name}_last_10_games_stats.csv')
        # Create a DataFrame with two columns: Title and Stat
        stats_df = pd.DataFrame(list(detailed_stats.items()), columns=['Title', 'Stat'])
        stats_df.to_csv(output_file, index=False)
        logging.info(f"Last 10 games stats saved to {output_file}")