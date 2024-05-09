# Tiktok Videos Quality evaluation
An automated process has been implemented for downloading videos from TikTok and assessing each video's quality in terms of clarity or blurriness.

## Working

Pipeline can be divided into parts
- Scraping and dowloading tiktok videos
- Quality evaluation of each downloaded video

![alt text](diagram/block_diagram.drawio.png)

### Scraping and dowloading tiktok videos
I have utilized the selenium and beautiful soap libraries of Python to automate scraping and downloading TikTok videos. A Captcha appears at the start of scraping, which need to solve manually within 30 seconds.

### Quality evaluation of each downloaded video
Use of traditional and deep learning algorithm to check the quality of each downloaded.

**Traditional Algorithms:**

- **Laplacian of Gaussian**: Highlights sharp edges and rapid intensity changes in an image. Sharp, well-defined edges typically indicate clarity, while their absence may suggest blurriness.

- **Structural Similarity Index (SSIM)**: Measures the similarity of two images based on luminance, contrast, and structure. Higher SSIM values (closer to 1) generally indicate clear, high-quality videos, while lower values suggest poor quality and potential blurriness.

- **Peak Signal to Noise Ratio (PSNR)**: Compares the maximum possible power of the original signal to the power of corrupting noise. Higher PSNR values indicate a clearer video with fewer distortions, whereas lower values are indicative of poor quality.

**Deep learning Algorithm:**

- **SimpleVQA**: SimpleVQA leverages deep learning techniques to predict the perceived quality of videos based on visual artifacts and other quality factors intrinsic to the video itself. The primary strength of this model lies in its ability to function without reference videos, using instead a set of learned features that correlate with human judgments of video quality.

## Directory
- **src**: Contains two modules: scraping and video quality quality.
- **video**: Contains the tiktok downloaded videos.
- **constants**: Contains constants involving scraping and video quality quality module.
- **output**: Contains generated output JSON file.


## Usage
### Virtal Environment and install Requirements:

- Create a virtual environment with python version **3.8.8**. To create conda environment use following command.
    ```
    conda create -n env_name python=3.8.8 -y
    ```
- Install the requirements using the following command
    
    ```
    pip install -r requirements.txt
    ```
- Download the SimpleVQA pre-trained model using following command.
    ```
    gdown -O src/video_quality_eval/deep_learning/simpleVQA/ckpts/UGC_BVQA_model.pth 137XJdq3reNMJ9tkBNqKUYTY_dTlcwXc3
    ```

### Set Configuration
- **For Tiktok videos scraping:** Add the `DOWNLOADED_VIDS_DIR` **absolute** path for video downloading in `constants/scraper/constants.py`.

### To Run
- Use following command to run the script
    ```
    python3 main.py
    ```
- You must need to solve the Captcha of tiktok within 30 seconds.

## Output
Each list element represents a video and against each video following metrics are calculated:
- **laplacian:** A measure of image sharpness. The quality_score represents the level of blurriness, with higher values indicating a sharper image. 
- **structural_similarty:** A metric that measures the similarity between two images. The quality_score represents the similarity between the original and processed images, with higher values indicating a higher similarity. 
- **peak_signal_to_noise_ratio:** A metric that measures the ratio of the maximum possible power of a signal to the power of corrupting noise. The quality_score represents the PSNR value, with higher values indicating a higher quality image.

```
[
    {
        "ssstik.io_1715156633074.mp4": {
            "laplacian": {
                "quality_score": 53.257578720245895,
                "quality": "Blur"
            },
            "structural_similarty": {
                "quality_score": 0.7905307352416306,
                "quality": "Clear"
            },
            "peak_signal_to_noise_ratio": {
                "quality_score": 32.663645218665536,
                "quality": "Clear"
            }
        }
    },
    {
        "ssstik.io_1715156596076.mp4": {
            "laplacian": {
                "quality_score": 25.011922787196852,
                "quality": "Blur"
            },
            "structural_similarty": {
                "quality_score": 0.8358675813388196,
                "quality": "Clear"
            },
            "peak_signal_to_noise_ratio": {
                "quality_score": 32.46371983910255,
                "quality": "Clear"
            }
        }
    }
]
```