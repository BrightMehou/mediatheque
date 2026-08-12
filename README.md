# Wiki

🚧 Projet en construction

Ce projet est actuellement en cours de développement.
De nouvelles fonctionnalités, améliorations et mises à jour arriveront prochainement.

Merci de votre patience !
## Structure du projet

```
├── .github/workflows/     # CI : tests Python et build Docker
├── src/
│   ├── api/               # FastAPI, persistance SQLite
│   ├── db/                # Utilitaire db
│   └── ui/                # Streamlit (accueil + pages)
├── tests/                 # Tests API, base de données et UI
├── docker-compose.yaml
├── Dockerfile
└── pyproject.toml         # Dépendances (uv) et configuration Ruff
```

## 🚀 **Installation et Exécution**


1. **Construire les images Docker et lancer les containeurs :**  
   ```bash
   docker-compose up -d
   ```
   
| Service | URL |
|---------|-----|
| API (Swagger) | http://localhost:8000/docs |
| Interface Streamlit | http://localhost:8501 |

### Qualité de code (développeurs)

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

## Licence

Voir le fichier [LICENSE](LICENSE).