import numpy as np
import argparse

xml_ball_segment = """
    <shape type="sphere">
        <float name="radius" value="{}"/>
        <transform name="toWorld">
            <translate x="{}" y="{}" z="{}"/>
        </transform>
        <bsdf type="diffuse">
            <rgb name="reflectance" value="{},{},{}"/>
        </bsdf>
    </shape>
"""

xml_bar_segment = """
    <shape type="cylinder">
        <float name="radius" value="{}"/>
        <point name="p0" x="{}" y="{}" z="{}"/>
        <point name="p1" x="{}" y="{}" z="{}"/>
        <bsdf type="twosided">
            <bsdf type="diffuse">
                <rgb name="reflectance" value="{},{},{}"/>
            </bsdf>
        </bsdf>
    </shape>
"""


def size_setup(width: int = 100, height: int = 100, xml_h: str = ""):
    """set up the size of the render window

    Args:
        width (int): the width of the image
        height (int): the hight of the image
        xml_h (str): the head of the xml file

    Returns:
        str: the head of the xml file
    """
    xml_h = xml_h.format(width=width, height=height)
    return xml_h


def eye_setup(origin: list = [1.5, 1.5, 1.5], target: list = [0, 0, 0], up: list = [0, 0, 1], xml_h: str = ''):
    """set up the eye of the toworld transformer

    Args:
        origin (list): the position of the origin point
        target (list): the position of the target point, default = [0,0,0]
        up (list): the direction of the up, default = [0,0,1]
        xml_h (str): the head of the xml file

    Returns:
        str: the head of the xml file
    """
    xml_h = xml_h.format(origin_x=origin[0], origin_y=origin[1], origin_z=origin[2],
                 target_x=target[0], target_y=target[1], target_z=target[2],
                 up_x=up[0], up_y=up[1], up_z=up[2])
    return xml_h


def fov_setup(fov: int = 25, xml_h: str = ''):
    """set up the fov of the render transformer

    Args:
        fov (int, optional): Defaults to 25.
        xml_h (str, optional): the head of the xml file. Defaults to ''.

    Returns:
        str: the head of the xml file
    """
    xml_h = xml_h.format(fov=fov)
    return xml_h


def init_head(args: argparse.Namespace):
    """init the head of xml for rendering

    Args:
        args (argparse.Namespace): the args of the render

    Returns:
        str: the head of the xml file
    """
    xml_head_toworld = """
<scene version="0.5.0">
    <integrator type="path">
        <integer name="maxDepth" value="-1"/>
    </integrator>
    <sensor type="perspective">
        <float name="farClip" value="100"/>
        <float name="nearClip" value="0.1"/>
        <transform name="toWorld">
            <lookat origin="{origin_x},{origin_y},{origin_z}" target="{target_x},{target_y},{target_z}" up="{up_x},{up_y},{up_z}"/>"""
    xml_head_fov = """
        </transform>
        <float name="fov" value="{fov}"/>
        
        <sampler type="ldsampler">
            <integer name="sampleCount" value="256"/>
        </sampler>"""
    xml_head_size = """
        <film type="hdrfilm">
            <integer name="width" value="{width}"/>
            <integer name="height" value="{height}"/>
            <rfilter type="gaussian"/>
            <boolean name="banner" value="false"/>
        </film>
    </sensor>
    
    <bsdf type="roughplastic" id="surfaceMaterial">
        <string name="distribution" value="ggx"/>
        <float name="alpha" value="0.05"/>
        <float name="intIOR" value="1.46"/>
        <rgb name="diffuseReflectance" value="1,1,1"/> <!-- default 0.5 -->
    </bsdf>
"""
    origin = [float(v) for v in args.origin.split(',')]
    target = [float(v) for v in args.target.split(',')]
    up = [float(v) for v in args.up.split(',')]
    xml_head_toworld = eye_setup(origin, target, up, xml_head_toworld)

    fov = args.fov
    xml_head_fov = fov_setup(fov, xml_head_fov)

    w, h = [int(v) for v in args.size.split("x")]
    xml_head_size = size_setup(w, h, xml_head_size)

    return [xml_head_toworld, xml_head_fov, xml_head_size]


def init_tail(radius: float, min_z: float):
    """init the tail of xml for rendering

    Args:
        radius (float): the radius of the point
        min_z (float): the mins of z 

    Returns:
        str: the tail of the xml file
    """
    xml_tail = """
    <shape type="rectangle">
        <ref name="bsdf" id="surfaceMaterial"/>
        <transform name="toWorld">
            <scale x="10" y="10" z="1"/>
            <translate x="0" y="0" z="{}"/>
        </transform>
    </shape>
    
    <shape type="rectangle">
        <transform name="toWorld">
            <scale x="10" y="10" z="1"/>
            <lookat origin="-4,4,20" target="0,0,0" up="0,0,1"/>
        </transform>
        <emitter type="area">
            <rgb name="radiance" value="6,6,6"/>
        </emitter>
    </shape>
</scene>
"""
    xml_tail = xml_tail.format(min_z - radius)
    return xml_tail


def add_point(point: np.array, color: np.array, radius: float, xml: str = ''):
    """add point info to the xml file

    Args:
        point (np.array): the position of 3D point 
        color (np.array): the color of the point
        radius (float): the radius of the point
        xml (str, optional): the xml file. Defaults to ''.

    Returns:
        str: the xml file
    """
    xml.append(xml_ball_segment.format(radius, *point, *color))
    return xml


def add_point_cloud(point_cloud: np.array, colors: np.array, radius: float, xml: str = ''):
    """add point cloud info to the xml file

    Args:
        point_cloud (np.array): the info of the point cloud.
        colors (np.array): the colors of the points
        radius (float): the radius of the point
        xml (str, optional): the xml file. Defaults to ''.

    Returns:
        str: the xml file
    """
    for i in range(point_cloud.shape[0]):
        xml = add_point(point_cloud[i], colors[i], radius, xml)
    return xml


def add_bbox(bbox_corners: np.array, color: np.array, bar_radius: float, xml: str = ''):
    """add bbox info to the xml file

    Args:
        bbox_corners (_type_): the info of the bbox_corners. the shape of the bbox is [8, 3]
        color (_type_): the color of the bbox
        bar_radius (float): the radius of the bar
        xml (str, optional): the xml file. Defaults to ''.

    Returns:
        str: the xml file
    """
    lines = [[0, 1], [1, 2], [2, 3], [0, 3],
             [4, 5], [5, 6], [6, 7], [4, 7],
             [0, 4], [1, 5], [2, 6], [3, 7]]
    for j in range(12):
        point_a = bbox_corners[lines[j][0]]
        point_b = bbox_corners[lines[j][1]]
        xml.append(xml_bar_segment.format(
            bar_radius, *point_a, *point_b, *color))
    return xml
