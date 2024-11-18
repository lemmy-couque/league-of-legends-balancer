import pandas as pd
from fetch_players import get_challenger_summoners, get_puuid, get_all_challenger_puuids, get_matches, get_all_challenger_matches

# Read the Parquet file
df = pd.read_csv('challenger_matches.csv')

# Display the data
print(df)
