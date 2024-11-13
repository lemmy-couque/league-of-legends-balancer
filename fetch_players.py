import requests
import pandas as pd
import time

# Ta clé API
RIOT_API_KEY = "RGAPI-8900586f-0aca-453c-92a3-da2c4c4e956b"

# URL de base pour l'API League
LEAGUE_URL = "https://euw1.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5"
# URLs spécifiques pour les rangs Master, Grandmaster, Challenger
HIGH_TIER_URLS = {
    "MASTER": "https://euw1.api.riotgames.com/lol/league/v4/masterleagues/by-queue/RANKED_SOLO_5x5",
    "GRANDMASTER": "https://euw1.api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/RANKED_SOLO_5x5",
    "CHALLENGER": "https://euw1.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5"
}

# Headers avec la clé API
headers = {"X-Riot-Token": RIOT_API_KEY}

def get_players_by_rank(tier, division=None, page=1):
    """Récupère les joueurs pour un rang et une division spécifiques."""
    params = {"page": page}
    url = f"{LEAGUE_URL}/{tier}/{division}" if division else f"{HIGH_TIER_URLS.get(tier)}"
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        print("Rate limit exceeded. Sleeping for 15 seconds...")
        time.sleep(15)  # Attend 15 secondes avant de réessayer
        return get_players_by_rank(tier, division, page)  # Requête récursive après la pause
    else:
        print(f"Erreur {response.status_code}: {response.text}")
        return []

def fetch_all_players_above_gold():
    """Récupère tous les joueurs dans les rangs Platinum et supérieurs, y compris les joueurs Master, Grandmaster, Challenger."""
    tiers = ["PLATINUM", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"]
    divisions = ["I", "II", "III", "IV"]
    all_players = []

    # Récupère les joueurs Master, Grandmaster, Challenger séparément
    for tier in ["MASTER", "GRANDMASTER", "CHALLENGER"]:
        players = get_players_by_rank(tier)
        all_players.extend(players)

    # Récupère les joueurs Platinum et Diamond avec pagination
    for tier in ["PLATINUM", "DIAMOND"]:
        for division in divisions:
            page = 1
            while True:
                players = get_players_by_rank(tier, division, page)
                if not players:
                    break
                all_players.extend(players)
                page += 1

    return all_players

def save_players_to_parquet(players):
    """Sauvegarde les joueurs dans un fichier Parquet."""
    # Créer une liste de dictionnaires avec les données des joueurs
    player_data = []
    for player in players:
        player_data.append({
            'summoner_name': player.get('summonerName', 'Nom non disponible'),
            'tier': player.get('tier', 'Rang inconnu'),
            'rank': player.get('rank', 'Classement inconnu'),
            'league_points': player.get('leaguePoints', 0)
        })
    
    # Convertir la liste de dictionnaires en DataFrame pandas
    df = pd.DataFrame(player_data)
    
    # Sauvegarder le DataFrame dans un fichier Parquet
    df.to_parquet('players.parquet', engine='pyarrow', index=False)
    print("Données des joueurs enregistrées dans 'players.parquet'.")

if __name__ == "__main__":
    players_above_gold = fetch_all_players_above_gold()
    print(f"Nombre de joueurs récupérés : {len(players_above_gold)}")

    # Sauvegarde les joueurs dans le fichier Parquet
    save_players_to_parquet(players_above_gold)

