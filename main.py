from pathlib import Path
from PIL import Image
import cv2, numpy as np
from tqdm import tqdm
import argparse

PIXEL_SIZE = 20
MAX_PIXELS = 5_000
FPS = 15

def get_rotation(video):
    """Detect rotation angle from video metadata (so portrait videos are handled correctly)"""
    angle = 0
    if hasattr(cv2, "CAP_PROP_ORIENTATION_META"):
        val = video.get(cv2.CAP_PROP_ORIENTATION_META)
        if val in (90, 180, 270):
            angle = int(val)
    return angle

def rotate(frame, angle):
    """rotate frame to the specified angle"""
    if angle == 90:
        return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    if angle == 180:
        return cv2.rotate(frame, cv2.ROTATE_180)
    if angle == 270:
        return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return frame

def calc_resized_size(w, h, MAX_PIXELS):
    """
    Calculate the resized dimensions while maintaining aspect ratio.
    Maximises number of pixels up to MAX_PIXELS.
    """
    scale = 1.0
    while (w * scale) * (h * scale) > MAX_PIXELS:
        scale *= 0.99
    return int(w * scale), int(h * scale)

def load_sprites(SCALE_DIR, SCALE_STEPS):
    """
    Load sprites from the scale directory and resize them to PIXEL_SIZE
    Load all frames before instead of as needed to avoid repeated resizing and loading.
    """
    return [Image.open(SCALE_DIR / f"scale{i}.png").resize(
                (PIXEL_SIZE, PIXEL_SIZE), Image.LANCZOS)
            for i in range(1, SCALE_STEPS + 1)]

def mosaic_frame(loaded_frame: Image.Image, sprites: dict, out_w: int, out_h: int, tiles_w: int, tiles_h: int, SCALE_STEPS, PIXEL_SIZE) -> Image.Image:
    """Create a mosaic of a frame using the loaded sprites"""
    small = loaded_frame.resize((tiles_w, tiles_h), Image.LANCZOS)
    out = Image.new("RGB", (out_w, out_h), "white")
    
    for y in range(tiles_h):
        for x in range(tiles_w):
            r, g, b = small.getpixel((x, y))
            scale_index = int(round(((r + g + b) / 3) / 255 * (SCALE_STEPS - 1)))
            out.paste(sprites[scale_index], (x * PIXEL_SIZE, y * PIXEL_SIZE))
    return out

def main(VIDEO_IN, VIDEO_OUT, SCALE_DIR, SCALE_STEPS, PIXEL_SIZE, MAX_PIXELS, FPS):
    video = cv2.VideoCapture(VIDEO_IN)
    if not video.isOpened():
        raise RuntimeError("Cannot open input video")

    rotate_angle = get_rotation(video)

    ok, video_data = video.read()
    if not ok: # haha
        raise RuntimeError("Empty video")
    
    first = rotate(video_data, rotate_angle)
    video.set(cv2.CAP_PROP_POS_FRAMES, 0)

    src_h, src_w = first.shape[:2]
    tiles_w, tiles_h = calc_resized_size(src_w, src_h, MAX_PIXELS)
    out_w, out_h     = tiles_w * PIXEL_SIZE, tiles_h * PIXEL_SIZE

    writer = cv2.VideoWriter(
        VIDEO_OUT,
        cv2.VideoWriter_fourcc(*"avc1"),
        FPS,
        (out_w, out_h))

    sprites = load_sprites(SCALE_DIR, SCALE_STEPS)

    # calculate step size for frame skipping
    src_fps = video.get(cv2.CAP_PROP_FPS)
    step = max(1, int(src_fps / FPS))

    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    for i in tqdm(range(0, frame_count, step), desc="Frames"):
        video.set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, frame = video.read()
        if not ok:
            break
        
        frame = rotate(frame, rotate_angle)
        loaded_frame   = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        mosaic = mosaic_frame(loaded_frame, sprites, out_w, out_h, tiles_w, tiles_h, SCALE_STEPS, PIXEL_SIZE)
        writer.write(cv2.cvtColor(np.asarray(mosaic), cv2.COLOR_RGB2BGR))

    video.release()
    writer.release()
    print(f"[✓] Saved video to {VIDEO_OUT}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a mosaic video from a source video.")
    parser.add_argument("--input", type=str, required=True, help="Path to input video file")
    parser.add_argument("--output", type=str, required=True, help="Path to output video file")
    parser.add_argument("--scale_dir", type=str, required=True, help="Directory containing scale sprites")
    parser.add_argument("--scale_steps", type=int, required=True, help="Number of images in the brightness scale")
    parser.add_argument("--pixel_size", type=int, default=PIXEL_SIZE, required=False, help="Size of each pixel in the mosaic")
    parser.add_argument("--max_pixels", type=int, default=MAX_PIXELS, required=False, help="Maximum number of pixels in the resized video")
    parser.add_argument("--fps", type=int, default=FPS, required=False, help="Frames per second for the output video")
    
    args = parser.parse_args()
    main(args.input, args.output, Path(args.scale_dir), args.scale_steps, args.pixel_size, args.max_pixels, args.fps)