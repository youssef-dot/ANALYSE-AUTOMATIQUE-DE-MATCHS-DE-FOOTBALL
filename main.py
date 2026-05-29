import os

from pipeline.analysis import run_analysis


def main():
    os.makedirs("input_videos", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    os.makedirs("output_videos", exist_ok=True)
    os.makedirs("stubs", exist_ok=True)

    video_path = "input_videos/08fd33_4.mp4"
    model_path = "models/best.pt"
    output_path = "output_videos/output_video.mp4"

    run_analysis(
        video_path,
        output_path,
        model_path=model_path,
        work_dir="stubs",
        use_stubs=True,
    )
    print(f"Vidéo enregistrée : {output_path}")


if __name__ == "__main__":
    main()
