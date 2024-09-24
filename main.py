from glob import glob
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
from scipy import ndimage
from scipy.spatial import Delaunay, Voronoi, ConvexHull
from scipy.interpolate import griddata
from PIL import Image


def reject_outliers(data, m=2.0):
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / mdev if mdev else np.zeros(len(d))
    return data[s < m]


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
        clip_min = 0
        clip_max = 0
        for file in files:
            # if rad != 0:
            #     return
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

            plt.figure(figsize=(img.shape[1] / 300, img.shape[0] / 300))
            plt.imshow(ori_img / 255.0 / 3.0)
            plt.scatter(xInd, yInd, s=0.2, c="cyan")
            plt.axis("off")
            plt.ylim((0, img.shape[0] - 1))
            plt.xlim((0, img.shape[1] - 1))
            plt.savefig(
                f"./raw/centers/{vid_no}_{frame_no}.png",
                bbox_inches="tight",
                pad_inches=0,
                dpi=300,
            )
            plt.close()
            delaunay = Delaunay(np.column_stack(np.where(min_img == bl_img)))
            plt.figure(figsize=(img.shape[1] / 300, img.shape[0] / 300))
            plt.imshow(ori_img / 255.0 / 4.0)
            for tri in delaunay.simplices:
                tri_pos = delaunay.points[np.concatenate((tri, tri[:1]))]
                plt.plot(tri_pos[:, 1], tri_pos[:, 0], linewidth=0.1, c="white")
            plt.axis("off")
            plt.ylim((0, img.shape[0] - 1))
            plt.xlim((0, img.shape[1] - 1))
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
            grid_x, grid_y = np.mgrid[0 : img.shape[0] : 1, 0 : img.shape[1] : 1]
            grid_z = griddata(
                delaunay.points, nb, (grid_x, grid_y), method="linear", fill_value=0
            )
            plt.figure(figsize=(img.shape[1] / 300, img.shape[0] / 300))
            plt.imshow(grid_z, cmap="plasma", vmin=0.0, vmax=7.0, interpolation="none")
            plt.axis("off")
            plt.savefig(
                f"./raw/bond_order/{vid_no}_{frame_no}.png",
                bbox_inches="tight",
                pad_inches=0,
                dpi=300,
            )
            plt.close()
            vor = Voronoi(np.column_stack(np.where(min_img == bl_img)))
            plasma = plt.get_cmap("plasma")

            # generate clipping values
            if clip_min == 0 and clip_max == 0:
                areas = []
                for i in range(len(vor.points)):
                    poly = vor.regions[vor.point_region[i]]
                    if len(poly) == 0 or -1 in poly:
                        continue
                    poly_pos = vor.vertices[poly]
                    area = ConvexHull(poly_pos).area / rad / rad
                    areas.append(area)
                areas = reject_outliers(np.array(areas))
                avg = np.average(areas)
                std = np.std(areas)
                clip_min = avg - 7 * std
                clip_max = avg + 7 * std
                print(f"Setting clipping to {clip_min:5.3f}:{clip_max:5.2f}")

            def get_color(x):
                return plasma(np.clip((x - clip_min) / (clip_max - clip_min), 0, 1))

            areas = []
            verts = []
            plt.figure(figsize=(img.shape[1] / 300, img.shape[0] / 300))
            for i in range(len(vor.points)):
                poly = vor.regions[vor.point_region[i]]
                if len(poly) == 0 or -1 in poly:
                    continue
                poly_pos = vor.vertices[poly]
                area = ConvexHull(poly_pos).area / rad / rad
                areas.append(area)
                verts.append(vor.points[i])
                plt.fill(
                    poly_pos[:, 1],
                    poly_pos[:, 0],
                    facecolor=get_color(area),
                    edgecolor=get_color(area),
                    linewidth=0.5,
                )
            plt.ylim((0, img.shape[0] - 1))
            plt.xlim((0, img.shape[1] - 1))
            plt.axis("off")
            plt.savefig(
                f"./raw/voronoi/{vid_no}_{frame_no}.png",
                bbox_inches="tight",
                pad_inches=0,
                dpi=300,
            )
            plt.close()
            verts = np.array(verts)
            areas = np.array(areas)
            colors = get_color(areas)
            grid_x, grid_y = np.mgrid[0 : img.shape[0] : 1, 0 : img.shape[1] : 1]
            grid_z = griddata(
                verts, colors, (grid_x, grid_y), method="cubic", fill_value=0
            )
            plt.figure(figsize=(img.shape[1] / 300, img.shape[0] / 300))
            plt.imshow(
                grid_z,
                interpolation="none",
            )
            plt.axis("off")
            plt.ylim((0, img.shape[0] - 1))
            plt.xlim((0, img.shape[1] - 1))
            plt.savefig(
                f"./raw/voronoi_interp/{vid_no}_{frame_no}.png",
                bbox_inches="tight",
                pad_inches=0,
                dpi=300,
            )
            plt.close()


if __name__ == "__main__":
    main()
