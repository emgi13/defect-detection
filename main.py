import os
from PIL import Image
from PIL.ImageFile import ImageFile

# video file name
vid_no = 1
base_frame_name = f"src_{vid_no}"


def process(img: ImageFile):
    print(f"Processing {img.filename}, size:{img.size}")


def main():
    base_dir = "./raw/frames"
    if not os.path.exists(base_dir):
        print("Please extract the frames from the source files first")
        return
    files = os.listdir(base_dir)
    files.sort()
    for filename in files:
        if filename.startswith(base_frame_name) and filename.endswith(".png"):
            file_path = os.path.join(base_dir, filename)
            with Image.open(file_path) as img:
                process(img)


if __name__ == "__main__":
    main()
