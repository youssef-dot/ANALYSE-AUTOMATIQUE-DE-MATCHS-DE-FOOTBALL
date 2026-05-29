# Guide des captures d’écran

Faites ces captures **après avoir relancé** l’API et le frontend (ou une analyse terminée).

## Préparation

```powershell
# Terminal 1
cd "c:\Users\youssef\OneDrive\Bureau\cv project"
.venv\Scripts\activate
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2
cd frontend
npm run dev
```

Ouvrir : http://localhost:5173

---

## Liste des captures (obligatoires)

### Capture 1 — Page d’accueil web
- **Fichier** : `captures/01_accueil_web.png`
- **Comment** : Page complète avec le titre « Analyse Football » et le badge « API prête » (vert).
- **Slide** : Introduction / Contexte

### Capture 2 — Zone d’upload
- **Fichier** : `captures/02_upload.png`
- **Comment** : Zone « Glissez une vidéo ici » + nom du fichier sélectionné visible.
- **Slide** : Interface utilisateur

### Capture 3 — Analyse en cours
- **Fichier** : `captures/03_analyse_en_cours.png`
- **Comment** : Barre de progression entre 20 % et 80 %, message du type « Détection et suivi (YOLO)… ».
- **Slide** : Fonctionnement temps réel

### Capture 4 — Résultat terminé
- **Fichier** : `captures/04_resultat_video.png`
- **Comment** : Barre à 100 %, lecteur vidéo avec annotations visibles, lien « Télécharger ».
- **Slide** : Résultat / Démo

### Capture 5 — Vidéo brute (avant)
- **Fichier** : `captures/05_video_avant.png`
- **Comment** : Une frame de la vidéo **sans** annotations (lecteur VLC ou première image extraite).
- **Slide** : Avant / Après

### Capture 6 — Vidéo annotée (après)
- **Fichier** : `captures/06_video_apres_annotee.png`
- **Comment** : Même moment du match si possible : ellipses joueurs, ID, vitesse km/h, distance m, triangle possession, % équipes.
- **Slide** : Avant / Après + Fonctionnalités

### Capture 7 — Structure du projet
- **Fichier** : `captures/07_structure_projet.png`
- **Comment** : Arborescence dans Cursor/VS Code : `trackers`, `api`, `frontend`, `pipeline`, `models`.
- **Slide** : Architecture technique

### Capture 8 — Terminal YOLO
- **Fichier** : `captures/09_yolo_terminal.png`
- **Comment** : Logs du type `20 players, 1 referee`, `Speed: … inference`.
- **Slide** : Détection & suivi

---

## Captures recommandées (bonus)

### Capture 9 — Documentation API
- **URL** : http://127.0.0.1:8000/docs
- **Fichier** : `captures/10_api_docs.png`
- **Slide** : Backend FastAPI

### Capture 10 — Code pipeline
- **Fichier** : `captures/11_code_pipeline.png`
- **Comment** : Fichier `pipeline/analysis.py` (fonction `run_analysis`).
- **Slide** : Implémentation

### Capture 11 — View transformer
- **Fichier** : `captures/12_view_transformer.png`
- **Comment** : `view_transformer.py` avec `pixel_vertices` (calibrage terrain).
- **Slide** : Métriques vitesse/distance

### Capture 12 — Comparaison côte à côte
- **Fichier** : `captures/13_avant_apres_montage.png`
- **Comment** : Montage PowerPoint/Canva : gauche = avant, droite = après.
- **Slide** : Impact visuel

---

## Astuces qualité

1. **Plein écran** navigateur (F11) pour les captures web.
2. **Masquer** onglets inutiles et barre des tâches si possible.
3. Vidéo annotée : mettre en **pause** sur une action claire (course, passe).
4. Utiliser le script `extract_frames.py` pour avoir plusieurs frames nettes.
5. Format PNG (meilleure qualité que JPG pour les slides).

---

## Où trouver la vidéo annotée

Après une analyse web réussie :

```
web_jobs/<job_id>/output_annotated.mp4
```

Exemple de job vu dans vos logs : `56476262-150b-4cda-bbe0-da073eddcd4e`
