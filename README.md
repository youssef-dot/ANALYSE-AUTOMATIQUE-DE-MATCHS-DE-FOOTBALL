# Analyse vidéo de football

Système d'analyse automatique de matchs de football à partir d'une vidéo.

## Fonctionnalités

| Module | Rôle |
|--------|------|
| `trackers/` | Détection YOLO + suivi ByteTrack (joueurs, arbitres, ballon) |
| `team_assigner/` | Assignation d'équipe par couleur (K-Means) |
| `player_ball_assigner/` | Possession du ballon (joueur le plus proche) |
| `camera_movement_estimator/` | Compensation du mouvement de caméra (flux optique) |
| `view_transformer/` | Coordonnées terrain (vue de dessus, en mètres) |
| `speed_and_distance_estimator/` | Vitesse (km/h) et distance parcourue (m) |
| `main.py` | Pipeline en ligne de commande |
| `pipeline/` | Logique d'analyse réutilisable (CLI + API) |
| `api/` | Backend FastAPI (upload, jobs, résultat) |
| `frontend/` | Interface React (upload + progression) |

## Résultat

Vidéo annotée : `output_videos/output_video.mp4` (CLI) ou téléchargement via l'interface web

- Boîtes / ellipses autour des joueurs et arbitres
- Numéros de suivi (ID)
- Triangle sur le joueur en possession
- Pourcentage de possession par équipe
- Mouvement caméra (X / Y)
- Vitesse et distance par joueur

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Prérequis fichiers

1. **Vidéo** : placer une vidéo dans `input_videos/` (ex. `08fd33_4.mp4`)
2. **Modèle YOLO** : placer `best.pt` dans `models/`  
   Entraîné pour les classes : `player`, `goalkeeper`, `referee`, `ball`  
   (projet Roboflow « football players detection » ou équivalent)

Créer les dossiers si besoin :

```bash
mkdir input_videos models output_videos stubs
```

## Lancer l'analyse

```bash
python main.py
```

La première exécution est longue (détection + suivi sur toutes les images). Les résultats intermédiaires sont mis en cache dans `stubs/` :

- `stubs/track_stubs.pkl` — pistes détectées
- `stubs/camera_movement_stub.pkl` — mouvement caméra

Pour recalculer, supprimez les fichiers `.pkl` correspondants.

## Interface web (FastAPI + React)

### 1. Installer les dépendances Python

```bash
pip install -r requirements.txt
```

### 2. Démarrer l'API (terminal 1)

Depuis la racine du projet :

```bash
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Démarrer le frontend (terminal 2)

```bash
cd frontend
npm install
npm run dev
```

Ouvrir **http://localhost:5173** — glisser une vidéo, cliquer sur « Lancer l'analyse », suivre la barre de progression, puis lire ou télécharger le résultat.

### Production (un seul serveur)

```bash
cd frontend && npm install && npm run build
cd ..
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

L'API sert alors le build React sur **http://localhost:8000**.

Les fichiers uploadés et les jobs sont stockés dans `web_jobs/` (un dossier par analyse).

## Adapter à une autre vidéo

1. Changer le chemin dans `main.py` : `read_video('input_videos/VOTRE_VIDEO.mp4')`
2. Recalibrer les 4 coins du terrain dans `view_transformer/view_transformer.py` (`pixel_vertices`) pour votre plan de caméra
3. Ajuster le masque caméra dans `camera_movement_estimator/camera_movement_estimator.py` si la résolution change

## Structure du pipeline

```
Vidéo → Détection/Suivi → Interpolation ballon → Positions pixels
     → Compensation caméra → Coordonnées terrain → Vitesse/Distance
     → Équipes → Possession → Rendu → output_video.mp4
```
