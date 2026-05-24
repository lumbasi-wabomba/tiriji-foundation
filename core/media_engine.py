import os
import subprocess
from PIL import Image
import cloudinary
import cloudinary.uploader

ffmpeg_path = 'ffmpeg'
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff'}
VIDEO_EXTS = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}


def compress_image(input_path, compression_ratio=0.35):
    try:
        if not os.path.isfile(input_path):
            raise FileNotFoundError(f"Input file does not exist: {input_path}")

        img = Image.open(input_path)
        scale_factor = 1 - compression_ratio
        new_width  = int(img.width  * scale_factor)
        new_height = int(img.height * scale_factor)
        compressed_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_compressed{ext}"
        compressed_img.save(output_path, quality=80, optimize=True)
        print(f"Image compressed: {output_path}")
        return output_path

    except Exception as e:
        print(f"compress_image failed: {e}")
        return None   

def compress_video(input_path, crf=28):
    try:
        if not os.path.isfile(input_path):
            raise FileNotFoundError(f"Input file does not exist: {input_path}")

        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_compressed{ext}"

        cmd = [
            ffmpeg_path, "-y",
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
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f"Video compressed: {output_path}")
        return output_path

    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr.decode() if e.stderr else e}")
        return None
    except Exception as e:
        print(f"compress_video failed: {e}")
        return None


def upload_media(filepath: str) -> dict:
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    _, ext = os.path.splitext(filepath)
    ext = ext.lower()

    try:
        if ext in IMAGE_EXTS:
            compressed_path = compress_image(filepath)
            upload_path = compressed_path if compressed_path else filepath  
            result = cloudinary.uploader.upload(upload_path, resource_type="image")

            if compressed_path and os.path.isfile(compressed_path):
                os.remove(compressed_path)  
            if not result.get("secure_url"):
                raise RuntimeError("Cloudinary returned no URL for image")
            return {"url": result["secure_url"], "type": "image"}

        elif ext in VIDEO_EXTS:
            compressed_path = compress_video(filepath)
            upload_path = compressed_path if compressed_path else filepath
            result = cloudinary.uploader.upload(upload_path, resource_type="video")

            if compressed_path and os.path.isfile(compressed_path):
                os.remove(compressed_path)
            if not result.get("secure_url"):
                raise RuntimeError("Cloudinary returned no URL for video")
            return {"url": result["secure_url"], "type": "video"}

        else:
            result = cloudinary.uploader.upload(filepath, resource_type="raw")

            if not result.get("secure_url"):
                raise RuntimeError("Cloudinary returned no URL for file")
            return {"url": result["secure_url"], "type": "file"}

    except Exception as e:
        raise RuntimeError(f"upload_media failed for {filepath}: {e}") from e