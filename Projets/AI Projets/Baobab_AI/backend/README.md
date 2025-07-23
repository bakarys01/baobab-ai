# Backend – FastAPI RAG Chatbot

## Prérequis
- Python 3.10+
- [Poetry](https://python-poetry.org/) ou `pip`

## Installation

1. Cloner le repo et se placer dans le dossier `backend` :
   ```bash
   cd backend
   ```
2. Copier le fichier `.env.example` en `.env` et renseigner votre clé OpenAI :
   ```bash
   copy .env.example .env  # Windows
   # ou
   cp .env.example .env    # Linux/Mac
   ```
3. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   # ou avec poetry
   poetry install
   ```

## Lancement du serveur

```bash
uvicorn main:app --reload
```

L’API sera disponible sur http://localhost:8000

## Endpoint principal
- `POST /rag` : reçoit `{ "question": "..." }` et retourne `{ "answer": "..." }`
