import os
import subprocess
from PIL import Image
import cloudinary
import cloudinary.uploader
 
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

# cloudinary engine
def cloudinary_upload(sender, instance, **kwargs):
    if instance.image and not instance.image_url:
        if os.path.isfile(instance.image.path):
            compressed_image_path = compress_image(instance.image.path)
            if compressed_image_path:
                try:
                    result = cloudinary.uploader.upload(compressed_image_path, resource_type="image")
                    instance.image_url = result.get('secure_url')
                    instance.save()
                    os.remove(compressed_image_path)
                except Exception as e:
                    print(f"Error uploading to Cloudinary: {e}")

    elif instance.video and not instance.video_url:
        if os.path.isfile(instance.video.path):
            compressed_video_path = compress_video(instance.video.path)
            if compressed_video_path:
                try:
                    result = cloudinary.uploader.upload(compressed_video_path, resource_type="video")
                    instance.video_url = result.get('secure_url')
                    instance.save()
                    os.remove(compressed_video_path)
                except Exception as e:
                    print(f"Error uploading to Cloudinary: {e}")

    elif instance.file and not instance.file_url:
        if os.path.isfile(instance.file.path):
            try:
                result = cloudinary.uploader.upload(instance.file.path, resource_type="raw")
                instance.file_url = result.get('secure_url')
                instance.save()
            except Exception as e:
                print(f"Error uploading to Cloudinary: {e}")
       