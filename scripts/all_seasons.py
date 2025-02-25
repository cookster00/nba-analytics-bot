from nba_api.stats.endpoints import leaguedashplayerstats, playergamelog
import pandas as pd
import logging
import concurrent.futures
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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

# List of seasons to fetch data for
seasons = ["2022-23", "2023-24", "2024-25"]

# Initialize an empty DataFrame to store aggregated data
all_seasons_stats = pd.DataFrame()

# Fetch player stats for each season and aggregate
for season in seasons:
    logging.info(f"Fetching player stats for {player_name} in season {season}")
    player_stats = leaguedashplayerstats.LeagueDashPlayerStats(season=season).get_data_frames()[0]
    player_stats = player_stats[player_stats['PLAYER_NAME'] == player_name]
    if not player_stats.empty:
        player_stats['SEASON'] = season  # Add a column for the season
        all_seasons_stats = pd.concat([all_seasons_stats, player_stats], ignore_index=True)
    else:
        logging.warning(f"No data found for {player_name} in season {season}")

# Check if any data was fetched
if all_seasons_stats.empty:
    logging.error(f"No data found for {player_name} in the specified seasons.")
else:
    # Select key stats for comparison
    key_stats = ['PLAYER_NAME', 'SEASON', 'PTS', 'AST', 'REB', 'FG_PCT']
    all_seasons_stats = all_seasons_stats[key_stats]

    # Save aggregated data to CSV
    all_seasons_stats.to_csv(f'{player_name}_all_seasons_stats.csv', index=False)
    logging.info(f"Aggregated player stats saved to {player_name}_all_seasons_stats.csv")

    # Example analysis: Calculate average points per game for the player across seasons
    avg_points_per_game = all_seasons_stats.groupby('PLAYER_NAME')['PTS'].mean().reset_index()
    avg_points_per_game = avg_points_per_game.sort_values(by='PTS', ascending=False)

    # Save analysis results to CSV
    avg_points_per_game.to_csv(f'{player_name}_avg_points_per_game.csv', index=False)
    logging.info(f"Average points per game saved to {player_name}_avg_points_per_game.csv")

    # Additional analysis: Calculate average assists per game for the player across seasons
    avg_assists_per_game = all_seasons_stats.groupby('PLAYER_NAME')['AST'].mean().reset_index()
    avg_assists_per_game = avg_assists_per_game.sort_values(by='AST', ascending=False)

    # Save analysis results to CSV
    avg_assists_per_game.to_csv(f'{player_name}_avg_assists_per_game.csv', index=False)
    logging.info(f"Average assists per game saved to {player_name}_avg_assists_per_game.csv")

    # Additional analysis: Calculate average rebounds per game for the player across seasons
    avg_rebounds_per_game = all_seasons_stats.groupby('PLAYER_NAME')['REB'].mean().reset_index()
    avg_rebounds_per_game = avg_rebounds_per_game.sort_values(by='REB', ascending=False)

    # Save analysis results to CSV
    avg_rebounds_per_game.to_csv(f'{player_name}_avg_rebounds_per_game.csv', index=False)
    logging.info(f"Average rebounds per game saved to {player_name}_avg_rebounds_per_game.csv")

    # Fetch last 10 games and calculate various statistics for the player
    def get_player_stats(player_id, player_name):
        try:
            logging.info(f"Fetching last 10 games stats for {player_name} (ID: {player_id})")
            gamelog = playergamelog.PlayerGameLog(player_id=player_id, season="2024-25", timeout=120).get_data_frames()[0]  # Increase timeout
            gamelog['PTS'] = pd.to_numeric(gamelog['PTS'])
            gamelog['REB'] = pd.to_numeric(gamelog['REB'])
            gamelog['AST'] = pd.to_numeric(gamelog['AST'])
            gamelog['STL'] = pd.to_numeric(gamelog['STL'])
            gamelog['BLK'] = pd.to_numeric(gamelog['BLK'])
            
            avg_points = gamelog['PTS'].head(10).mean()
            avg_rebounds = gamelog['REB'].head(10).mean()
            avg_assists = gamelog['AST'].head(10).mean()
            avg_steals = gamelog['STL'].head(10).mean()
            avg_blocks = gamelog['BLK'].head(10).mean()
            
            return {
                "Player": player_name,
                "Last 10 Games PPG": round(avg_points, 1),
                "Last 10 Games RPG": round(avg_rebounds, 1),
                "Last 10 Games APG": round(avg_assists, 1),
                "Last 10 Games SPG": round(avg_steals, 1),
                "Last 10 Games BPG": round(avg_blocks, 1)
            }
        except Exception as e:
            logging.error(f"Error fetching {player_name}: {e}")
            return None

    # Find the player ID for the selected player
    player_stats = leaguedashplayerstats.LeagueDashPlayerStats(season="2024-25").get_data_frames()[0]
    player = player_stats[player_stats['PLAYER_NAME'] == player_name]

    if not player.empty:
        player_id = player.iloc[0]['PLAYER_ID']
        detailed_stats = get_player_stats(player_id, player_name)
        if detailed_stats:
            logging.info(f"Detailed stats for {player_name}: {detailed_stats}")
            # Save detailed stats to CSV
            pd.DataFrame([detailed_stats]).to_csv(f'{player_name}_last_10_games_stats.csv', index=False)
            logging.info(f"Last 10 games stats saved to {player_name}_last_10_games_stats.csv")
    else:
        logging.error(f"Player {player_name} not found in the current season data.")
