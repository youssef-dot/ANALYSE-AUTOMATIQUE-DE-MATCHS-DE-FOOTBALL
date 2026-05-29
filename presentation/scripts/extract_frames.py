"""
Extrait des images PNG depuis une vidéo (résultat annoté ou brute).
Usage:
  python presentation/scripts/extract_frames.py --video path/to/video.mp4
  python presentation/scripts/extract_frames.py --video path/to/video.mp4 --frames 0,120,240
"""

import argparse
import os
import sys

import cv2

# Permet d'exécuter depuis la racine du projet
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def extract(video_path: str, out_dir: str, frame_indices: list[int]) -> None:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Impossible d'ouvrir : {video_path}")

    os.makedirs(out_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(video_path))[0]

    for idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, frame = cap.read()
        if not ok:
            print(f"Frame {idx} ignorée (hors vidéo).")
            continue
        out_path = os.path.join(out_dir, f"{base}_frame_{idx:05d}.png")
        cv2.imwrite(out_path, frame)
        print(f"Enregistré : {out_path}")

    cap.release()


def main():
    parser = argparse.ArgumentParser(description="Extraire des frames PNG d'une vidéo")
    parser.add_argument("--video", required=True, help="Chemin vers le fichier vidéo")
    parser.add_argument(
        "--out",
        default=os.path.join(ROOT, "presentation", "captures"),
        help="Dossier de sortie (défaut: presentation/captures)",
    )
    parser.add_argument(
        "--frames",
        default="0,60,120,180,240",
        help="Indices de frames séparés par des virgules (ex: 0,100,200)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=0,
        help="Si > 0, extrait N frames réparties uniformément sur toute la vidéo",
    )
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.video)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    if args.count > 0 and total > 0:
        step = max(1, total // (args.count + 1))
        indices = [i * step for i in range(1, args.count + 1)]
    else:
        indices = [int(x.strip()) for x in args.frames.split(",") if x.strip()]

    print(f"Vidéo : {args.video} ({total} frames)")
    extract(args.video, args.out, indices)


if __name__ == "__main__":
    main()
