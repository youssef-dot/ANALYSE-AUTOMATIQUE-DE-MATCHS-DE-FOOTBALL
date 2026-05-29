import os
from typing import Callable, Optional

import numpy as np

from utlis import read_video, save_video
from trackers.tracker import Tracker
from team_assigner import TeamAssigner
from player_ball_assigner import PlayerBallAssigner
from camera_movement_estimator import CameraMovementEstimator
from view_transformer import ViewTransformer
from speed_and_distance_estimator import SpeedAndDistance_Estimator

ProgressCallback = Optional[Callable[[int, str], None]]

STEPS = [
    (5, "Lecture de la vidéo…"),
    (40, "Détection et suivi (YOLO)…"),
    (55, "Compensation mouvement caméra…"),
    (70, "Vitesse et distance…"),
    (85, "Assignation des équipes…"),
    (95, "Rendu de la vidéo annotée…"),
    (100, "Terminé"),
]


def _report(progress_cb: ProgressCallback, step_index: int) -> None:
    if progress_cb is None:
        return
    pct, message = STEPS[step_index]
    progress_cb(pct, message)


def run_analysis(
    video_path: str,
    output_path: str,
    *,
    model_path: str = "models/best.pt",
    work_dir: Optional[str] = None,
    frame_rate: float = 20.0,
    use_stubs: bool = True,
    progress_cb: ProgressCallback = None,
) -> str:
    """
    Run the full football analysis pipeline.

    Args:
        video_path: Path to input video file.
        output_path: Path for annotated output video (.mp4 recommended for web).
        model_path: YOLO weights path.
        work_dir: Directory for per-job stub cache (created if missing).
        frame_rate: FPS used for speed/distance calculations.
        use_stubs: Reuse/write stub pickles under work_dir when True.
        progress_cb: Optional callback(percent, message).

    Returns:
        output_path on success.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Vidéo introuvable : {video_path}")
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Modèle introuvable : {model_path}\n"
            "Placez best.pt dans le dossier models/"
        )

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    if work_dir:
        os.makedirs(work_dir, exist_ok=True)

    track_stub = None
    camera_stub = None
    if use_stubs and work_dir:
        track_stub = os.path.join(work_dir, "track_stubs.pkl")
        camera_stub = os.path.join(work_dir, "camera_movement_stub.pkl")

    _report(progress_cb, 0)
    video_frames = read_video(video_path)
    if not video_frames:
        raise ValueError("La vidéo ne contient aucune image.")

    _report(progress_cb, 1)
    tracker = Tracker(model_path)
    tracks = tracker.get_object_tracks(
        video_frames,
        read_from_stub=use_stubs,
        stub_path=track_stub,
    )

    tracks["ball"] = tracker.interpolate_ball_positions(tracks["ball"])
    tracker.add_position_to_tracks(tracks)

    _report(progress_cb, 2)
    camera_movement_estimator = CameraMovementEstimator(video_frames[0])
    camera_movement_per_frame = camera_movement_estimator.get_camera_movement(
        video_frames,
        read_from_stub=use_stubs,
        stub_path=camera_stub,
    )
    camera_movement_estimator.add_adjust_positions_to_tracks(
        tracks, camera_movement_per_frame
    )

    view_transformer = ViewTransformer()
    view_transformer.add_transformed_position_to_tracks(tracks)

    _report(progress_cb, 3)
    speed_and_distance_estimator = SpeedAndDistance_Estimator(frame_rate=frame_rate)
    speed_and_distance_estimator.add_speed_and_distance_to_tracks(tracks)

    _report(progress_cb, 4)
    team_assigner = TeamAssigner()
    team_assigner.assign_team_color(video_frames[0], tracks["players"][0])

    for frame_num, player_track in enumerate(tracks["players"]):
        for player_id, track in player_track.items():
            team = team_assigner.get_player_team(
                video_frames[frame_num], track["bbox"], player_id
            )
            tracks["players"][frame_num][player_id]["team"] = team
            tracks["players"][frame_num][player_id]["team_color"] = (
                team_assigner.team_colors[team]
            )

    player_assigner = PlayerBallAssigner()
    team_ball_control = []
    for frame_num, player_track in enumerate(tracks["players"]):
        ball_bbox = tracks["ball"][frame_num][1]["bbox"]
        assigned_player = player_assigner.assign_ball_to_player(
            player_track, ball_bbox
        )

        if assigned_player != -1:
            tracks["players"][frame_num][assigned_player]["has_ball"] = True
            team_ball_control.append(
                tracks["players"][frame_num][assigned_player]["team"]
            )
        elif team_ball_control:
            team_ball_control.append(team_ball_control[-1])
        else:
            team_ball_control.append(1)
    team_ball_control = np.array(team_ball_control)

    _report(progress_cb, 5)
    output_video_frames = tracker.draw_annotations(
        video_frames, tracks, team_ball_control
    )
    output_video_frames = camera_movement_estimator.draw_camera_movement(
        output_video_frames, camera_movement_per_frame
    )
    output_video_frames = speed_and_distance_estimator.draw_speed_and_distance(
        output_video_frames, tracks
    )

    save_video(output_video_frames, output_path)
    _report(progress_cb, 6)
    return output_path
