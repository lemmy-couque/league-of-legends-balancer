import requests
import time
import pandas as pd
import os
from dotenv import load_dotenv


# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupérer la clé API
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
if not RIOT_API_KEY:
    raise ValueError("La clé API n'est pas définie dans le fichier .env")

MASTER_URL = "https://euw1.api.riotgames.com/lol/league/v4/masterleagues/by-queue/RANKED_SOLO_5x5"
GRANDMASTER_URL = "https://euw1.api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/RANKED_SOLO_5x5"
CHALLENGER_URL = "https://euw1.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5"
SUMMONER_URL = "https://euw1.api.riotgames.com/lol/summoner/v4/summoners/"
MATCH_URL = "https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
MATCH_DETAILS_URL = "https://europe.api.riotgames.com/lol/match/v5/matches/{matchId}"
MASTERY_URL = "https://euw1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{summonerId}"


# Headers pour inclure votre clé API
headers = {"X-Riot-Token": RIOT_API_KEY}

# Parameters to fill before requesting match API
params = {
    "startTime": int(time.time()) - (7 * 24 * 60 * 60),  # 7 jours d'historique
    "endTime": int(time.time()),
    "queue": 420,  # Ranked Solo/Duo
    "start": 0,
    "count": 100,
}


def get_summoners(url):
    """Récupère la liste des summonerId des joueurs d'un rang donné."""
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return [entry['summonerId'] for entry in data['entries']]
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération des summoners depuis {url} : {e}")
        return []


def get_puuid(summoner_id):
    """Convertit un summonerId en puuid."""
    try:
        response = requests.get(f"{SUMMONER_URL}{summoner_id}", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()['puuid']
        elif response.status_code == 429:
            print("Rate limit exceeded. Retrying after 15 seconds...")
            time.sleep(15)
            return get_puuid(summoner_id)
        else:
            print(f"Erreur {response.status_code} : {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erreur réseau lors de la conversion du summonerId : {e}")
        return None


def get_all_puuids():
    challenger_summoners = get_summoners(CHALLENGER_URL)
    # master_summoners = get_summoners(MASTER_URL)
    # grandmaster_summoners = get_summoners(GRANDMASTER_URL)
    summoner_ids = challenger_summoners # + grandmaster_summoners + master_summoners
    puuids = []
    for i, summoner_id in enumerate(summoner_ids):
        if i > 0 and i % 20 == 0:  # Pause toutes les 20 requêtes
            time.sleep(1)
        puuid = get_puuid(summoner_id)
        if puuid:
            puuids.append(puuid)
    print(f"Nombre total de PUUIDs récupérés : {len(puuids)}")
    return puuids


def get_matches(puuid):
    """Get every match ID related to a given puuid."""
    url = MATCH_URL.format(puuid=puuid)
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            print("Rate limit exceeded. Retrying after 15 seconds...")
            time.sleep(15)
            return get_matches(puuid)
        else:
            print(f"Erreur {response.status_code}: {response.text}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Erreur réseau lors de la récupération des matchs pour {puuid} : {e}")
        return []


def get_all_matches(puuids):
    matches = []
    for i, puuid in enumerate(puuids):
        if i > 0 and i % 10 == 0:  # Pause toutes les 10 requêtes
            time.sleep(2)
        match_ids = get_matches(puuid)
        matches.extend(match_ids)
    print(f"Nombre total de matchs uniques récupérés : {len(set(matches))}")
    return list(set(matches))


def get_match_details(match_id):
    """Récupère les détails d'un match via son matchId."""
    url = MATCH_DETAILS_URL.format(matchId=match_id)
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            print("Rate limit exceeded. Retrying after 15 seconds...")
            time.sleep(15)
            return get_match_details(match_id)
        else:
            print(f"Erreur {response.status_code}: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erreur réseau lors de la récupération des détails du match {match_id} : {e}")
        return None


def get_all_match_details(match_ids):
    """Récupère les détails pour une liste de match IDs."""
    matches_data = []
    for i, match_id in enumerate(match_ids):
        if i > 0 and i % 5 == 0:  # Pause toutes les 5 requêtes
            time.sleep(1)
        match_data = get_match_details(match_id)
        if match_data:
            matches_data.append(match_data)
    print(f"Nombre total de détails de matchs récupérés : {len(matches_data)}")
    return matches_data


def save_matches_to_dataframe(matches_data):
    rows = []
    for match in matches_data:
        match_id = match.get('metadata', {}).get('matchId', None)
        participants = match.get('info', {}).get('participants', [])
        teams = match.get('info', {}).get('teams', [])
        
        # Collecter les bans pour chaque équipe
        bans_team_1 = [ban["championId"] for ban in teams[0].get("bans", [])] if len(teams) > 0 else []
        bans_team_2 = [ban["championId"] for ban in teams[1].get("bans", [])] if len(teams) > 1 else []
        
        for participant in participants:
            summoner_id = participant.get('summonerId', None)
            champion_id = participant.get('championId', None)
                        
            rows.append({
                "match_id": match_id,
                "summoner_name": participant.get('summonerName', None),
                "champion_id": champion_id,
                "role": participant.get('teamPosition', None),
                "win": participant.get('win', None),
                "bans_team_1": bans_team_1,  # Bans équipe 1
                "bans_team_2": bans_team_2,  # Bans équipe 2
            })
    return pd.DataFrame(rows)


# Étapes principales
summoner_puuids = get_all_puuids()
summoner_matches = get_all_matches(summoner_puuids)
all_match_details = get_all_match_details(summoner_matches)

matches_df = save_matches_to_dataframe(all_match_details)
matches_df.to_csv("datasets/summoner_matches.csv", index=False)
print("Données des matchs sauvegardées dans 'summoner_matches.csv'")
