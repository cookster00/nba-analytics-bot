from nba_api.stats.endpoints import leaguedashplayerstats
import pandas as pd
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Directory to save CSV files
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# Fetch season averages for all players
def fetch_season_averages():
    logging.info("Fetching season averages for all players")
    player_stats = leaguedashplayerstats.LeagueDashPlayerStats(season="2024-25").get_data_frames()[0]
    return player_stats

# Calculate performance score per game
def calculate_performance_score_per_game(row):
    score = (
        row['PTS/G'] * 1.0 +
        row['OREB/G'] * 1.5 +
        row['DREB/G'] * 1.2 +
        row['AST/G'] * 1.5 +
        row['STL/G'] * 3.0 +
        row['BLK/G'] * 3.0 -
        row['TOV/G'] * 1.0 +
        row['PLUS_MINUS/G'] * 0.5
    )
    return score

# Main execution
player_stats = fetch_season_averages()

# Calculate per-game stats
player_stats['PTS/G'] = player_stats['PTS'] / player_stats['GP']
player_stats['OREB/G'] = player_stats['OREB'] / player_stats['GP']
player_stats['DREB/G'] = player_stats['DREB'] / player_stats['GP']
player_stats['REB/G'] = player_stats['REB'] / player_stats['GP']
player_stats['AST/G'] = player_stats['AST'] / player_stats['GP']
player_stats['STL/G'] = player_stats['STL'] / player_stats['GP']
player_stats['BLK/G'] = player_stats['BLK'] / player_stats['GP']
player_stats['TOV/G'] = player_stats['TOV'] / player_stats['GP']
player_stats['PLUS_MINUS/G'] = player_stats['PLUS_MINUS'] / player_stats['GP']

# Calculate performance scores per game
player_stats['Performance_Score/G'] = player_stats.apply(calculate_performance_score_per_game, axis=1)

# Rank and select top 100 performances
top_performances = player_stats.nlargest(100, 'Performance_Score/G')

# Reformat the stats
top_performances['Formatted_Stats'] = top_performances.apply(
    lambda row: f"{row['PTS/G']:.1f} ppg, {row['OREB/G']:.1f} orpg, {row['DREB/G']:.1f} drpg, {row['REB/G']:.1f} rpg, {row['AST/G']:.1f} apg, {row['STL/G']:.1f} spg, {row['BLK/G']:.1f} bpg, {row['TOV/G']:.1f} tov, {row['PLUS_MINUS/G']:.1f} +/-",
    axis=1
)

# Select relevant columns for the CSV file
top_performances = top_performances[['PLAYER_NAME', 'Formatted_Stats', 'Performance_Score/G']]

# Save the top 100 performances to a CSV file
output_file = os.path.join(output_dir, 'top_100_season_performances.csv')
top_performances.to_csv(output_file, index=False)
logging.info(f"Top 100 season performances saved to {output_file}")