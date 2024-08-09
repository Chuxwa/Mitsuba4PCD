import numpy as np
import os
import sys
import argparse
import scipy.linalg as linalg
import math
from utils_mitsuba_v3.xml_helpers import init_head, init_tail, add_point_cloud, add_bbox
from utils_mitsuba_v3.bbox_helpers import standardize_point, rotate, colormap, box_center_to_corner
import mitsuba as mi
import matplotlib.pyplot as plt
import imageio
import cv2

def render(xml_path):
    """render the 3D scene to 2D image

    Args:
        xml_path (str): path of the xml files
    """
    print(xml_path)
    assert os.path.exists(xml_path)
    mi.set_variant("scalar_rgb")
    scene = mi.load_file(xml_path)
    image = mi.render(scene)
    # mi.Bitmap(image).write(xml_path.replace('_.xml', '.exr'))
    mi.util.write_bitmap(xml_path.replace('.xml', '.png'), image)
    os.remove(xml_path)


def process_data(in_path):
    pcl  = np.load(in_path + "points.npy")
    colors  = np.load(in_path + "colors.npy")
    return pcl, colors

def paint_point_cloud(in_path, out_path, args):
    # load the data
    pcl, colors = process_data(in_path)

    for i in range(len(args.axis)):  # 旋转
        pcl = rotate(pcl, args.axis[i], args.yum[i])
    
    mins = np.amin(pcl, axis=0)
    maxs = np.amax(pcl, axis=0)

    pcl = standardize_point(pcl, mins, maxs)
    pcl = pcl[:, [2, 0, 1]]
    pcl[:, 0] *= -1
    pcl[:, 2] += 0.0125

    # save the info into xml file
    xml_path = os.path.join(args.workdir, out_path + ".xml") 
    xml_head = init_head(args)
    xml_tail = init_tail(args.radius, np.min(pcl[:, 2]))
    xml = xml_head
    xml = add_point_cloud(pcl, colors, args.radius, xml)
    xml.append(xml_tail)
    xml_content = str.join("", xml)
    with open(xml_path, "w") as f:
        f.write(xml_content)

    # render the picture
    render(xml_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="data",
                        type=str, help="root directory")
    parser.add_argument("--workdir", default="outputs",
                        type=str, help="working directory")
    parser.add_argument("--size", default="1000x1000",
                        type=str, help="size of the render window")
    parser.add_argument('--origin', default='2,2,2',
                        type=str, help="position of the origin")
    parser.add_argument('--target', default='0,0,0',
                        type=str, help="position of the target")
    parser.add_argument('--up', default='0,0,1', type=str,
                        help="direction of the up")
    parser.add_argument('--fov', default=25.0, type=float,
                        help="the fov of the render transformer")
    parser.add_argument("--radius", default=0.018,
                        type=float, help="radius of the ball")
    parser.add_argument('--bar_radius', default=0.005,
                        type=float, help="radius of the bar")
    parser.add_argument('--axis', default=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                        type=list, help="the rotation axis")
    parser.add_argument('--yum', default=[0, 0, 0],
                        type=list, help="the angle of the rotation")
    parser.add_argument("--bar_color", default=[1, 0, 0],
                        type=list, help='RGB color')
    args = parser.parse_args()

    if not os.path.exists(args.workdir):
        os.mkdir(args.workdir)
    
    mae_root = os.path.join(args.root, "test_")
    paint_point_cloud(mae_root, "test", args)
