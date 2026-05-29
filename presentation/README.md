# Présentation du projet — Analyse Football CV

Ce dossier contient tout pour préparer une soutenance ou un rapport avec **captures d’écran**.

## Fichiers

| Fichier | Usage |
|---------|--------|
| `contenu-slides.md` | Texte de chaque slide (à copier dans PowerPoint / Google Slides / Canva) |
| `guide-captures.md` | Liste précise des captures à faire |
| `scripts/extract_frames.py` | Extrait des images depuis une vidéo annotée (.mp4) |

## Étapes rapides

### 1. Créer le dossier des captures

```powershell
mkdir presentation\captures
```

### 2. Faire les captures (voir `guide-captures.md`)

Raccourci Windows : **Win + Shift + S**

### 3. Extraire des frames de la vidéo résultat (optionnel)

```powershell
cd "c:\Users\youssef\OneDrive\Bureau\cv project"
.venv\Scripts\activate
python presentation/scripts/extract_frames.py --video "web_jobs\VOTRE_JOB\output_annotated.mp4" --out presentation\captures
```

### 4. Monter les slides

Ouvrir `contenu-slides.md`, créer ~12 slides dans PowerPoint, insérer les images depuis `presentation/captures/`.

## Durée conseillée

- Présentation orale : **8 à 12 minutes**
- Slides : **10 à 14** (+ démo live optionnelle)

## Nommage des images

Utilisez ces noms pour retrouver facilement chaque capture :

```
01_accueil_web.png
02_upload.png
03_analyse_en_cours.png
04_resultat_video.png
05_video_avant.png
06_video_apres_annotee.png
07_structure_projet.png
08_pipeline.png
09_yolo_terminal.png
10_api_docs.png
```
