import os
import requests
from dotenv import load_dotenv

load_dotenv()

RIOT_API_KEY = os.getenv("RIOT_API_KEY")

# Exemple d'URL d'API
# Remplace "summoner_name" par le nom d'invocateur que tu veux rechercher
BASE_URL = "https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/"
summoner_name = "NomDeLInvocateur"  # Remplace par le nom de l'invocateur
url = f"{BASE_URL}{summoner_name}"

# En-têtes pour l'API
headers = {
    "X-Riot-Token": RIOT_API_KEY
}

# Requête API
response = requests.get(url, headers=headers)

# Vérification et affichage de la réponse
if response.status_code == 200:
    data = response.json()
    print("Informations de l'invocateur :", data)
else:
    print(f"Erreur {response.status_code}: {response.text}")
