"""
This script generates an extensive daily NBA report with advanced metrics, standout performances, game trends, rookie watch, and more.
The report is saved as a text file in the `reports/daily` folder.
"""

from nba_api.stats.endpoints import (
    scoreboardv2, boxscoretraditionalv2, boxscoresummaryv2,
    leaguedashplayerstats, leaguedashteamstats, boxscoreadvancedv2,
    leaguedashteamshotlocations
)
import pandas as pd
import os
from datetime import datetime, timedelta

# Directory to save daily reports
daily_reports_dir = "reports/daily"
os.makedirs(daily_reports_dir, exist_ok=True)

# Fetch game IDs for the previous day
def fetch_game_ids(date):
    scoreboard = scoreboardv2.ScoreboardV2(game_date=date).get_data_frames()[0]
    return scoreboard[['GAME_ID', 'HOME_TEAM_ID', 'VISITOR_TEAM_ID']]

# Fetch player stats for each game
def fetch_player_stats(game_ids):
    all_stats = []
    for game_id in game_ids:
        boxscore = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id).get_data_frames()[0]
        all_stats.append(boxscore)
    return pd.concat(all_stats, ignore_index=True)

# Fetch advanced player metrics
def fetch_advanced_metrics(game_ids):
    all_advanced_stats = []
    for game_id in game_ids:
        advanced_stats = boxscoreadvancedv2.BoxScoreAdvancedV2(game_id=game_id).get_data_frames()[0]
        all_advanced_stats.append(advanced_stats)
    return pd.concat(all_advanced_stats, ignore_index=True)

# Fetch game scores for each game
def fetch_game_scores(game_ids):
    game_scores = []
    for game_id in game_ids:
        boxscore_summary = boxscoresummaryv2.BoxScoreSummaryV2(game_id=game_id).get_data_frames()[5]  # LineScore DataFrame
        game_scores.append(boxscore_summary)
    return pd.concat(game_scores, ignore_index=True)

# Fetch team stats for the season
def fetch_team_stats():
    team_stats = leaguedashteamstats.LeagueDashTeamStats(season="2024-25").get_data_frames()[0]
    
    # Debug: Print available columns
    print("Available columns in team_stats:")
    print(team_stats.columns)
    
    # Adjust column selection based on available data
    columns_to_select = ['TEAM_NAME', 'W', 'L', 'FG_PCT', 'REB', 'AST', 'TOV']
    if 'OFF_RATING' in team_stats.columns:
        columns_to_select.append('OFF_RATING')
    if 'DEF_RATING' in team_stats.columns:
        columns_to_select.append('DEF_RATING')
    if 'PACE' in team_stats.columns:
        columns_to_select.append('PACE')
    
    # Select relevant columns
    team_stats = team_stats[columns_to_select]
    
    # Sort by wins (descending order)
    team_stats = team_stats.sort_values(by='W', ascending=False)
    
    return team_stats

# Fetch team shooting efficiency by zone
def fetch_team_shooting_locations():
    shooting_data = leaguedashteamshotlocations.LeagueDashTeamShotLocations(season="2024-25").get_data_frames()[0]
    
    # Debug: Print available columns
    print("Available columns in shooting_data:")
    print(shooting_data.columns)
    
    # Flatten the MultiIndex columns
    shooting_data.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in shooting_data.columns]
    
    # Debug: Print flattened columns
    print("Flattened columns in shooting_data:")
    print(shooting_data.columns)
    
    # Select relevant columns (only FG_PCT columns)
    columns_to_select = [
        '_TEAM_NAME',
        'Restricted Area_FG_PCT',
        'In The Paint (Non-RA)_FG_PCT',
        'Mid-Range_FG_PCT',
        'Left Corner 3_FG_PCT',
        'Right Corner 3_FG_PCT',
        'Corner 3_FG_PCT',
        'Above the Break 3_FG_PCT',
        'Backcourt_FG_PCT'
    ]
    shooting_data = shooting_data[columns_to_select]
    
    # Rename columns for clarity
    shooting_data.rename(columns={
        '_TEAM_NAME': 'Team Name',
        'Restricted Area_FG_PCT': 'Restricted Area FG%',
        'In The Paint (Non-RA)_FG_PCT': 'In The Paint (Non-RA) FG%',
        'Mid-Range_FG_PCT': 'Mid-Range FG%',
        'Left Corner 3_FG_PCT': 'Left Corner 3 FG%',
        'Right Corner 3_FG_PCT': 'Right Corner 3 FG%',
        'Corner 3_FG_PCT': 'Corner 3 FG%',
        'Above the Break 3_FG_PCT': 'Above the Break 3 FG%',
        'Backcourt_FG_PCT': 'Backcourt FG%'
    }, inplace=True)
    
    # Sort by Restricted Area FG% (optional)
    shooting_data = shooting_data.sort_values(by='Restricted Area FG%', ascending=False)
    
    return shooting_data

# Identify standout performances
def identify_standout_performances(player_stats):
    standout = player_stats[
        (player_stats['PTS'] >= 30) |  # High scoring games
        (player_stats['REB'] >= 15) |  # High rebounds
        (player_stats['AST'] >= 10) |  # Double-digit assists
        (player_stats['STL'] >= 5) |   # High steals
        (player_stats['BLK'] >= 5)     # High blocks
    ]
    return standout[['PLAYER_NAME', 'PTS', 'REB', 'AST', 'STL', 'BLK']]

# Identify game trends
def identify_game_trends(game_scores):
    home_scores = game_scores[game_scores['TEAM_ABBREVIATION'] == 'HOME']
    visitor_scores = game_scores[game_scores['TEAM_ABBREVIATION'] == 'VISITOR']
    merged_scores = pd.merge(
        home_scores[['GAME_ID', 'PTS']],
        visitor_scores[['GAME_ID', 'PTS']],
        on='GAME_ID',
        suffixes=('_HOME', '_VISITOR')
    )
    merged_scores['Point Differential'] = abs(merged_scores['PTS_HOME'] - merged_scores['PTS_VISITOR'])
    blowouts = merged_scores.nlargest(3, 'Point Differential')
    close_games = merged_scores.nsmallest(3, 'Point Differential')
    return blowouts, close_games

# Identify rookie performances
def identify_rookie_watch(player_stats):
    # Fetch season stats to get the ROOKIE_FLAG
    season_stats = leaguedashplayerstats.LeagueDashPlayerStats(season="2024-25").get_data_frames()[0]
    
    # Debug: Print available columns in season_stats
    print("Available columns in season_stats:")
    print(season_stats.columns)
    
    # Check if ROOKIE_FLAG exists
    if 'ROOKIE_FLAG' not in season_stats.columns:
        raise KeyError("ROOKIE_FLAG column not found in season_stats. Please verify the API response.")
    
    # Filter rookies
    rookies = season_stats[season_stats['ROOKIE_FLAG'] == 1]
    
    # Merge with player_stats to get rookies who played in the games
    rookies_in_games = pd.merge(
        player_stats,
        rookies[['PLAYER_ID', 'PLAYER_NAME']],
        on='PLAYER_ID',
        how='inner'
    )
    
    # Return top-performing rookies
    return rookies_in_games.nlargest(5, 'PTS')[['PLAYER_NAME', 'PTS', 'REB', 'AST']]

# Identify young players (21 years old or younger) performances
def identify_young_players_watch(player_stats):
    # Fetch season stats to get the AGE column
    season_stats = leaguedashplayerstats.LeagueDashPlayerStats(season="2024-25").get_data_frames()[0]
    
    # Debug: Print available columns in season_stats
    print("Available columns in season_stats:")
    print(season_stats.columns)
    
    # Filter players aged 21 or younger
    young_players = season_stats[season_stats['AGE'] <= 21]
    
    # Debug: Print available columns in young_players
    print("Available columns in young_players:")
    print(young_players.columns)
    
    # Merge with player_stats to get young players who played in the games
    young_players_in_games = pd.merge(
        player_stats,
        young_players[['PLAYER_ID', 'PLAYER_NAME']],
        on='PLAYER_ID',
        how='inner'
    )
    
    # Debug: Print available columns in young_players_in_games
    print("Available columns in young_players_in_games:")
    print(young_players_in_games.columns)
    
    # Rename PLAYER_NAME_y to PLAYER_NAME for clarity
    young_players_in_games = young_players_in_games.rename(columns={'PLAYER_NAME_y': 'PLAYER_NAME'})
    
    # Return top-performing young players
    return young_players_in_games.nlargest(5, 'PTS')[['PLAYER_NAME', 'PTS', 'REB', 'AST']]

# Placeholder for clutch performance logic
def identify_clutch_performances(player_stats):
    # Filter for clutch moments (e.g., last 5 minutes of close games)
    # This will require additional logic to filter based on game context
    return pd.DataFrame()  # Placeholder for now

# Main execution
def generate_daily_report():
    previous_day = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    games = fetch_game_ids(previous_day)
    game_ids = games['GAME_ID'].tolist()

    player_stats = fetch_player_stats(game_ids)
    game_scores = fetch_game_scores(game_ids)
    team_stats = fetch_team_stats()
    shooting_stats = fetch_team_shooting_locations()

    print("Available columns in team_stats:")
    print(team_stats.columns)

    standout_performances = identify_standout_performances(player_stats)
    blowouts, close_games = identify_game_trends(game_scores)
    young_players = identify_young_players_watch(player_stats)

    report_path = os.path.join(daily_reports_dir, f"daily_report_{previous_day}.txt")
    with open(report_path, "w", encoding="utf-8") as report_file:
        report_file.write(f"Daily NBA Report for {previous_day}\n")
        report_file.write("=" * 30 + "\n\n")

        report_file.write("Standout Performances:\n")
        report_file.write(standout_performances.to_string(index=False))
        report_file.write("\n\n")

        report_file.write("Game Trends:\n")
        report_file.write("Largest Blowouts:\n")
        report_file.write(blowouts.to_string(index=False))
        report_file.write("\n\nClosest Games:\n")
        report_file.write(close_games.to_string(index=False))
        report_file.write("\n\n")

        report_file.write("Young Players Watch:\n")
        report_file.write(young_players.to_string(index=False))
        report_file.write("\n\n")

        report_file.write("Team Stats:\n")
        report_file.write(team_stats.to_string(index=False))
        report_file.write("\n\n")

        report_file.write("Shooting Efficiency by Zone:\n")
        report_file.write(shooting_stats.to_string(index=False))
        report_file.write("\n\n")

    print(f"Daily report saved to {report_path}")

# Run the script
if __name__ == "__main__":
    generate_daily_report()