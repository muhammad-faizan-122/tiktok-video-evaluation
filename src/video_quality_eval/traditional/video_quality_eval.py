from skimage.metrics import structural_similarity as ssim
import cv2
import numpy as np


def laplacian_video_quality(video_path):
    """
    Assess the video quality based on the Laplacian variance of video frames.

    This function calculates the Laplacian variance for each frame in a video file to determine
    the overall sharpness or blurriness of the video. A higher average Laplacian variance
    suggests a clearer video, while a lower value indicates a blurrier video.

    Args:
        video_path (str): Path to the video file.

    Returns:
        float: The average Laplacian variance of the frames in the video.
        str: A quality assessment of 'Clear' if the average Laplacian variance is above 100, otherwise 'Blur'.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Error opening video file")

    laplacian_values = []

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray_frame, cv2.CV_64F).var()
            laplacian_values.append(laplacian_var)

    finally:
        cap.release()

    if not laplacian_values:
        raise ValueError("No frames to analyze")

    avg_laplacian = np.mean(laplacian_values)
    quality = "Clear" if avg_laplacian > 100 else "Blur"

    return avg_laplacian, quality


def structural_similarity_video_quality(video_path, threshold=0.75):
    """Evaluate video quality using SSIM. Videos with higher SSIM are considered clearer.

    Args:
        video_path (str): Path to the video file.
        threshold (float): Threshold for determining if the video is clear or blurred.

    Returns:
        Tuple of average SSIM and video quality classification.
    """
    ssim_values = []
    cap = cv2.VideoCapture(video_path)
    ret, prev_frame = cap.read()
    prev_frame = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY) if ret else None

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ssim_score = ssim(prev_frame, gray_frame)
        ssim_values.append(ssim_score)
        prev_frame = gray_frame

    cap.release()

    avg_ssim = np.mean(ssim_values)
    quality = "Clear" if avg_ssim > threshold else "Blur"
    return avg_ssim, quality


def psnr_video_quality(video_path, threshold=30):
    """Evaluate video quality using PSNR. Higher PSNR values indicate better quality.

    Args:
        video_path (str): Path to the video file.
        threshold (float): Threshold for determining if the video is clear or blurred.

    Returns:
        Tuple of average PSNR and video quality classification.
    """
    psnr_values = []
    cap = cv2.VideoCapture(video_path)
    ret, prev_frame = cap.read()
    prev_frame = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY) if ret else None

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mse = np.mean((prev_frame - gray_frame) ** 2)
        if mse == 0:
            psnr = float(
                "inf"
            )  # PSNR is infinity if there is no noise (identical frames)
        else:
            psnr = 20 * np.log10(255.0 / np.sqrt(mse))
        psnr_values.append(psnr)
        prev_frame = gray_frame

    cap.release()

    avg_psnr = np.mean(psnr_values)
    quality = "Clear" if avg_psnr > threshold else "Blur"
    return avg_psnr, quality
