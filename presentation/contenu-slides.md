# Présentation — Analyse automatique de matchs de football

> Copiez chaque section dans une slide PowerPoint / Google Slides.  
> Insérez l’image indiquée depuis le dossier `captures/`.

---

## Slide 1 — Titre

**Titre :** Analyse vidéo de football par Computer Vision

**Sous-titre :** Détection, suivi, équipes, possession, vitesse et distance

**Votre nom · Date · Formation**

*Image : optionnelle (logo football ou capture 01)*

**Notes orateur (30 s)**  
« Ce projet analyse automatiquement une vidéo de match : il détecte joueurs et ballon, suit leurs déplacements, estime la vitesse en km/h et la distance en mètres, et produit une vidéo annotée accessible via une interface web. »

---

## Slide 2 — Problématique

**Titre :** Pourquoi ce projet ?

**Contenu :**
- Analyser un match manuellement = long et subjectif
- Besoin de métriques objectives : vitesse, distance, possession
- La vidéo TV a une caméra mobile → distorsion et mouvement
- Objectif : pipeline automatique **vidéo → insights visuels**

*Image : `05_video_avant.png` (match brut)*

**Notes orateur (45 s)**  
Expliquer le contexte sport/analytics. Insister sur le fait qu’on part d’une simple vidéo MP4.

---

## Slide 3 — Solution proposée

**Titre :** Notre solution

**Contenu :**
- Upload d’une vidéo via interface web
- Traitement IA en arrière-plan (YOLO + suivi)
- Vidéo annotée téléchargeable
- Métriques par joueur affichées en direct sur l’image

*Image : `04_resultat_video.png` ou `06_video_apres_annotee.png`*

**Notes orateur (45 s)**  
Montrer le résultat tôt pour accrocher l’audience.

---

## Slide 4 — Fonctionnalités

**Titre :** Ce que le système produit

| Fonctionnalité | Détail |
|----------------|--------|
| Détection | Joueurs, gardiens, arbitres, ballon |
| Suivi | ID stable frame à frame (ByteTrack) |
| Équipes | Couleur du maillot (K-Means) |
| Possession | Joueur le plus proche du ballon |
| Caméra | Compensation du mouvement (flux optique) |
| Métriques | Vitesse (km/h), distance (m) |
| Rendu | % possession, triangle sur le porteur |

*Image : `06_video_apres_annotee.png` (zoom sur annotations)*

---

## Slide 5 — Interface web

**Titre :** Interface utilisateur (React)

**Contenu :**
- Upload par glisser-déposer
- Barre de progression en temps réel
- Lecture et téléchargement du résultat
- Stack : **React + Vite** (frontend), **FastAPI** (backend)

*Images : `01_accueil_web.png` + `03_analyse_en_cours.png`*

**Notes orateur (1 min)**  
Démo live possible : upload court clip → montrer la progression.

---

## Slide 6 — Architecture globale

**Titre :** Architecture du système

```
[Navigateur React]  →  [API FastAPI]  →  [Pipeline Python]
                              ↓
                    YOLO · ByteTrack · OpenCV
                              ↓
                    Vidéo annotée (MP4)
```

**Modules principaux :**
- `trackers/` — détection & suivi
- `pipeline/` — orchestration
- `api/` — jobs & upload
- `frontend/` — interface

*Image : `07_structure_projet.png`*

---

## Slide 7 — Pipeline de traitement

**Titre :** Pipeline vidéo → résultat

1. Lecture vidéo  
2. Détection YOLO + suivi ByteTrack  
3. Interpolation trajectoire du ballon  
4. Compensation mouvement caméra  
5. Transformation perspective → coordonnées terrain (m)  
6. Calcul vitesse & distance  
7. Assignation équipes & possession  
8. Rendu annotations → MP4  

*Image : schéma (diagramme ci-dessous dans PowerPoint) ou `11_code_pipeline.png`*

**Diagramme à recréer dans PowerPoint :**

```
Vidéo → Détection/Suivi → Ballon → Caméra → Terrain (m)
     → Vitesse/Distance → Équipes → Possession → Export MP4
```

---

## Slide 8 — Détection & suivi (YOLO)

**Titre :** Cœur IA : YOLO + ByteTrack

**Contenu :**
- Modèle custom `best.pt` (classes : player, goalkeeper, referee, ball)
- Ultralytics YOLO pour la détection frame par frame
- ByteTrack pour lier les détections dans le temps (ID joueur)
- Cache `.pkl` pour ne pas tout recalculer

*Image : `09_yolo_terminal.png`*

**Notes orateur**  
« Environ 794 ms par image sur notre machine — la première analyse est la plus longue. »

---

## Slide 9 — Vitesse et distance

**Titre :** Métriques en mètres réels

**Contenu :**
- `ViewTransformer` : 4 coins du terrain → vue de dessus
- Positions en **mètres** sur le terrain
- **Vitesse** : km/h (fenêtre de 5 images)
- **Distance** : mètres parcourus **cumulés** par joueur

*Image : `06_video_apres_annotee.png` (texte 12.5 km/h et 45.2 m visible)*

**Phrase clé :**  
« Le “m” affiché = distance totale courue, pas la distance au but. »

---

## Slide 10 — Backend API

**Titre :** API REST (FastAPI)

| Endpoint | Rôle |
|----------|------|
| `POST /api/jobs` | Upload + lance l’analyse |
| `GET /api/jobs/{id}` | Statut & progression |
| `GET /api/jobs/{id}/result` | Télécharge la vidéo |

- Un job = un dossier dans `web_jobs/`
- Traitement en thread (non bloquant)

*Image : `10_api_docs.png`*

---

## Slide 11 — Avant / Après

**Titre :** Résultat visuel

| Avant | Après |
|-------|-------|
| Vidéo brute | Ellipses, IDs, équipes, stats |

*Image : `13_avant_apres_montage.png` ou deux images `05` + `06`*

---

## Slide 12 — Technologies

**Titre :** Stack technique

| Couche | Technologies |
|--------|----------------|
| IA | PyTorch, Ultralytics YOLO, supervision |
| Vision | OpenCV |
| ML classique | scikit-learn (K-Means équipes) |
| Backend | FastAPI, Uvicorn |
| Frontend | React, Vite |
| Données | NumPy, Pandas |

---

## Slide 13 — Limites & améliorations

**Titre :** Limites actuelles & perspectives

**Limites :**
- Calibrage terrain manuel (`pixel_vertices`) par vidéo/caméra
- Temps de traitement élevé sans GPU
- Vidéo entière chargée en RAM

**Améliorations possibles :**
- UI pour cliquer les 4 coins du terrain
- GPU / traitement par chunks
- Tableau de bord stats (heatmap, sprint count)
- Export CSV des métriques

---

## Slide 14 — Conclusion

**Titre :** Conclusion

**Résumé :**
- Pipeline CV complet football : détection → métriques → rendu
- Interface web pour upload et résultat
- Projet modulaire et extensible

**Merci — Questions ?**

*Image : `04_resultat_video.png`*

---

## Slide bonus — Démo live (optionnel)

1. Ouvrir http://localhost:5173  
2. Uploader un extrait court (30 s)  
3. Montrer la barre de progression  
4. Lire la vidéo annotée  

*Préparer une petite vidéo à l’avance au cas où le réseau ou le CPU soit lent.*
