# 🔄 Workflow API Riot — Guide Complet

## 📋 Vue d'ensemble

Ce document décrit **exactement** les appels API nécessaires pour récupérer toutes les données, comme OP.GG le fait.

---

## 🎯 Étape 1: Riot ID → PUUID

### Endpoint: Account-V1
```
GET https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}
```

**Paramètres:**
- `region`: `europe` (pour EUW/EUNE), `americas`, `asia`, `sea`
- `gameName`: "Player1" (sans le #)
- `tagLine`: "EUW" (après le #)

**Exemple:**
```python
# Pour "Player1#EUW"
url = "https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/Player1/EUW"
headers = {"X-Riot-Token": RIOT_API_KEY}
response = requests.get(url, headers=headers)

# Response:
{
    "puuid": "abc123...",
    "gameName": "Player1",
    "tagLine": "EUW"
}
```

**Note:** OP.GG parse automatiquement les liens multisearch pour extraire les `gameName#tagLine`.

---

## 🎯 Étape 2: PUUID → Summoner Info

### Endpoint: Summoner-V4
```
GET https://{platform}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}
```

**Paramètres:**
- `platform`: `euw1` (pas "europe" ici!)
- `puuid`: reçu de l'étape 1

**Exemple:**
```python
url = f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
response = requests.get(url, headers=headers)

# Response:
{
    "id": "encrypted_summoner_id_xyz789",  # ← Important pour l'étape 3
    "accountId": "...",
    "puuid": "abc123...",
    "name": "Player1",  # Nom d'invocateur (peut différer du gameName)
    "profileIconId": 1234,
    "summonerLevel": 234
}
```

**Important:** Récupère `id` (encryptedSummonerId) nécessaire pour League-V4.

---

## 🎯 Étape 3: Summoner ID → Rank Actuel

### Endpoint: League-V4
```
GET https://{platform}.api.riotgames.com/lol/league/v4/entries/by-summoner/{encryptedSummonerId}
```

**Paramètres:**
- `platform`: `euw1`
- `encryptedSummonerId`: `id` reçu de l'étape 2

**Exemple:**
```python
url = f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}"
response = requests.get(url, headers=headers)

# Response: Liste (SoloQ + Flex)
[
    {
        "queueType": "RANKED_SOLO_5x5",
        "tier": "DIAMOND",
        "rank": "II",
        "leaguePoints": 45,
        "wins": 127,
        "losses": 98,
        "veteran": false,
        "hotStreak": true
    },
    {
        "queueType": "RANKED_FLEX_SR",
        "tier": "PLATINUM",
        "rank": "I",
        "leaguePoints": 82,
        "wins": 45,
        "losses": 32
    }
]
```

**À stocker dans teams_with_puuid.json:**
```json
{
    "ranked_tier": "DIAMOND",
    "ranked_rank": "II",
    "ranked_lp": 45,
    "wins": 127,
    "losses": 98
}
```

**Cas spéciaux:**
- Si joueur unranked → liste vide `[]`
- Challenger/GM/Master → pas de `rank` (juste `tier`)

---

## 🎯 Étape 4: PUUID → Match IDs (Custom Games)

### Endpoint: Match-V5 (list)
```
GET https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids
```

**Paramètres:**
- `region`: `europe` (macro routing, comme Account-V1)
- `puuid`: PUUID du joueur
- Query params:
  - `queue=0` (custom games)
  - `startTime=1609459200` (timestamp Unix, début tournoi)
  - `endTime=1612137600` (timestamp Unix, fin tournoi)
  - `count=100` (max 100 par page)

**Exemple:**
```python
url = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
params = {
    "queue": 0,  # Custom games
    "startTime": int(start_date.timestamp()),
    "endTime": int(end_date.timestamp()),
    "count": 100
}
response = requests.get(url, headers=headers, params=params)

# Response: Liste d'IDs
[
    "EUW1_6234567890",
    "EUW1_6234567891",
    "EUW1_6234567892"
]
```

**Important:**
- Faire 1 appel **par équipe** (via 1 joueur de chaque équipe)
- Queue 0 = custom games (tournois)
- Dates précises évitent de récupérer des scrims hors tournoi

---

## 🎯 Étape 5: Match ID → Détails Complets

### Endpoint: Match-V5 (details)
```
GET https://{region}.api.riotgames.com/lol/match/v5/matches/{matchId}
```

**Paramètres:**
- `region`: `europe`
- `matchId`: "EUW1_6234567890"

**Exemple:**
```python
url = f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}"
response = requests.get(url, headers=headers)

# Response: Objet massif (~20-30KB)
{
    "metadata": {
        "matchId": "EUW1_6234567890",
        "participants": ["puuid1", "puuid2", ...]
    },
    "info": {
        "gameCreation": 1609459200000,
        "gameDuration": 1847,  # Secondes
        "gameMode": "CLASSIC",
        "queueId": 0,
        "participants": [
            {
                "puuid": "abc123...",
                "summonerName": "Player1",
                "championId": 157,  # Yasuo
                "championName": "Yasuo",
                "teamPosition": "MIDDLE",
                "kills": 7,
                "deaths": 3,
                "assists": 12,
                "totalMinionsKilled": 245,
                "neutralMinionsKilled": 12,
                "goldEarned": 14250,
                "totalDamageDealtToChampions": 28500,
                "visionScore": 42,
                "wardsPlaced": 15,
                "wardsKilled": 8,
                "win": true,
                "item0": 3078,  # Trinity Force
                # ... 5 autres items
                "summoner1Id": 4,  # Flash
                "summoner2Id": 14,  # Ignite
                "perks": {...}  # Runes
            }
            # ... 9 autres joueurs
        ],
        "teams": [
            {
                "teamId": 100,
                "win": true,
                "bans": [
                    {"championId": 11, "pickTurn": 1},  # Master Yi
                    {"championId": 53, "pickTurn": 2}   # Blitzcrank
                    # ... 3 autres bans
                ],
                "objectives": {
                    "baron": {"kills": 1, "first": false},
                    "dragon": {"kills": 3, "first": true},
                    "tower": {"kills": 9, "first": true}
                }
            },
            {
                "teamId": 200,
                "win": false,
                # ...
            }
        ]
    }
}
```

**Cache local obligatoire:**
```
data/cache/matches/EUW1_6234567890.json
```
→ Évite de refetch si match déjà récupéré (partagé entre éditions).

---

## 🎯 Étape 6: Champions Les Plus Joués (Agrégation)

**Méthode A: Depuis Match-V5 (recommandée)**

Après avoir récupéré tous les détails de matchs:

```python
# Agréger par joueur (PUUID) et champion
player_champions = {}

for match in match_details:
    for participant in match["info"]["participants"]:
        puuid = participant["puuid"]
        champ_id = participant["championId"]
        
        if puuid not in player_champions:
            player_champions[puuid] = {}
        
        if champ_id not in player_champions[puuid]:
            player_champions[puuid][champ_id] = {
                "games": 0,
                "wins": 0,
                "kills": 0,
                "deaths": 0,
                "assists": 0
            }
        
        player_champions[puuid][champ_id]["games"] += 1
        if participant["win"]:
            player_champions[puuid][champ_id]["wins"] += 1
        player_champions[puuid][champ_id]["kills"] += participant["kills"]
        player_champions[puuid][champ_id]["deaths"] += participant["deaths"]
        player_champions[puuid][champ_id]["assists"] += participant["assists"]

# Trier par nombre de parties
for puuid, champs in player_champions.items():
    sorted_champs = sorted(champs.items(), key=lambda x: x[1]["games"], reverse=True)
    player_champions[puuid] = sorted_champs[:3]  # Top 3
```

**Méthode B: Champion-Mastery-V4 (optionnel)**

```
GET https://{platform}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{encryptedSummonerId}
```

Renvoie les champions triés par **points de maîtrise** (historique global, pas saison actuelle).

**Note:** OP.GG utilise la **Méthode A** pour "Most Played (Season 14)".

---

## 📊 Résumé du Pipeline Complet

```
CSV Upload (team_name, opgg_link)
         ↓
    Parse OP.GG → Extract gameName#tagLine
         ↓
    Account-V1 (Riot ID → PUUID)
         ↓
    Summoner-V4 (PUUID → summoner_id)
         ↓
    League-V4 (summoner_id → rank/LP)
         ↓
    Match-V5 (PUUID → match IDs avec queue=0, dates tournoi)
         ↓
    Match-V5 (match ID → détails complets + cache)
         ↓
    Agrégation (KDA, CS/min, champions plus joués, records)
         ↓
    general_stats.json
```

---

## ⚙️ Paramètres Techniques

### Rate Limiting
- **Limite:** 20 requêtes/seconde (application rate limit)
- **Stratégie:** 
  - Ajouter `time.sleep(0.05)` entre requêtes (sécurité)
  - Gérer 429 (Too Many Requests) avec exponential backoff
  - Header `X-Rate-Limit-Count` à surveiller

### Retry Logic
```python
import time

def api_call_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        
        elif response.status_code == 429:  # Rate limit
            retry_after = int(response.headers.get("Retry-After", 1))
            print(f"Rate limited, waiting {retry_after}s...")
            time.sleep(retry_after)
        
        elif response.status_code == 404:  # Not found
            return None
        
        else:
            print(f"Error {response.status_code}, retrying...")
            time.sleep(2 ** attempt)  # Exponential backoff
    
    raise Exception(f"Failed after {max_retries} retries")
```

### Regional Routing

| API | Region | Platform |
|-----|--------|----------|
| Account-V1 | `europe` | N/A |
| Summoner-V4 | N/A | `euw1` |
| League-V4 | N/A | `euw1` |
| Match-V5 | `europe` | N/A |

**Important:** 
- `region` (europe/americas/asia) pour Account-V1 et Match-V5
- `platform` (euw1/na1/kr) pour Summoner-V4 et League-V4

---

## 🔍 Data Dragon (Assets)

Pour afficher les icônes de champions:

```
GET https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json
```

Exemple: Champion ID 157 → "Yasuo" → icône `Yasuo.png`

```
https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/Yasuo.png
```

**Latest version:**
```
GET https://ddragon.leagueoflegends.com/api/versions.json
```

---

## ✅ Checklist d'implémentation

- [ ] Account-V1: Riot ID → PUUID
- [ ] Summoner-V4: PUUID → summoner_id
- [ ] League-V4: summoner_id → rank/LP
- [ ] Match-V5 (list): PUUID → match IDs (queue=0, dates)
- [ ] Match-V5 (details): match ID → détails + cache
- [ ] Rate limiting (20 req/s)
- [ ] Retry logic (429, 5xx)
- [ ] Cache local (matches, puuid_map)
- [ ] Agrégation champions les plus joués
- [ ] Data Dragon (assets)

---

**Prêt pour l'implémentation de `core/riot_client.py` !** 🚀
