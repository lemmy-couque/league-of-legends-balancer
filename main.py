import pandas as pd
from transform import (fetch_champion_mapping, enrich_match_data, calculate_win_rates, get_all_puuids, 
                       get_all_matches, get_all_match_details, save_matches_to_dataframe) 
from analysis import plot_champion_win_rates


# Get summoner games on the past week
summoner_puuids = get_all_puuids()
summoner_matches = get_all_matches(summoner_puuids)
all_match_details = get_all_match_details(summoner_matches)
matches_df = save_matches_to_dataframe(all_match_details)
matches_df.to_csv("datasets/summoner_matches.csv", index=False)

print("Games data saved in 'datasets/summoner_matches.csv'")

# Calculate winrates
matches_df = pd.read_csv("datasets/summoner_matches.csv")
champion_mapping = fetch_champion_mapping()
matches_df = enrich_match_data(matches_df, champion_mapping)
win_rate_df = calculate_win_rates(matches_df)
matches_df.to_csv("datasets/detailed_matches.csv", index=False)
win_rate_df.to_csv("datasets/champion_win_rates_by_role.csv", index=False)

print("Detailled games data saved in 'datasets/detailed_matches.csv'.")
print("Winrates for each champion and role saved in 'datasets/champion_win_rates_by_role.csv'.")

# Visualization of the winrates on the past week
winrates_df = pd.read_csv("datasets/champion_win_rates_by_role.csv")
winrates_report = plot_champion_win_rates(winrates_df)

print("Reports saved in 'reports/'")