#returns top performances from the previous days worth of games

from nba_api.stats.endpoints import scoreboardv2, boxscoretraditionalv2
import pandas as pd
import logging
import os
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Directory to save CSV files
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# Calculate the date for the previous night
previous_night = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

# Fetch game IDs for the previous night
def fetch_game_ids(date):
    logging.info(f"Fetching game IDs for {date}")
    scoreboard = scoreboardv2.ScoreboardV2(game_date=date).get_data_frames()[0]
    game_ids = scoreboard['GAME_ID'].tolist()
    return game_ids

# Fetch game logs for the previous night
def fetch_previous_night_game_logs(game_ids):
    all_game_logs = []
    for game_id in game_ids:
        logging.info(f"Fetching game logs for game ID {game_id}")
        boxscore = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id).get_data_frames()[0]
        all_game_logs.append(boxscore)
    return pd.concat(all_game_logs, ignore_index=True)

# Calculate performance score
def calculate_performance_score(row):
    score = (
        row['PTS'] * 1.0 +
        row['REB'] * 1.2 +
        row['AST'] * 1.5 +
        row['STL'] * 3.0 +
        row['BLK'] * 3.0
    )
    return score

# Fetch game IDs for the previous night
game_ids = fetch_game_ids(previous_night)

# Fetch game logs for the previous night
game_logs = fetch_previous_night_game_logs(game_ids)

# Calculate performance scores
game_logs['Performance_Score'] = game_logs.apply(calculate_performance_score, axis=1)

# Rank and select top 10 performances
top_performances = game_logs.nlargest(10, 'Performance_Score')

# Format the top performances for the CSV file
top_performances['Formatted_Stats'] = top_performances.apply(
    lambda row: f"{row['PTS']} pts, {row['REB']} reb, {row['AST']} ast, {row['STL']} stl, {row['BLK']} blk", axis=1
)

# Select relevant columns for the CSV file
top_performances = top_performances[['PLAYER_NAME', 'Formatted_Stats', 'Performance_Score']]

# Save the top 10 performances to a CSV file
output_file = os.path.join(output_dir, f'top_10_performances_{previous_night}.csv')
top_performances.to_csv(output_file, index=False)
logging.info(f"Top 10 performances saved to {output_file}")