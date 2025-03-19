"""
This script analyzes defensive impact metrics for NBA players using the LeagueDashPtDefend endpoint.
It ranks players based on defensive stats such as opponent field goal percentage (D_FG_PCT) and compares it to the league average.
Only players who have played a minimum of 25 games are included in the analysis.

Usage:
- Run the script, and the results will be saved in the `output` directory.
"""

from nba_api.stats.endpoints import leaguedashptdefend
import pandas as pd
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Directory to save CSV files
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# Fetch defensive stats
def fetch_defensive_stats():
    logging.info("Fetching defensive stats for players...")
    defensive_data = leaguedashptdefend.LeagueDashPtDefend().get_data_frames()[0]
    return defensive_data

# Main execution
try:
    # Fetch defensive stats
    defensive_stats = fetch_defensive_stats()

    # Debug: Print available columns
    print("Available columns in defensive stats:")
    print(defensive_stats.columns)

    # Select relevant columns
    defensive_stats = defensive_stats[[
        "PLAYER_NAME", "GP", "D_FGM", "D_FGA", "D_FG_PCT", "NORMAL_FG_PCT", "PCT_PLUSMINUS"
    ]]

    # Rename columns for clarity
    defensive_stats.rename(columns={
        "PLAYER_NAME": "Player Name",
        "GP": "Games Played",
        "D_FGM": "Defended FGM",
        "D_FGA": "Defended FGA",
        "D_FG_PCT": "Defended FG%",
        "NORMAL_FG_PCT": "League Average FG%",
        "PCT_PLUSMINUS": "FG% Difference"
    }, inplace=True)

    # Filter players with a minimum of 25 games played
    defensive_stats = defensive_stats[defensive_stats["Games Played"] >= 25]

    # Sort players by FG% Difference (ascending, lower is better)
    defensive_stats = defensive_stats.sort_values(by="FG% Difference", ascending=True)

    # Save the results to a CSV file
    output_file = os.path.join(output_dir, "defensive_impact_analysis.csv")
    defensive_stats.to_csv(output_file, index=False)
    logging.info(f"Defensive impact analysis saved to {output_file}")

except Exception as e:
    logging.error(f"An error occurred: {e}")