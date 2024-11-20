import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# Get the API key
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
if not RIOT_API_KEY:
    raise ValueError("La clé API n'est pas définie dans le fichier .env")

# URLs API
CHAMPION_MASTERY_URL = "https://euw1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{summonerId}"
CHAMPION_DATA_URL = "http://ddragon.leagueoflegends.com/cdn/13.19.1/data/en_US/champion.json"


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


# Étape 2 : Récupérer le score de maîtrise
def get_champion_mastery(summoner_id, champion_id):
    """Récupère le score de maîtrise d'un joueur pour un champion donné."""
    try:
        response = requests.get(CHAMPION_MASTERY_URL.format(summonerId=summoner_id), headers={"X-Riot-Token": RIOT_API_KEY}, timeout=10)
        response.raise_for_status()
        masteries = response.json()
        for mastery in masteries:
            if mastery["championId"] == champion_id:
                return mastery["championPoints"]
        return 0  # Si le joueur n'a pas de maîtrise sur ce champion
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération de la maîtrise pour {summoner_id} : {e}")
        return None


# Étape 3 : Enrichir les données des matchs
def enrich_match_data(matches_df, champion_mapping):
    """Ajoute les noms des champions, le rôle, le score de maîtrise et les bans."""
    matches_df['champion_name'] = matches_df['champion_id'].map(champion_mapping)

    # Ajouter le rôle depuis la colonne `teamPosition`
    matches_df['role'] = matches_df['role'].fillna('UNKNOWN')

    # Exemple fictif pour récupérer les bans et score de maîtrise (à adapter selon vos données)
    matches_df['bans_team_1'] = matches_df['match_id'].apply(lambda x: get_bans_for_team(x, team=1))
    matches_df['bans_team_2'] = matches_df['match_id'].apply(lambda x: get_bans_for_team(x, team=2))

    matches_df['mastery_score'] = matches_df.apply(
        lambda row: get_champion_mastery(row['summoner_id'], row['champion_id']),
        axis=1
    )
    return matches_df


# Étape 4 : Calculer les win rates par rôle et champion
def calculate_win_rates(matches_df):
    """Calcule les win rates par champion et rôle."""
    win_rates = (
        matches_df.groupby(['champion_name', 'role'])
        .agg(
            total_matches=('win', 'count'),
            wins=('win', 'sum'),
            avg_mastery_score=('mastery_score', 'mean')
        )
        .reset_index()
    )
    win_rates['win_rate'] = (win_rates['wins'] / win_rates['total_matches']) * 100
    return win_rates


# Charger les données existantes
matches_df = pd.read_csv("summoner_matches.csv")

# Obtenir le mapping champion_id -> nom
champion_mapping = fetch_champion_mapping()

# Enrichir les données des matchs
matches_df = enrich_match_data(matches_df, champion_mapping)

# Calculer les win rates
win_rate_df = calculate_win_rates(matches_df)

# Sauvegarder les résultats
matches_df.to_csv("detailed_matches.csv", index=False)
win_rate_df.to_csv("champion_win_rates_by_role.csv", index=False)

print("Les données détaillées des matchs sont sauvegardées dans 'detailed_matches.csv'.")
print("Les win rates des champions par rôle sont sauvegardés dans 'champion_win_rates_by_role.csv'.")
