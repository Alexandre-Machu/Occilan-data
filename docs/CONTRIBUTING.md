# Guide de Contribution — OcciLan Stats

Merci de votre intérêt pour contribuer à OcciLan Stats ! 🎮

## Table des matières

1. [Code de conduite](#code-de-conduite)
2. [Comment contribuer](#comment-contribuer)
3. [Standards de code](#standards-de-code)
4. [Process de développement](#process-de-développement)
5. [Tests](#tests)
6. [Documentation](#documentation)

---

## Code de conduite

### Nos engagements

- Respect de tous les contributeurs
- Feedback constructif
- Collaboration bienveillante
- Focus sur le projet et la communauté OcciLan

---

## Comment contribuer

### Types de contributions

- 🐛 **Bug fixes**: Correction de bugs
- ✨ **Features**: Nouvelles fonctionnalités
- 📝 **Documentation**: Amélioration de la doc
- 🎨 **UI/UX**: Améliorations visuelles
- ⚡ **Performance**: Optimisations
- ✅ **Tests**: Ajout de tests

### Avant de commencer

1. **Vérifier les issues existantes**
   - Éviter les doublons
   - Voir si quelqu'un travaille déjà dessus

2. **Créer une issue** (pour features majeures)
   - Décrire le problème/feature
   - Discuter de l'approche
   - Obtenir un feedback

3. **Fork le repository**
   ```bash
   git clone https://github.com/votre-username/Occilan-data.git
   cd Occilan-data
   ```

---

## Standards de code

### Python Style Guide

**PEP 8** avec quelques adaptations :

#### Formatage

```python
# Utilisez Black pour le formatage automatique
black src/

# Ligne max: 100 caractères
# Indentation: 4 espaces
```

#### Naming conventions

```python
# Classes: PascalCase
class RiotAPIClient:
    pass

# Fonctions et variables: snake_case
def get_match_details():
    player_name = "Faker"

# Constantes: UPPER_CASE
API_BASE_URL = "https://api.riotgames.com"

# Private: prefix avec _
def _internal_helper():
    pass
```

#### Imports

```python
# 1. Standard library
import os
import sys
from datetime import datetime

# 2. Third-party
import pandas as pd
import requests

# 3. Local application
from src.api.riot_api import RiotAPIClient
from src.database.models import Player
```

#### Type hints

```python
# Toujours utiliser les type hints
def get_player_stats(player_id: int) -> dict[str, float]:
    """
    Get player statistics
    
    Args:
        player_id: ID of the player
        
    Returns:
        Dictionary with player stats
    """
    return {"kda": 3.5, "cs_per_min": 8.2}
```

#### Docstrings

```python
def complex_function(param1: str, param2: int) -> list[dict]:
    """
    Short description (one line)
    
    Longer description if needed. Explain what the function does,
    any important details, edge cases, etc.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param2 is negative
        
    Example:
        >>> complex_function("test", 5)
        [{"key": "value"}]
    """
    pass
```

---

## Process de développement

### 1. Créer une branche

```bash
# Format: type/short-description
git checkout -b feature/add-champion-stats
git checkout -b fix/rate-limit-bug
git checkout -b docs/update-api-guide
```

**Types de branches**:
- `feature/` : Nouvelle fonctionnalité
- `fix/` : Correction de bug
- `docs/` : Documentation
- `refactor/` : Refactoring
- `test/` : Ajout de tests
- `perf/` : Optimisation

### 2. Développer

```bash
# Activer l'environnement virtuel
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Installer les dépendances
pip install -r requirements.txt

# Faire vos modifications
# ...

# Tester localement
pytest tests/
```

### 3. Committer

#### Format des commits

```
type(scope): short description

Optional longer description

Fixes #123
```

**Types**:
- `feat`: Nouvelle fonctionnalité
- `fix`: Correction de bug
- `docs`: Documentation
- `style`: Formatage (pas de changement de code)
- `refactor`: Refactoring
- `test`: Ajout de tests
- `chore`: Maintenance

**Exemples**:
```bash
git commit -m "feat(api): add rate limiting to Riot API client"
git commit -m "fix(parser): handle empty OP.GG URLs correctly"
git commit -m "docs(readme): update installation instructions"
```

### 4. Push et Pull Request

```bash
# Push vers votre fork
git push origin feature/add-champion-stats

# Créer une Pull Request sur GitHub
# Template automatique fourni
```

#### Checklist PR

- [ ] Code formaté avec Black
- [ ] Type hints ajoutés
- [ ] Docstrings complètes
- [ ] Tests ajoutés/mis à jour
- [ ] Documentation mise à jour
- [ ] Pas de breaking changes (ou documentés)
- [ ] Tests passent (`pytest`)

---

## Tests

### Structure

```
tests/
├── unit/              # Tests unitaires
├── integration/       # Tests d'intégration
└── e2e/              # Tests end-to-end
```

### Écrire des tests

```python
# tests/unit/test_parsers.py
import pytest
from src.parsers.opgg_parser import OPGGParser

def test_extract_riot_ids_valid_url():
    """Test extraction from valid OP.GG URL"""
    parser = OPGGParser()
    url = "https://www.op.gg/multisearch/euw?summoners=Player1,Player2"
    
    result = parser.extract_riot_ids_from_url(url)
    
    assert len(result) == 2
    assert result[0]['game_name'] == 'Player1'
    assert result[0]['tag_line'] == 'EUW'

def test_extract_riot_ids_invalid_url():
    """Test handling of invalid URL"""
    parser = OPGGParser()
    
    with pytest.raises(ValueError):
        parser.extract_riot_ids_from_url("not-a-valid-url")
```

### Lancer les tests

```bash
# Tous les tests
pytest

# Tests spécifiques
pytest tests/unit/test_parsers.py

# Avec coverage
pytest --cov=src tests/

# Verbose
pytest -v
```

### Mocking

```python
from unittest.mock import Mock, patch

@patch('src.api.riot_api.requests.get')
def test_riot_api_call(mock_get):
    """Test Riot API call with mocked response"""
    mock_response = Mock()
    mock_response.json.return_value = {'puuid': 'test123'}
    mock_response.status_code = 200
    mock_get.return_value = mock_response
    
    client = RiotAPIClient()
    result = client.get_account_by_riot_id("Test", "EUW")
    
    assert result['puuid'] == 'test123'
```

---

## Documentation

### Où documenter ?

1. **Code**: Docstrings Python
2. **README.md**: Guide utilisateur
3. **docs/**: Documentation technique détaillée
4. **Comments**: Expliquer le "pourquoi", pas le "quoi"

### Exemple de documentation

```python
def calculate_kda(kills: int, deaths: int, assists: int) -> float:
    """
    Calculate KDA (Kill/Death/Assist ratio)
    
    The KDA is calculated as (kills + assists) / deaths.
    If deaths is 0, returns kills + assists (perfect KDA).
    
    Args:
        kills: Number of kills
        deaths: Number of deaths
        assists: Number of assists
        
    Returns:
        KDA ratio as a float
        
    Example:
        >>> calculate_kda(5, 2, 10)
        7.5
        >>> calculate_kda(10, 0, 5)
        15.0
    """
    if deaths == 0:
        return float(kills + assists)
    return (kills + assists) / deaths
```

---

## Outils de développement

### Pre-commit hooks (recommandé)

```bash
# Installer pre-commit
pip install pre-commit

# Configurer (.pre-commit-config.yaml)
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8

# Installer les hooks
pre-commit install
```

### IDE recommandé

**VS Code** avec extensions :
- Python
- Pylance
- Black Formatter
- autoDocstring
- GitLens

### Configuration VS Code

```json
// .vscode/settings.json
{
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true
}
```

---

## Review Process

### Ce que nous regardons

1. **Fonctionnalité**
   - Le code fait ce qu'il est censé faire
   - Pas de régression
   - Edge cases gérés

2. **Qualité du code**
   - Lisibilité
   - Maintenabilité
   - Performance raisonnable

3. **Tests**
   - Coverage adéquat
   - Tests pertinents

4. **Documentation**
   - Docstrings complètes
   - Changements documentés

### Timeline

- **Première review** : 1-3 jours
- **Reviews suivantes** : 1-2 jours
- **Merge** : après approbation + CI vert

---

## Communication

### Où échanger ?

- **Issues GitHub** : Bugs, features, questions
- **Pull Requests** : Discussions sur le code
- **Discussions** : Questions générales

### Conseils

- Soyez précis dans vos descriptions
- Ajoutez des exemples si possible
- Mentionnez les issues liées
- Soyez patient et respectueux

---

## Reconnaissance

Tous les contributeurs seront :
- Mentionnés dans les release notes
- Ajoutés au fichier CONTRIBUTORS.md
- Remerciés dans la communauté OcciLan

---

## Questions ?

N'hésitez pas à :
- Ouvrir une issue
- Contacter [@Alexandre-Machu](https://github.com/Alexandre-Machu)

---

**Merci de contribuer à OcciLan Stats ! 🚀**
