from glob import glob
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
from scipy import ndimage
from scipy.spatial import Delaunay
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
    for vid_no in range(2, 7):
        files = glob(f"./raw/frames/src_{vid_no}_*.png")
        files.sort()
        rad = 0
        for file in files:
            if rad != 0:
                return
            frame_no = int(file.split("_")[-1].split(".")[0])
            img = loadImage(file, True)
            ori_img = loadImage(file)
            # Get optimal blur radius
            if rad == 0:
                rad = getBlurRadius(img)
                print(f"Set radius to {rad:5.2f}px")
            # Find all centers of shadows (atoms)
            bl_img = blurImg(img, rad)
            min_img = ndimage.minimum_filter(bl_img, rad * 2)
            yInd, xInd = np.where(min_img == bl_img)
            print(f"Found {len(yInd):6d} centers")
            # plt.imshow(ori_img / 255.0 / 3.0)
            # plt.scatter(xInd, yInd, s=0.2, c="cyan")
            # plt.axis("off")
            # plt.savefig(
            #     f"./raw/centers/{vid_no}_{frame_no}.png",
            #     bbox_inches="tight",
            #     pad_inches=0,
            #     dpi=300,
            # )
            # plt.close()
            delaunay = Delaunay(np.column_stack(np.where(min_img == bl_img)))
            plt.imshow(ori_img / 255.0 / 4.0)
            for tri in delaunay.simplices:
                tri_pos = delaunay.points[np.concatenate((tri, tri[:1]))]
                plt.plot(tri_pos[:, 1], tri_pos[:, 0], linewidth=0.1, c="white")
            plt.axis("off")
            plt.savefig(
                f"./raw/delaunay/{vid_no}_{frame_no}.png",
                bbox_inches="tight",
                pad_inches=0,
                dpi=300,
            )
            plt.close()
            nb = []
            for i in range(len(delaunay.points)):
                nb.append(np.sum(delaunay.simplices == i))


if __name__ == "__main__":
    main()
