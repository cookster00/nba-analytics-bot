# This script fetches and analyzes the last X games stats for a specific NBA player.
# The user is prompted to enter the player's name and the number of games to analyze (1-30) or "season" for season totals.
# The script then fetches the player's game logs, calculates various statistics, and saves the results to a CSV file.

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

# Prompt for the number of games to analyze or "season" for season totals
while True:
    num_games_input = input("Enter the number of games to analyze (1-30) or 'season' for season totals: ")
    if num_games_input.lower() == "season":
        num_games = "season"
        break
    try:
        num_games = int(num_games_input)
        if 1 <= num_games <= 30:
            break
        else:
            print("Please enter a number between 1 and 30.")
    except ValueError:
        print("Invalid input. Please enter a number between 1 and 30 or 'season'.")

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

# Fetch last x games or season totals and calculate various statistics for the player
def get_last_x_games_stats(player_id, player_name, num_games):
    try:
        logging.info(f"Fetching last {num_games} games stats for {player_name} (ID: {player_id})")
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
        gamelog['PLUS_MINUS'] = pd.to_numeric(gamelog['PLUS_MINUS'])

        if num_games == "season":
            avg_points = gamelog['PTS'].mean()
            avg_rebounds = gamelog['REB'].mean()
            avg_assists = gamelog['AST'].mean()
            avg_steals = gamelog['STL'].mean()
            avg_blocks = gamelog['BLK'].mean()
            avg_minutes = gamelog['MIN'].mean()
            avg_fgm = gamelog['FGM'].mean()
            avg_fga = gamelog['FGA'].mean()
            avg_fg3m = gamelog['FG3M'].mean()
            avg_fg3a = gamelog['FG3A'].mean()
            avg_ftm = gamelog['FTM'].mean()
            avg_fta = gamelog['FTA'].mean()
            avg_turnovers = gamelog['TO'].mean()
            avg_fouls = gamelog['PF'].mean()
            avg_plus_minus = gamelog['PLUS_MINUS'].mean()
            num_games_text = "Season"
        else:
            avg_points = gamelog['PTS'].head(num_games).mean()
            avg_rebounds = gamelog['REB'].head(num_games).mean()
            avg_assists = gamelog['AST'].head(num_games).mean()
            avg_steals = gamelog['STL'].head(num_games).mean()
            avg_blocks = gamelog['BLK'].head(num_games).mean()
            avg_minutes = gamelog['MIN'].head(num_games).mean()
            avg_fgm = gamelog['FGM'].head(num_games).mean()
            avg_fga = gamelog['FGA'].head(num_games).mean()
            avg_fg3m = gamelog['FG3M'].head(num_games).mean()
            avg_fg3a = gamelog['FG3A'].head(num_games).mean()
            avg_ftm = gamelog['FTM'].head(num_games).mean()
            avg_fta = gamelog['FTA'].head(num_games).mean()
            avg_turnovers = gamelog['TO'].head(num_games).mean()
            avg_fouls = gamelog['PF'].head(num_games).mean()
            avg_plus_minus = gamelog['PLUS_MINUS'].head(num_games).mean()
            num_games_text = f"Last {num_games} Games"

        return {
            "Player": player_name,
            f"{num_games_text} PPG": round(avg_points, 1),
            f"{num_games_text} RPG": round(avg_rebounds, 1),
            f"{num_games_text} APG": round(avg_assists, 1),
            f"{num_games_text} SPG": round(avg_steals, 1),
            f"{num_games_text} BPG": round(avg_blocks, 1),
            f"{num_games_text} MPG": round(avg_minutes, 1),
            f"{num_games_text} FGM": round(avg_fgm, 1),
            f"{num_games_text} FGA": round(avg_fga, 1),
            f"{num_games_text} FG3M": round(avg_fg3m, 1),
            f"{num_games_text} FG3A": round(avg_fg3a, 1),
            f"{num_games_text} FTM": round(avg_ftm, 1),
            f"{num_games_text} FTA": round(avg_fta, 1),
            f"{num_games_text} TO": round(avg_turnovers, 1),
            f"{num_games_text} PF": round(avg_fouls, 1),
            f"{num_games_text} +/-": round(avg_plus_minus, 1)
        }
    except Exception as e:
        logging.error(f"Error fetching {player_name}: {e}")
        return None

# Main execution
player_id = get_player_id(player_name)
if player_id:
    detailed_stats = get_last_x_games_stats(player_id, player_name, num_games)
    if detailed_stats:
        logging.info(f"Detailed stats for {player_name}: {detailed_stats}")
        # Save detailed stats to CSV
        output_file = os.path.join(output_dir, f'{player_name}_last_{num_games}_games_stats.csv')
        # Create a DataFrame with two columns: Title and Stat
        stats_df = pd.DataFrame(list(detailed_stats.items()), columns=['Title', 'Stat'])
        stats_df.to_csv(output_file, index=False)
        logging.info(f"Last {num_games} games stats saved to {output_file}")