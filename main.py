from glob import glob
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
from scipy import ndimage
from PIL import Image


def loadImage(path: str, gray=False) -> np.ndarray:
    print(f"Loading : {path} with gray={gray}")
    with Image.open(path) as img:
        if gray:
            return np.array(img.convert("L"), np.float32)
        return np.array(img)


def showImg(data: np.ndarray):
    Image.fromarray(data).show()


def saveImg(data: np.ndarray, path: str):
    print(f"Saving to {path}")
    Image.fromarray(data.astype(np.uint8)).save(path)


def blurImg(img: np.ndarray, r: float) -> np.ndarray:
    return ndimage.gaussian_filter(img, r)


def getBlurRadius(img: np.ndarray):
    radii = np.linspace(0, 15, 15 * 3)
    n = len(radii)
    getMin = np.vectorize(lambda x: blurImg(img, x).min())
    mins = getMin(radii)
    dmins = mins[1:] - mins[: n - 1]
    return radii[1:][dmins == dmins.max()][0]


def main():
    # Get all files
    for vid_no in range(1, 7):
        files = glob(f"./raw/frames/src_{vid_no}_*.png")
        files.sort()
        rad = 0
        for file in files:
            frame_no = int(file.split("_")[-1].split(".")[0])
            img = loadImage(file, True)
            ori_img = loadImage(file)
            if rad == 0:
                rad = getBlurRadius(img)
                print(f"Set radius to {rad:5.2f}px")
            bl_img = blurImg(img, rad)
            min_img = ndimage.minimum_filter(bl_img, rad * 2)
            yInd, xInd = np.where(min_img == bl_img)
            print(f"Found {len(yInd):6d} centers")
            plt.imshow(ori_img / 255.0 / 3.0)
            plt.scatter(xInd, yInd, s=0.2, c="cyan")
            plt.axis("off")
            plt.savefig(
                f"./raw/centers/{vid_no}_{frame_no}.png",
                bbox_inches="tight",
                pad_inches=0,
                dpi=300,
            )
            plt.close()


if __name__ == "__main__":
    main()
