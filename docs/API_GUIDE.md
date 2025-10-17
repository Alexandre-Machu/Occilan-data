# Guide d'utilisation des APIs — OcciLan Stats

## Table des matières

1. [Riot API](#riot-api)
2. [Toornament API](#toornament-api)
3. [Rate Limiting](#rate-limiting)
4. [Exemples d'utilisation](#exemples-dutilisation)
5. [Gestion des erreurs](#gestion-des-erreurs)

---

## Riot API

### Configuration

1. **Obtenir une clé API**
   - Créer un compte sur [Riot Developer Portal](https://developer.riotgames.com/)
   - Générer une clé de développement (24h) ou production

2. **Configurer dans le projet**
   ```bash
   # .env
   RIOT_API_KEY=RGAPI-your-key-here
   ```

### Endpoints utilisés

#### 1. Account API (RIOT ID → PUUID)

```python
GET /riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}
```

**Exemple**:
```python
from src.api.riot_api import RiotAPIClient

client = RiotAPIClient()
account = client.get_account_by_riot_id("Player", "EUW")
# Returns: {"puuid": "...", "gameName": "Player", "tagLine": "EUW"}
```

**Réponse**:
```json
{
  "puuid": "abc123...",
  "gameName": "Player",
  "tagLine": "EUW"
}
```

---

#### 2. Summoner API (PUUID → Summoner)

```python
GET /lol/summoner/v4/summoners/by-puuid/{puuid}
```

**Exemple**:
```python
summoner = client.get_summoner_by_puuid(puuid)
# Returns: {"id": "...", "accountId": "...", "name": "...", ...}
```

**Réponse**:
```json
{
  "id": "summoner123",
  "accountId": "account456",
  "puuid": "abc123...",
  "name": "Player",
  "profileIconId": 29,
  "revisionDate": 1697500000000,
  "summonerLevel": 150
}
```

---

#### 3. Match API (Match History)

```python
GET /lol/match/v5/matches/by-puuid/{puuid}/ids
```

**Paramètres**:
- `start`: Index de départ (default: 0)
- `count`: Nombre de matchs (default: 20, max: 100)
- `queue`: ID de queue (420 = Ranked Solo, 0 = Custom)
- `startTime`: Timestamp epoch (secondes)
- `endTime`: Timestamp epoch (secondes)

**Exemple**:
```python
# Récupérer les 50 derniers matchs custom
match_ids = client.get_match_ids_by_puuid(
    puuid=puuid,
    count=50,
    queue=0,  # Custom games
    start_time=1697500000  # Date de début du tournoi
)
# Returns: ["EUW1_123456789", "EUW1_123456790", ...]
```

---

#### 4. Match Details API

```python
GET /lol/match/v5/matches/{matchId}
```

**Exemple**:
```python
match = client.get_match_details("EUW1_123456789")
```

**Structure de réponse**:
```json
{
  "metadata": {
    "matchId": "EUW1_123456789",
    "participants": ["puuid1", "puuid2", ...]
  },
  "info": {
    "gameCreation": 1697500000000,
    "gameDuration": 1800,
    "gameMode": "CLASSIC",
    "gameType": "CUSTOM_GAME",
    "participants": [
      {
        "puuid": "abc123...",
        "summonerName": "Player1",
        "championName": "Ahri",
        "kills": 5,
        "deaths": 2,
        "assists": 10,
        "totalMinionsKilled": 180,
        "goldEarned": 12000,
        "totalDamageDealtToChampions": 25000,
        "visionScore": 45,
        "win": true,
        ...
      },
      ...
    ]
  }
}
```

---

#### 5. Match Timeline API (optionnel)

```python
GET /lol/match/v5/matches/{matchId}/timeline
```

**Utilité**: Analyse détaillée (early game, objectives, etc.)

**Exemple**:
```python
timeline = client.get_match_timeline("EUW1_123456789")
# Returns: Detailed frame-by-frame events
```

---

## Toornament API

### Configuration (futur)

```bash
# .env
TOORNAMENT_API_KEY=your-key
TOORNAMENT_CLIENT_ID=your-client-id
TOORNAMENT_CLIENT_SECRET=your-secret
```

### Endpoints prévus

#### 1. Get Tournament
```python
GET /tournaments/{tournament_id}
```

#### 2. Get Participants
```python
GET /tournaments/{tournament_id}/participants
```

#### 3. Get Matches
```python
GET /tournaments/{tournament_id}/matches
```

---

## Rate Limiting

### Riot API

**Limites par défaut** (clé développement):
- 20 requêtes / seconde
- 100 requêtes / 2 minutes

**Limites production**:
- Négociables selon le projet

### Stratégie implémentée

```python
class RiotAPIClient:
    def __init__(self):
        self.rate_limiter = RateLimiter(max_calls=20, period=1)
    
    def _request(self, url):
        self.rate_limiter.wait_if_needed()
        return requests.get(url, headers=self.headers)
```

### Gestion des erreurs 429 (Rate Limit)

```python
try:
    response = requests.get(url)
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 429:
        retry_after = int(e.response.headers.get('Retry-After', 5))
        time.sleep(retry_after)
        # Retry
```

---

## Exemples d'utilisation

### Exemple 1: Récupérer les infos d'un joueur

```python
from src.api.riot_api import RiotAPIClient

client = RiotAPIClient()

# Étape 1: Riot ID → PUUID
account = client.get_account_by_riot_id("Faker", "KR")
puuid = account['puuid']

# Étape 2: PUUID → Summoner
summoner = client.get_summoner_by_puuid(puuid)
print(f"Level: {summoner['summonerLevel']}")

# Étape 3: Récupérer les matchs
match_ids = client.get_match_ids_by_puuid(puuid, count=10)
print(f"Found {len(match_ids)} matches")
```

---

### Exemple 2: Analyser un match

```python
match_id = "EUW1_123456789"
match = client.get_match_details(match_id)

# Infos générales
duration = match['info']['gameDuration']
game_mode = match['info']['gameMode']

# Participants
for participant in match['info']['participants']:
    print(f"{participant['summonerName']} ({participant['championName']})")
    print(f"  KDA: {participant['kills']}/{participant['deaths']}/{participant['assists']}")
    print(f"  Damage: {participant['totalDamageDealtToChampions']}")
```

---

### Exemple 3: Récupérer tous les matchs d'une période

```python
import datetime

# Date du tournoi
start = datetime.datetime(2025, 1, 15, 0, 0, 0)
end = datetime.datetime(2025, 1, 17, 23, 59, 59)

start_timestamp = int(start.timestamp())
end_timestamp = int(end.timestamp())

# Récupérer matchs custom uniquement
match_ids = client.get_match_ids_by_puuid(
    puuid=player_puuid,
    count=100,
    queue=0,  # Custom games
    start_time=start_timestamp,
    end_time=end_timestamp
)

print(f"Found {len(match_ids)} tournament matches")
```

---

### Exemple 4: Traiter plusieurs joueurs (batch)

```python
from concurrent.futures import ThreadPoolExecutor

def get_player_matches(puuid):
    try:
        return client.get_match_ids_by_puuid(puuid, count=50)
    except Exception as e:
        print(f"Error for {puuid}: {e}")
        return []

# Liste de PUUIDs
player_puuids = ["puuid1", "puuid2", "puuid3", ...]

# Paralléliser les requêtes
with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(get_player_matches, player_puuids))

# Dédupliquer les match IDs
all_match_ids = set()
for match_list in results:
    all_match_ids.update(match_list)

print(f"Total unique matches: {len(all_match_ids)}")
```

---

## Gestion des erreurs

### Codes d'erreur HTTP courants

| Code | Signification | Action recommandée |
|------|---------------|-------------------|
| 400 | Bad Request | Vérifier les paramètres |
| 401 | Unauthorized | Vérifier la clé API |
| 403 | Forbidden | Clé API invalide/expirée |
| 404 | Not Found | Joueur/match introuvable |
| 429 | Rate Limited | Attendre et réessayer |
| 500 | Server Error | Réessayer plus tard |
| 503 | Service Unavailable | Réessayer plus tard |

### Template de gestion d'erreurs

```python
import time
import requests

def safe_api_call(func, *args, max_retries=3, **kwargs):
    """Wrapper pour appels API avec retry"""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code
            
            if status == 429:
                # Rate limit
                retry_after = int(e.response.headers.get('Retry-After', 5))
                print(f"Rate limited. Waiting {retry_after}s...")
                time.sleep(retry_after)
            
            elif status in [500, 503]:
                # Server error - retry
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Server error. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            
            elif status == 404:
                # Not found - don't retry
                print("Resource not found")
                return None
            
            else:
                # Other errors - don't retry
                raise
        
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            time.sleep(2 ** attempt)
    
    raise Exception(f"Failed after {max_retries} attempts")
```

---

## Bonnes pratiques

### 1. Respect des rate limits
- Ne jamais dépasser les limites
- Implémenter un rate limiter
- Espacer les requêtes

### 2. Cache local
- Stocker les réponses API
- Éviter les appels redondants
- Invalider le cache si nécessaire

### 3. Gestion des erreurs
- Toujours wrapper les appels API
- Logger les erreurs
- Retry avec backoff exponentiel

### 4. Optimisation
- Batch requests quand possible
- Paralléliser avec ThreadPoolExecutor
- Limiter le nombre de workers

### 5. Respect des CGU
- Usage non commercial
- Pas de scraping excessif
- Attribution correcte

---

## Références

- [Riot API Documentation](https://developer.riotgames.com/docs/lol)
- [Toornament API Documentation](https://developer.toornament.com/doc)
- [Rate Limiting Best Practices](https://developer.riotgames.com/docs/portal#web-apis_rate-limiting)

---

**Dernière mise à jour**: 2025-10-17
