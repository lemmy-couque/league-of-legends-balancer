import requests
import time
import pandas as pd

RIOT_API_KEY = "RGAPI-66a350e3-6a0f-4e0c-9a2d-9f779328473b"  # Remplacez par votre clé API
CHALLENGER_URL = "https://euw1.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5"
SUMMONER_URL = "https://euw1.api.riotgames.com/lol/summoner/v4/summoners/"
MATCH_URL = "https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
MATCH_DETAILS_URL = "https://europe.api.riotgames.com/lol/match/v5/matches/{matchId}"

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


def get_challenger_summoners():
    """Récupère la liste des summonerId des joueurs Challenger."""
    try:
        response = requests.get(CHALLENGER_URL, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return [entry['summonerId'] for entry in data['entries']]
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération des Challenger summoners : {e}")
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


def get_all_challenger_puuids():
    summoner_ids = get_challenger_summoners()
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


def get_all_challenger_matches(puuids):
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
    """Convertit les données de matchs en DataFrame."""
    rows = []
    for match in matches_data:
        match_id = match.get('metadata', {}).get('matchId', None)
        game_start = match.get('info', {}).get('gameStartTimestamp', None)
        game_duration = match.get('info', {}).get('gameDuration', None)
        participants = match.get('info', {}).get('participants', [])
        
        for participant in participants:
            rows.append({
                "match_id": match_id,
                "summoner_name": participant.get('summonerName', None),
                "champion_id": participant.get('championId', None),
                "win": participant.get('win', None),
            })
    return pd.DataFrame(rows)


# Étapes principales
challenger_puuids = get_all_challenger_puuids()
challenger_matches = get_all_challenger_matches(challenger_puuids)
all_match_details = get_all_match_details(challenger_matches)

matches_df = save_matches_to_dataframe(all_match_details)
matches_df.to_csv("challenger_matches.csv", index=False)
print("Données des matchs sauvegardées dans 'challenger_matches.csv'")
