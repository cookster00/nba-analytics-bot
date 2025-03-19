# This script compares the season averages of two NBA players side by side.
# The user is prompted to enter the names of two players for comparison.
# The script then fetches the players' season statistics, calculates per-game averages, and saves the comparison to a CSV file.

from nba_api.stats.endpoints import leaguedashplayerstats
import pandas as pd
import logging
import os
from difflib import get_close_matches

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Directory to save CSV files
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# Prompt for player selection
player1_name = input("Enter the name of the first player for comparison: ")
player2_name = input("Enter the name of the second player for comparison: ")

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

# Fetch season averages for the player
def get_season_averages(player_name):
    try:
        logging.info(f"Fetching season averages for {player_name}")
        player_stats = leaguedashplayerstats.LeagueDashPlayerStats(season="2024-25").get_data_frames()[0]
        player_stats = player_stats[player_stats['PLAYER_NAME'] == player_name]
        if not player_stats.empty:
            games_played = player_stats['GP'].values[0]
            avg_points = player_stats['PTS'].sum() / games_played
            avg_rebounds = player_stats['REB'].sum() / games_played
            avg_assists = player_stats['AST'].sum() / games_played
            avg_steals = player_stats['STL'].sum() / games_played
            avg_blocks = player_stats['BLK'].sum() / games_played
            avg_minutes = player_stats['MIN'].sum() / games_played
            avg_fgm = player_stats['FGM'].sum() / games_played
            avg_fga = player_stats['FGA'].sum() / games_played
            avg_fg3m = player_stats['FG3M'].sum() / games_played
            avg_fg3a = player_stats['FG3A'].sum() / games_played
            avg_ftm = player_stats['FTM'].sum() / games_played
            avg_fta = player_stats['FTA'].sum() / games_played
            avg_turnovers = player_stats['TOV'].sum() / games_played
            avg_fouls = player_stats['PF'].sum() / games_played

            return {
                "Player": player_name,
                "Season PPG": round(avg_points, 1),
                "Season RPG": round(avg_rebounds, 1),
                "Season APG": round(avg_assists, 1),
                "Season SPG": round(avg_steals, 1),
                "Season BPG": round(avg_blocks, 1),
                "Season MPG": round(avg_minutes, 1),
                "Season FGM": round(avg_fgm, 1),
                "Season FGA": round(avg_fga, 1),
                "Season FG3M": round(avg_fg3m, 1),
                "Season FG3A": round(avg_fg3a, 1),
                "Season FTM": round(avg_ftm, 1),
                "Season FTA": round(avg_fta, 1),
                "Season TO": round(avg_turnovers, 1),
                "Season PF": round(avg_fouls, 1)
            }
        else:
            logging.error(f"No season data found for {player_name}.")
            return None
    except Exception as e:
        logging.error(f"Error fetching season averages for {player_name}: {e}")
        return None

# Main execution
player1_id = get_player_id(player1_name)
player2_id = get_player_id(player2_name)

if player1_id and player2_id:
    player1_stats = get_season_averages(player1_name)
    player2_stats = get_season_averages(player2_name)

    if player1_stats and player2_stats:
        logging.info(f"Season averages for {player1_name}: {player1_stats}")
        logging.info(f"Season averages for {player2_name}: {player2_stats}")
        # Combine the stats for comparison
        comparison_stats = {
            "Stat": list(player1_stats.keys())[1:],  # Skip the "Player" key
            player1_name: list(player1_stats.values())[1:],  # Skip the "Player" value
            player2_name: list(player2_stats.values())[1:]  # Skip the "Player" value
        }
        # Create a DataFrame for the comparison
        comparison_df = pd.DataFrame(comparison_stats)
        # Save the comparison to CSV
        output_file = os.path.join(output_dir, f'{player1_name}_vs_{player2_name}_season_comparison.csv')
        comparison_df.to_csv(output_file, index=False)
        logging.info(f"Season comparison saved to {output_file}")
else:
    if not player1_id:
        logging.error(f"Player {player1_name} not found.")
    if not player2_id:
        logging.error(f"Player {player2_name} not found.")