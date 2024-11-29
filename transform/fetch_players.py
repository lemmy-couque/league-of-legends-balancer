import requests
import time
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve the Riot Games API key
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
if not RIOT_API_KEY:
    raise ValueError("The API key is not defined in the .env file.")

# Riot Games API URLs
MASTER_URL = "https://euw1.api.riotgames.com/lol/league/v4/masterleagues/by-queue/RANKED_SOLO_5x5"
GRANDMASTER_URL = "https://euw1.api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/RANKED_SOLO_5x5"
CHALLENGER_URL = "https://euw1.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5"
SUMMONER_URL = "https://euw1.api.riotgames.com/lol/summoner/v4/summoners/"
MATCH_URL = "https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
MATCH_DETAILS_URL = "https://europe.api.riotgames.com/lol/match/v5/matches/{matchId}"
MASTERY_URL = "https://euw1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{summonerId}"

# API request headers
headers = {"X-Riot-Token": RIOT_API_KEY}

# Parameters for match history requests
params = {
    "startTime": int(time.time()) - (7 * 24 * 60 * 60),  # 7 days of history
    "endTime": int(time.time()),
    "queue": 420,  # Ranked Solo/Duo
    "start": 0,
    "count": 100,
}


def get_summoners(url: str) -> list:
    """
    Retrieve a list of summoner IDs from a specified league URL.

    Args:
        url (str): API URL for a specific league (e.g., Challenger).

    Returns:
        list: A list of summoner IDs.
    """
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return [entry['summonerId'] for entry in data['entries']]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching summoners from {url}: {e}")
        return []


def get_puuid(summoner_id: str) -> str:
    """
    Convert a summoner ID to a PUUID.

    Args:
        summoner_id (str): Summoner ID.

    Returns:
        str: The corresponding PUUID, or None if an error occurs.
    """
    try:
        response = requests.get(f"{SUMMONER_URL}{summoner_id}", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get('puuid')
        elif response.status_code == 429:
            print("Rate limit exceeded. Retrying after 15 seconds...")
            time.sleep(15)
            return get_puuid(summoner_id)
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Network error while converting summoner ID: {e}")
        return None


def get_all_puuids() -> list:
    """
    Retrieve all PUUIDs for Challenger players.

    Returns:
        list: A list of PUUIDs.
    """
    challenger_summoners = get_summoners(CHALLENGER_URL)
    puuids = []

    for i, summoner_id in enumerate(challenger_summoners):
        if i > 0 and i % 20 == 0:  # Pause after every 20 requests
            time.sleep(1)
        puuid = get_puuid(summoner_id)
        if puuid:
            puuids.append(puuid)

    print(f"Total PUUIDs retrieved: {len(puuids)}")
    return puuids


def get_matches(puuid: str) -> list:
    """
    Retrieve match IDs associated with a given PUUID.

    Args:
        puuid (str): The player's PUUID.

    Returns:
        list: A list of match IDs.
    """
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
            print(f"Error {response.status_code}: {response.text}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Network error fetching matches for {puuid}: {e}")
        return []


def get_all_matches(puuids: list) -> list:
    """
    Retrieve all match IDs for a list of PUUIDs.

    Args:
        puuids (list): List of PUUIDs.

    Returns:
        list: A list of unique match IDs.
    """
    matches = []
    for i, puuid in enumerate(puuids):
        if i > 0 and i % 10 == 0:  # Pause after every 10 requests
            time.sleep(2)
        match_ids = get_matches(puuid)
        matches.extend(match_ids)

    unique_matches = list(set(matches))
    print(f"Total unique matches retrieved: {len(unique_matches)}")
    return unique_matches


def get_match_details(match_id: str) -> dict:
    """
    Retrieve details of a match by its match ID.

    Args:
        match_id (str): Match ID.

    Returns:
        dict: Match details, or None if an error occurs.
    """
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
            print(f"Error {response.status_code}: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Network error fetching match details for {match_id}: {e}")
        return None


def get_all_match_details(match_ids: list) -> list:
    """
    Retrieve details for a list of match IDs.

    Args:
        match_ids (list): List of match IDs.

    Returns:
        list: A list of match details.
    """
    matches_data = []
    for i, match_id in enumerate(match_ids):
        if i > 0 and i % 5 == 0:  # Pause after every 5 requests
            time.sleep(1)
        match_data = get_match_details(match_id)
        if match_data:
            matches_data.append(match_data)

    print(f"Total match details retrieved: {len(matches_data)}")
    return matches_data


def save_matches_to_dataframe(matches_data: list) -> pd.DataFrame:
    """
    Save match data into a DataFrame.

    Args:
        matches_data (list): List of match details.

    Returns:
        pd.DataFrame: A DataFrame containing structured match data.
    """
    rows = []
    for match in matches_data:
        match_id = match.get('metadata', {}).get('matchId')
        participants = match.get('info', {}).get('participants', [])
        teams = match.get('info', {}).get('teams', [])

        # Collect bans for each team
        bans_team_1 = [ban["championId"] for ban in teams[0].get("bans", [])] if len(teams) > 0 else []
        bans_team_2 = [ban["championId"] for ban in teams[1].get("bans", [])] if len(teams) > 1 else []

        for participant in participants:
            rows.append({
                "match_id": match_id,
                "summoner_name": participant.get('summonerName'),
                "champion_id": participant.get('championId'),
                "role": participant.get('teamPosition'),
                "win": participant.get('win'),
                "bans_team_1": bans_team_1,
                "bans_team_2": bans_team_2,
            })

    return pd.DataFrame(rows)

