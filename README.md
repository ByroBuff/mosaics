
# mosaics
This is a project that converts normal video into a mosaic like piece of art where each pixel is replaced with a specific image depending on its brightness. It can be used to generate some fairly interesting effects as seen in [this](https://www.instagram.com/p/DMMqQvSAacP) video by [@alg.comp.mod](https://www.instagram.com/alg.comp.mod/) on Instagram (credit to him for the idea for this project).

## Usage
```
usage: main.py [-h] --input INPUT --output OUTPUT --scale_dir SCALE_DIR --scale_steps SCALE_STEPS [--pixel_size PIXEL_SIZE] [--max_pixels MAX_PIXELS] [--fps FPS]

Create a mosaic video from a source video.

options:
  -h, --help            show this help message and exit
  --input INPUT         Path to input video file
  --output OUTPUT       Path to output video file
  --scale_dir SCALE_DIR
                        Directory containing scale sprites
  --scale_steps SCALE_STEPS
                        Number of images in the brightness scale
  --pixel_size PIXEL_SIZE
                        Size of each pixel in the mosaic
  --max_pixels MAX_PIXELS
                        Maximum number of pixels in the resized video
  --fps FPS             Frames per second for the output video
```

## Example
https://github.com/user-attachments/assets/34cab244-cb73-4890-92ce-6e1b7a68b1ed

https://github.com/user-attachments/assets/30116d8c-aaf8-40b7-9198-c7c4f196d4e9

If you zoom in on the second video, the moonrise pixels are now different phases of the moon depending on how bright it is!
