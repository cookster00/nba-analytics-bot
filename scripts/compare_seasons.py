"""
This script compares player performance between two NBA seasons and identifies the top 25 improvements 
and declines in overall performance. The comparison is based on per-game averages for points (PTS), 
rebounds (REB), assists (AST), steals (STL), and blocks (BLK).

Key Features:
1. Fetches season averages for the current and previous NBA seasons using the nba_api.
2. Calculates per-game averages for key stats (PTS, REB, AST, STL, BLK).
3. Computes the difference in performance between the two seasons for each player.
4. Identifies the top 25 players with the greatest improvements and declines in overall performance.
5. Outputs the results to two CSV files:
   - `top_25_improvements.csv`: Players with the greatest improvements.
   - `top_25_declines.csv`: Players with the greatest declines.
6. Each player is represented in the output with three rows:
   - Current season stats.
   - Difference in stats between the two seasons.
   - Previous season stats.

Usage:
- Update the `season_current` and `season_previous` variables to specify the seasons to compare.
- Run the script, and the results will be saved in the `output` directory.
"""

from nba_api.stats.endpoints import leaguedashplayerstats
import pandas as pd
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Directory to save CSV files
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# Fetch season averages for a given season
def fetch_season_averages(season):
    logging.info(f"Fetching season averages for {season}")
    player_stats = leaguedashplayerstats.LeagueDashPlayerStats(season=season).get_data_frames()[0]
    return player_stats

# Calculate per-game stats
def calculate_per_game_stats(df):
    df['PTS/G'] = df['PTS'] / df['GP']
    df['REB/G'] = df['REB'] / df['GP']
    df['AST/G'] = df['AST'] / df['GP']
    df['STL/G'] = df['STL'] / df['GP']
    df['BLK/G'] = df['BLK'] / df['GP']
    return df

# Main execution
season_current = "2024-25"
season_previous = "2023-24"

# Fetch season averages for both seasons
player_stats_current = fetch_season_averages(season_current)
player_stats_previous = fetch_season_averages(season_previous)

# Calculate per-game stats for both seasons
player_stats_current = calculate_per_game_stats(player_stats_current)
player_stats_previous = calculate_per_game_stats(player_stats_previous)

# Merge the dataframes on PLAYER_ID
merged_stats = pd.merge(player_stats_current[['PLAYER_ID', 'PLAYER_NAME', 'PTS/G', 'REB/G', 'AST/G', 'STL/G', 'BLK/G']], 
                        player_stats_previous[['PLAYER_ID', 'PTS/G', 'REB/G', 'AST/G', 'STL/G', 'BLK/G']], 
                        on='PLAYER_ID', 
                        suffixes=('_current', '_previous'))

# Calculate the differences in stats
merged_stats['PTS_Difference'] = merged_stats['PTS/G_current'] - merged_stats['PTS/G_previous']
merged_stats['REB_Difference'] = merged_stats['REB/G_current'] - merged_stats['REB/G_previous']
merged_stats['AST_Difference'] = merged_stats['AST/G_current'] - merged_stats['AST/G_previous']
merged_stats['STL_Difference'] = merged_stats['STL/G_current'] - merged_stats['STL/G_previous']
merged_stats['BLK_Difference'] = merged_stats['BLK/G_current'] - merged_stats['BLK/G_previous']

# Calculate the overall performance difference
merged_stats['Overall_Difference'] = (
    merged_stats['PTS_Difference'] +
    merged_stats['REB_Difference'] +
    merged_stats['AST_Difference'] +
    merged_stats['STL_Difference'] +
    merged_stats['BLK_Difference']
)

# Identify the top 25 improvements and declines
top_improvements = merged_stats.nlargest(25, 'Overall_Difference')
top_declines = merged_stats.nsmallest(25, 'Overall_Difference')

# Format the stats to one decimal place
top_improvements = top_improvements.round(1)
top_declines = top_declines.round(1)

# Prepare the data for output
def format_player_stats(row, season, suffix):
    return {
        "Player": f"{row['PLAYER_NAME']} ({season})",
        "PTS": f"{row[f'PTS/G{suffix}']:.1f}",
        "REB": f"{row[f'REB/G{suffix}']:.1f}",
        "AST": f"{row[f'AST/G{suffix}']:.1f}",
        "STL": f"{row[f'STL/G{suffix}']:.1f}",
        "BLK": f"{row[f'BLK/G{suffix}']:.1f}"
    }

def format_difference_stats(row):
    return {
        "Player": f"{row['PLAYER_NAME']} (Difference)",
        "PTS": f"{row['PTS_Difference']:.1f}",
        "REB": f"{row['REB_Difference']:.1f}",
        "AST": f"{row['AST_Difference']:.1f}",
        "STL": f"{row['STL_Difference']:.1f}",
        "BLK": f"{row['BLK_Difference']:.1f}"
    }

# Combine the data for improvements and declines
def combine_stats(stats):
    combined_stats = []
    for _, row in stats.iterrows():
        combined_stats.append(format_player_stats(row, season_current, '_current'))
        combined_stats.append(format_difference_stats(row))
        combined_stats.append(format_player_stats(row, season_previous, '_previous'))
    return combined_stats

combined_improvements = combine_stats(top_improvements)
combined_declines = combine_stats(top_declines)

# Convert to DataFrame
improvements_df = pd.DataFrame(combined_improvements)
declines_df = pd.DataFrame(combined_declines)

# Save the results to CSV files
improvements_file = os.path.join(output_dir, 'top_25_improvements.csv')
declines_file = os.path.join(output_dir, 'top_25_declines.csv')

improvements_df.to_csv(improvements_file, index=False)
declines_df.to_csv(declines_file, index=False)

logging.info(f"Top 25 improvements saved to {improvements_file}")
logging.info(f"Top 25 declines saved to {declines_file}")
