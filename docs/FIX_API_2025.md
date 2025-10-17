# 🔧 Fix API Riot — Octobre 2025

## Problème découvert

L'API Riot a changé la structure de Summoner-V4 et League-V4 :

### Avant (2024)
```python
# Summoner-V4 retournait:
{
    "id": "encrypted_summoner_id",  # ← N'existe plus
    "name": "Summoner Name",         # ← N'existe plus
    "puuid": "...",
    "summonerLevel": 589
}

# League-V4 utilisait summoner_id:
GET /lol/league/v4/entries/by-summoner/{summoner_id}
```

### Après (2025)
```python
# Summoner-V4 retourne maintenant:
{
    "puuid": "...",
    "profileIconId": 6923,
    "revisionDate": 1760129138000,
    "summonerLevel": 589
    # Plus de champs "id" ni "name"
}

# League-V4 utilise maintenant directement le PUUID:
GET /lol/league/v4/entries/by-puuid/{puuid}
```

## Solution appliquée

### 1. Modifié `get_summoner_by_puuid()`
```python
# Avant
self.puuid_map[puuid] = result["name"]  # ❌ KeyError
logger.info(f"✓ Summoner info found: {result['name']}")  # ❌

# Après
summoner_name = result.get("gameName", result.get("name", "Unknown"))
self.puuid_map[puuid] = summoner_name
logger.info(f"✓ Summoner info found (level {result.get('summonerLevel', '?')})")  # ✅
```

### 2. Modifié `get_ranked_info()`
```python
# Avant
def get_ranked_info(self, summoner_id: str):
    url = f".../lol/league/v4/entries/by-summoner/{summoner_id}"  # ❌

# Après
def get_ranked_info(self, puuid: str):
    url = f".../lol/league/v4/entries/by-puuid/{puuid}"  # ✅
```

### 3. Modifié `get_player_full_info()`
```python
# Avant
return {
    "summoner_id": summoner["id"],  # ❌ KeyError
    "summoner_name": summoner["name"],  # ❌ KeyError
}

# Après
return {
    "puuid": puuid,  # ✅ PUUID suffit maintenant
    "summoner_name": summoner.get("gameName", game_name),  # ✅ Fallback
    "summoner_level": summoner["summonerLevel"],
    "profile_icon_id": summoner.get("profileIconId"),
}
```

## Test validé

```bash
python scripts/test_api_real.py
```

**Résultat :**
```
[OK] Joueur trouve!
   Riot ID: Colfeo#LRC
   Summoner: Colfeo
   Niveau: 589
   PUUID: QeJhymObZO6iAA4vLGpz...
   Rank SoloQ: EMERALD IV (76 LP)
   Winrate: 63W 53L (54.3%)

   Recherche des custom games recents...
   [INFO] Aucun custom game trouve (normal)
```

✅ **Toutes les APIs fonctionnent !**

## Impact sur le reste du code

### Fichiers à vérifier
- ✅ `src/core/riot_client.py` — Corrigé
- ⚠️ `src/core/data_manager.py` — Vérifie les champs `summoner_id` stockés
- ⚠️ Documentation — Mettre à jour `docs/API_WORKFLOW.md`

### Champs JSON à adapter

Dans `teams_with_puuid.json`, on n'a plus besoin de `summoner_id` :

**Avant :**
```json
{
  "puuid": "...",
  "summoner_id": "xyz789...",  // ← Plus nécessaire
  "summoner_name": "Player1"
}
```

**Après :**
```json
{
  "puuid": "...",  // ← Suffit pour toutes les APIs
  "summoner_name": "Player1"
}
```

## Notes importantes

1. **PUUID est maintenant la clé primaire** pour toutes les APIs Riot
2. **Summoner-V4** ne retourne plus `id` ni `name` (champs legacy)
3. **League-V4** accepte maintenant `/entries/by-puuid/{puuid}`
4. **Compatibilité** : Les anciens projets utilisant `summoner_id` doivent être mis à jour

## Date de changement API

Cette modification Riot semble avoir été faite **courant 2025** (API testée le 17 octobre 2025).

---

**Fix validé et fonctionnel !** ✅
