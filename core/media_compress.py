import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
import os
import subprocess
from PIL import Image
 

# Configuration       
cloudinary.config( 
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'), 
    api_key = os.getenv('CLOUDINARY_API_KEY'), 
    api_secret = os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

ffmpeg_path = 'ffmpeg'

# compress image 
def compress_image(input_path, compression_ratio=0.35):
    try:
        if not os.path.isfile(input_path):
            print(f"Input file {input_path} does not exist.")
            return None

        img = Image.open(input_path)
        scale_factor = 1 - compression_ratio
        new_width = int(img.width * scale_factor)
        new_height = int(img.height * scale_factor)

        compressed_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_compressed{ext}"

        compressed_img.save(output_path, quality=85, optimize=True)
        print(f"Image compressed successfully: {output_path}")

        return output_path

    except Exception as e:
        print(f"An error occurred while compressing image: {e}")
        return None

# compress video 
def compress_video(input_path, crf=30):
    try:
        if not os.path.isfile(input_path):
            print(f"Input file {input_path} does not exist.")
            return None

        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_compressed{ext}"

        cmd = [
            ffmpeg_path,
            "-i", input_path,
            "-vcodec", "libx264",
            "-crf", str(crf),
            "-preset", "slow",
            "-profile:v", "high",
            "-level", "4.2",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            "-acodec", "aac",
            "-b:a", "128k",
            output_path
        ]
        subprocess.run(cmd, check=True)
        print(f"Video compressed successfully: {output_path}")
        return output_path

    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None