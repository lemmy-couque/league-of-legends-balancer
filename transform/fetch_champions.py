import requests
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve the Riot Games API key
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
if not RIOT_API_KEY:
    raise ValueError("The API key is not defined in the .env file.")

# API URLs
CHAMPION_DATA_URL = "http://ddragon.leagueoflegends.com/cdn/13.19.1/data/en_US/champion.json"
MATCH_DETAILS_URL = "https://europe.api.riotgames.com/lol/match/v5/matches/{matchId}"


def fetch_champion_mapping() -> dict:
    """
    Fetches champion data from Data Dragon and maps champion IDs to champion names.

    Returns:
        dict: A dictionary mapping champion IDs (int) to their respective names (str).
    """
    try:
        response = requests.get(CHAMPION_DATA_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        champion_data = data['data']
        return {int(champ['key']): champ['name'] for champ in champion_data.values()}
    except requests.exceptions.RequestException as e:
        print(f"Error fetching champion data: {e}")
        return {}


def enrich_match_data(matches_df, champion_mapping: dict):
    """
    Enriches match data by adding champion names, roles, and additional details.

    Args:
        matches_df (pd.DataFrame): DataFrame containing match data with a `champion_id` column.
        champion_mapping (dict): A dictionary mapping champion IDs to names.

    Returns:
        pd.DataFrame: The enriched match data.
    """
    # Map champion IDs to names
    matches_df['champion_name'] = matches_df['champion_id'].map(champion_mapping)

    # Fill missing roles with 'UNKNOWN'
    matches_df['role'] = matches_df['role'].fillna('UNKNOWN')

    return matches_df


def calculate_win_rates(matches_df):
    """
    Calculates win rates grouped by champion and role.

    Args:
        matches_df (pd.DataFrame): DataFrame containing match data with columns:
                                   - `champion_name` (str): The name of the champion.
                                   - `role` (str): The role of the champion in the game.
                                   - `win` (bool): Whether the champion won the match.

    Returns:
        pd.DataFrame: A DataFrame containing win rates for each champion and role.
                      Columns include:
                      - `champion_name`
                      - `role`
                      - `total_matches`
                      - `wins`
                      - `win_rate`
    """
    win_rates = (
        matches_df.groupby(['champion_name', 'role'])
        .agg(
            total_matches=('win', 'count'),
            wins=('win', 'sum')
        )
        .reset_index()
    )
    win_rates['win_rate'] = (win_rates['wins'] / win_rates['total_matches']) * 100
    return win_rates
