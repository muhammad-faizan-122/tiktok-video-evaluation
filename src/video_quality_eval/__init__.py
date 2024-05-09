from constants.scraper.constants import DOWNLOADED_VIDS_DIR
from constants.video_quality_eval.constants import OUT_PATH
from src.video_quality_eval.traditional.video_quality_eval import (
    laplacian_video_quality,
    structural_similarity_video_quality,
    psnr_video_quality,
)
from src.video_quality_eval.deep_learning.simpleVQA.infer import simple_vqa_infer
import os
import json


def save_json(data, file_path):
    """
    Save data to a JSON file.

    Args:
        data: Data to be saved (dictionary or list).
        file_path (str): Path to the JSON file.
    """
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)


def assess_videos_quality():
    videos_qualities_metadata = []
    videos = os.listdir(DOWNLOADED_VIDS_DIR)
    for video_id, video in enumerate(videos):

        if not video.endswith(".mp4"):
            continue

        print(f"Evaluating video-{video_id+1}...")

        video_path = os.path.join(DOWNLOADED_VIDS_DIR, video)

        lap_score, lap_res = laplacian_video_quality(video_path)
        ss_score, ss_res = structural_similarity_video_quality(video_path)
        psnr_score, psnr_res = psnr_video_quality(video_path)

        video_quality = {
            video: {
                "laplacian": {
                    "quality_score": lap_score,
                    "quality": lap_res,
                },
                "structural_similarty": {
                    "quality_score": ss_score,
                    "quality": ss_res,
                },
                "peak_signal_to_noise_ratio": {
                    "quality_score": psnr_score,
                    "quality": psnr_res,
                },
            }
        }

        videos_qualities_metadata.append(video_quality)

    save_json(videos_qualities_metadata, OUT_PATH)
