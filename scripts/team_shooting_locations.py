"""
This script analyzes team shooting percentages from different areas of the court for the entire NBA season
using the LeagueDashTeamShotLocations endpoint. It ranks teams based on their shooting efficiency by location.

Usage:
- Run the script, and the results will be saved in the `output` directory.
"""

from nba_api.stats.endpoints import leaguedashteamshotlocations
import pandas as pd
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Directory to save CSV files
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# Fetch team shooting location stats
def fetch_team_shooting_locations(season="2024-25"):
    logging.info(f"Fetching team shooting location stats for the {season} season...")
    shooting_data = leaguedashteamshotlocations.LeagueDashTeamShotLocations(season=season).get_data_frames()[0]
    return shooting_data

# Main execution
try:
    # Fetch team shooting location stats
    team_shooting_stats = fetch_team_shooting_locations()

    # Debug: Print available columns
    print("Available columns in team shooting stats:")
    print(team_shooting_stats.columns)

    # Flatten the MultiIndex columns
    team_shooting_stats.columns = ['_'.join(col).strip() for col in team_shooting_stats.columns.values]

    # Debug: Print flattened columns
    print("Flattened columns in team shooting stats:")
    print(team_shooting_stats.columns)

    # Select relevant columns
    team_shooting_stats = team_shooting_stats[[
        "_TEAM_NAME", "Restricted Area_FG_PCT", "In The Paint (Non-RA)_FG_PCT",
        "Mid-Range_FG_PCT", "Corner 3_FG_PCT", "Above the Break 3_FG_PCT"
    ]]

    # Rename columns for clarity
    team_shooting_stats.rename(columns={
        "_TEAM_NAME": "Team Name",
        "Restricted Area_FG_PCT": "Restricted Area FG%",
        "In The Paint (Non-RA)_FG_PCT": "Paint (Non-RA) FG%",
        "Mid-Range_FG_PCT": "Mid-Range FG%",
        "Corner 3_FG_PCT": "Corner 3 FG%",
        "Above the Break 3_FG_PCT": "Above the Break 3 FG%"
    }, inplace=True)

    # Sort teams by Restricted Area FG% (descending)
    team_shooting_stats = team_shooting_stats.sort_values(by="Restricted Area FG%", ascending=False)

    # Save the results to a CSV file
    output_file = os.path.join(output_dir, "team_shooting_locations_analysis.csv")
    team_shooting_stats.to_csv(output_file, index=False)
    logging.info(f"Team shooting locations analysis saved to {output_file}")

except Exception as e:
    logging.error(f"An error occurred: {e}")