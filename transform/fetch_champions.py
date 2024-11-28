import requests
import os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# Get the API key
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
if not RIOT_API_KEY:
    raise ValueError("La clé API n'est pas définie dans le fichier .env")

# URLs API
CHAMPION_DATA_URL = "http://ddragon.leagueoflegends.com/cdn/13.19.1/data/en_US/champion.json"
MATCH_DETAILS_URL = "https://europe.api.riotgames.com/lol/match/v5/matches/{matchId}"


# Étape 1 : Charger les données de correspondance champion_id -> nom
def fetch_champion_mapping():
    """Récupère la correspondance champion_id -> nom depuis Data Dragon."""
    response = requests.get(CHAMPION_DATA_URL)
    if response.status_code == 200:
        data = response.json()
        champion_data = data['data']
        return {int(champ['key']): champ['name'] for champ in champion_data.values()}
    else:
        print("Erreur lors du téléchargement des données des champions")
        return {}


# Étape 3 : Enrichir les données des matchs
def enrich_match_data(matches_df, champion_mapping):
    """Ajoute les noms des champions, le rôle, le score de maîtrise et les bans."""
    matches_df['champion_name'] = matches_df['champion_id'].map(champion_mapping)

    # Ajouter le rôle depuis la colonne `teamPosition`
    matches_df['role'] = matches_df['role'].fillna('UNKNOWN')

    return matches_df


# Étape 4 : Calculer les win rates par rôle et champion
def calculate_win_rates(matches_df):
    """Calcule les win rates par champion et rôle."""
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
