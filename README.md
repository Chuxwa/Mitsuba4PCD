# Mitsuba4PCD
**Mitsuba4PCD** is a point cloud rendering tool based on Python and Mitsuba, you can use Mitsuba's rich features to render virtual point cloud scenes. Note: Mitsuba 0.6 is suitable for CPU rendering and Mitsuba 3.0 is suitable for GPU rendering.

## Features

- **High-Quality Rendering**: Leverage the power of Mitsuba 3.0 to render physically accurate and photorealistic point cloud scenes.
- **Python Integration**: Provides an easy-to-use Python API for loading and processing point cloud data.
- **Flexible Rendering Settings**: Customize lighting, materials, and camera parameters to suit your specific rendering needs.
- **Extensible**: Easily integrate with other data processing and machine learning libraries.

## Installation

Ensure you have [Mitsuba 3.0](https://www.mitsuba-renderer.org/) installed. 

Or follow my environment setting:

```bash
conda create --name m4pcd python=3.10 -y
conda activate m4pcd
pip install -r requirements.txt
```

## Quick Start

Here’s a simple example showing how to use this library to render a point cloud:

```python
# load the data
pcl, colors = process_data(in_path)

for i in range(len(args.axis)):
    pcl = rotate(pcl, args.axis[i], args.yum[i])

# normlize
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
```

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

If you have any questions or suggestions, feel free to contact us at [wcx0602@mail.ustc.edu.cn](wcx0602@mail.ustc.edu.cn).
