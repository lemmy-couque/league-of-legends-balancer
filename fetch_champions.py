import requests
import pandas as pd
import os
from dotenv import load_dotenv
import time

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



# Étape 2 : Récupérer les bans pour une équipe
def get_bans_for_team(match_id, team):
    """
    Récupère les champions bannis pour une équipe dans un match donné.

    Parameters:
    - match_id (str): ID du match
    - team (int): Numéro de l'équipe (1 ou 2)

    Returns:
    - list: Liste des IDs des champions bannis
    """
    try:
        while True:  # Boucle pour réessayer en cas de limite atteinte
            response = requests.get(
                MATCH_DETAILS_URL.format(matchId=match_id),
                headers={"X-Riot-Token": RIOT_API_KEY},
                timeout=10
            )
            
            if response.status_code == 200:
                match_data = response.json()
                teams = match_data.get("info", {}).get("teams", [])
                if team == 1:
                    bans = teams[0].get("bans", [])
                elif team == 2:
                    bans = teams[1].get("bans", [])
                else:
                    print(f"Numéro d'équipe invalide : {team}")
                    return []
                return [ban["championId"] for ban in bans]

            elif response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 15))
                print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
            else:
                print(f"Erreur {response.status_code}: {response.text}")
                return []

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération des bans pour le match {match_id} : {e}")
        return []
    except (IndexError, KeyError) as e:
        print(f"Erreur dans les données pour le match {match_id} : {e}")
        return []


# Étape 3 : Enrichir les données des matchs
def enrich_match_data(matches_df, champion_mapping):
    """Ajoute les noms des champions, le rôle, le score de maîtrise et les bans."""
    matches_df['champion_name'] = matches_df['champion_id'].map(champion_mapping)

    # Ajouter le rôle depuis la colonne `teamPosition`
    matches_df['role'] = matches_df['role'].fillna('UNKNOWN')

    # Ajouter les bans par équipe avec une pause pour éviter la limite
    bans_team_1 = []
    bans_team_2 = []

    for i, match_id in enumerate(matches_df['match_id']):
        if i > 0 and i % 10 == 0:  # Pause toutes les 10 requêtes
            time.sleep(2)
        bans_team_1.append(get_bans_for_team(match_id, team=1))
        bans_team_2.append(get_bans_for_team(match_id, team=2))

    matches_df['bans_team_1'] = bans_team_1
    matches_df['bans_team_2'] = bans_team_2

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
