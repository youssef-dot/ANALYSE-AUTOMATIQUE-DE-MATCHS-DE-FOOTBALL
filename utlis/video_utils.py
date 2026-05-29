import cv2
import math

def read_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frames = []
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    
    cap.release()
    return frames

def save_video(output_video_frames, output_video_path):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, 20.0, (output_video_frames[0].shape[1], output_video_frames[0].shape[0]))

    for frame in output_video_frames:
        out.write(frame)

    out.release()

def measure_distance(point1, point2):
    """Calculate Euclidean distance between two points"""
    return math.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)

def measure_xy_distance(point1, point2):
    """Calculate X and Y distance between two points"""
    return point2[0]-point1[0], point2[1]-point1[1]