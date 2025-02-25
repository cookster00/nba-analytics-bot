from nba_api.stats.endpoints import leaguedashplayerstats
import pandas as pd

# Fetch player stats for the current season
player_stats = leaguedashplayerstats.LeagueDashPlayerStats(season="2024-25").get_data_frames()[0]

# Select key stats
df = player_stats[['PLAYER_NAME', 'PTS', 'AST', 'REB', 'FG_PCT']]

# Save to CSV
df.to_csv('player_stats.csv', index=False)
print("Player stats saved to player_stats.csv")
