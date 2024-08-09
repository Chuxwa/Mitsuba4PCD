import numpy as np
import scipy.linalg as linalg
import math


def rotate_mat(axis: list, radian: list):
    """give the mat of rotation

    Args:
        axis (list): the rotation axis
        radian (list): the rotation radian

    Returns:
        np.array: the mat of rotation
    """
    rot_matrix = linalg.expm(
        np.cross(np.eye(3), axis / linalg.norm(axis) * radian))
    return rot_matrix


def rotate(points: np.array, axis: list, angle: list):
    """rotate the points

    Args:
        points (np.array): the points before rotation
        axis (list): the rotation axis
        angle (list): the rotation angle

    Returns:
        np.array: the points after rotation
    """
    angle = math.pi/180*angle
    rot_matrix = rotate_mat(axis, angle)
    points = np.dot(points, rot_matrix)
    return points


def standardize_point(point: np.array, mins: int, maxs: int):
    """normlize the points

    Args:
        point (np.array): the points [n,3]
        mins (int): the mins of the scene
        maxs (int): the maxs of the scene

    Returns:
        np.array: the points [n,3]
    """
    center = (mins + maxs) / 2.0
    scale = np.amax(maxs - mins)
    point_result = ((point - center) / scale).astype(np.float32)
    return point_result


def standardize_pcl_bbox(pcl: np.array, bbox_corners: np.array):
    """normlize the point cloud and bboxes

    Args:
        pcl (np.array): the points [n,3]
        bbox_corners (np.array): the bbox_corners [n,3]

    Returns:
        np.array: the points [n,3]
        np.array: the bbox_corners [n,3]
    """
    mins = np.amin(pcl, axis=0)
    maxs = np.amax(pcl, axis=0)
    pcl_result = standardize_point(pcl, mins, maxs)
    bbox_result = standardize_point(bbox_corners, mins, maxs)
    return pcl_result, bbox_result


def box_center_to_corner(box: np.array):
    """box to conner

    Args:
        box (np.array): [7] :
            center is xyz of box center
            box_size is array(l,w,h)
            heading_angle is radius clockwise from pos x axis

    Returns:
        np.array: [8,3] array for 3D box cornders
    """
    center = box[0:3]
    center[..., [0, 1, 2]] = center[..., [0, 2, 1]]  # cam X,Y,Z = depth X,-Z,Y
    center[..., 1] *= -1

    l, w, h = box[3], box[4], box[5]

    rotation = 0  # /np.pi*180

    R = np.array([
        [np.cos(rotation), 0.0, np.sin(rotation)],
        [0.0, 1.0, 0.0],
        [-np.sin(rotation), 0.0, np.cos(rotation)]])

    x_corners = [l / 2, l / 2, -l / 2, -l / 2, l / 2, l / 2, -l / 2, -l / 2]
    y_corners = [h / 2, h / 2, h / 2, h / 2, -h / 2, -h / 2, -h / 2, -h / 2]
    z_corners = [w / 2, -w / 2, -w / 2, w / 2, w / 2, -w / 2, -w / 2, w / 2]
    corners_3d = np.dot(R, np.vstack([x_corners, y_corners, z_corners]))
    corners_3d[0, :] = corners_3d[0, :] + center[0]
    corners_3d[1, :] = corners_3d[1, :] + center[1]
    corners_3d[2, :] = corners_3d[2, :] + center[2]
    corners_3d = np.transpose(corners_3d)
    return corners_3d


def colormap(x: np.array = None, y: np.array = None, z: np.array = None, mode: str = ""):
    """set up the color mode

    Args:
        x (np.array): x of the points
        y (np.array): y of the points
        z (np.array): z of the points
        mode (str): the mode of color

    Returns:
        list: color of points
    """
    if mode == "gradient":
        vec = np.array([x, y, z])
        vec = np.clip(vec, 0.001, 1.0)
        norm = np.sqrt(np.sum(vec ** 2))
        vec /= norm
        return [vec[0], vec[1], vec[2]]
    elif mode == "gray":
        return [0.5, 0.5, 0.5]
    else:
        return [1.0, 0.0, 0.0]
