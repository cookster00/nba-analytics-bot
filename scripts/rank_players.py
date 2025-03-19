"""
This script ranks NBA players based on their monthly performance using data from a CSV file. 
It calculates per-game averages for key statistics and computes a performance score for each player. 
The top 35 players are selected and saved to a new CSV file with their stats reformatted.

Key Features:
1. Reads player data from a CSV file located in the `storage` directory.
2. Calculates per-game averages for key stats:
   - Points (PTS), Offensive Rebounds (ORB), Defensive Rebounds (DRB), Total Rebounds (REB),
     Assists (AST), Steals (STL), Blocks (BLK), Turnovers (TOV), Personal Fouls (PF), and Plus-Minus (+/-).
3. Computes a performance score for each player based on weighted contributions of their stats.
4. Ranks players by their performance score and selects the top 35 players.
5. Outputs the results to a CSV file in the `output` directory with the following columns:
   - Player Name, Games Played, Reformatted Stats, and Performance Score.

Usage:
- Place the input CSV file in the `storage` directory.
- Run the script, and the results will be saved in the `output` directory as `top_35_performances_reformatted.csv`.
"""

import pandas as pd
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(asctime)s - %(levelname)s - %(message)s')

# Directory containing the CSV file
input_dir = "storage"
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# Find the CSV file in the input directory
def find_csv_file(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            return os.path.join(directory, filename)
    return None

# Calculate per-game averages
def calculate_per_game_averages(df):
    df['PTS/G'] = df['PTS'] / df['G']
    df['ORB/G'] = df['ORB'] / df['G']
    df['DRB/G'] = df['DRB'] / df['G']
    df['REB/G'] = df['TRB'] / df['G']
    df['AST/G'] = df['AST'] / df['G']
    df['STL/G'] = df['STL'] / df['G']
    df['BLK/G'] = df['BLK'] / df['G']
    df['TOV/G'] = df['TOV'] / df['G']
    df['PF/G'] = df['PF'] / df['G']
    df['+/-/G'] = df['+/-'] / df['G']
    return df

# Calculate performance score
def calculate_performance_score(row):
    score = (
        row['PTS/G'] * 1.0 +
        row['ORB/G'] * 1.5 +
        row['DRB/G'] * 1.2 +
        row['AST/G'] * 1.5 +
        row['STL/G'] * 3.0 +
        row['BLK/G'] * 3.0 -
        row['TOV/G'] * 1.0 +
        row['+/-/G'] * 0.5
    )
    return score

# Main execution
csv_file = find_csv_file(input_dir)
if csv_file:
    logging.info(f"Reading CSV file: {csv_file}")
    df = pd.read_csv(csv_file)

    # Calculate per-game averages
    df = calculate_per_game_averages(df)

    # Calculate performance scores
    df['Performance_Score'] = df.apply(calculate_performance_score, axis=1)

    # Rank and select top 35 performances
    top_performances = df.nlargest(35, 'Performance_Score')

    # Reformat the stats
    top_performances['Formatted_Stats'] = top_performances.apply(
        lambda row: f"{row['PTS/G']:.1f} ppg, {row['ORB/G']:.1f} orpg, {row['DRB/G']:.1f} drpg, {row['REB/G']:.1f} rpg, {row['AST/G']:.1f} apg, {row['STL/G']:.1f} spg, {row['BLK/G']:.1f} bpg, {row['TOV/G']:.1f} tov, {row['+/-/G']:.1f} +/-",
        axis=1
    )

    # Add the number of games played to the DataFrame
    top_performances['Games_Played'] = top_performances['G']

    # Select relevant columns for the CSV file
    top_performances = top_performances[['Player', 'Games_Played', 'Formatted_Stats', 'Performance_Score']]

    # Save the top 35 performances to a CSV file
    output_file = os.path.join(output_dir, 'top_35_performances_reformatted.csv')
    top_performances.to_csv(output_file, index=False)
    logging.info(f"Reformatted top 35 performances saved to {output_file}")
else:
    logging.error("No CSV file found in the input directory.")