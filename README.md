<h1 align="center"> Hausdorff Distance Optimization in 3D Point Clouds </h1>
<img width="3124" height="1581" alt="General methodology steps diagram" src="https://github.com/user-attachments/assets/9ec54418-6cae-4e32-9800-884ad0c0ed65" />

<p align="center">
  <img src="https://img.shields.io/badge/release_date-may_2026-blue">
  <img src="https://img.shields.io/badge/version-1.0-green">
</p>

## Description
Python project for optimizing the Hausdorff distance present in low-density (simplified) point clouds using a high-density (original) point cloud as a reference.

## Functionalities
- <b>Preprocessing:</b>
  - <b>Alignment axes </b>:To ensure optimization accuracy, the point clouds must be aligned in the same direction.
    <p align="center"><img width="2789" height="775" alt="clouds_alignment" src="https://github.com/user-attachments/assets/1d55a22e-0867-48e1-acf1-83c77c12a429" /></p>

  - <b>Min-max scalling</b>: To better understanding for error metrics, the point clouds must be on the same scale.
    <p align="center"> <img width="450px" alt="clouds_scalling" src="https://github.com/user-attachments/assets/efc01953-cb0d-4215-bcaa-b7f9eb2dc534" /></p>
  - <b>Centering coordinates</b>: To ensure adequate superimposing in the point clouds, they are centered in the range [0, 1].
    <p align="center"> <img width="450px" height="1829" alt="clouds_centering" src="https://github.com/user-attachments/assets/79ff85ed-6d0b-4403-a8aa-3ffa1bc93fad"/> </p>
- <b>Optimization</b>:
  - <b>Making neighborhoods (detection area)</b>: To create an initial segmentation (neighborhoods) in the original point cloud, a detection area is applied to each of its points to detect the nearest simplified cloud points and create a neighborhood for each simplified point; as shown below with a 2D example.
    <p align="center"> <img width="800px" height="1291" alt="clouds_detection_area" src="https://github.com/user-attachments/assets/583ab32a-1800-49ee-883b-87905091a5f8" /></p>
  - <b>First approach</b>: With only one point of the simplified cloud linked to each neighborhood, the simplified points are reassigned to the original neighborhood and those that were not linked are discarded.
    <p align="center"> <img width="450px" height="1168" alt="clouds_first_approach" src="https://github.com/user-attachments/assets/5a8074d6-2469-4f7c-9222-aca6f925b19b" /> </p>
  - <b>Second approach</b>: Those simplified points that were not linked in the formation of neighborhoods are linked to their nearest neighborhood that does not have a number of original points less than the number of simplified points already linked, and all the points of the simplified one are reassigned.
    <p align="center"> <img width="450px" height="1168" alt="clouds_second_approach" src="https://github.com/user-attachments/assets/b9f660b3-dcc7-4e42-a8a3-793db4a8ce15" /> </p>
  - <b>Third approach</b>: The first simplified point that was linked in the creation of neighborhoods is assigned, then, iteratively, more points are assigned to the neighborhood where the Hausdorff distance is greater until all the points of the simplified cloud have been used.
    <p align="center"> <img width="650px" height="1169" alt="clouds_third_approach" src="https://github.com/user-attachments/assets/086ce46a-15f0-47f1-a455-3ebff68e105f" /> </p>

- <b> Metrics in Point Clouds </b>:
  - <b> Hausdorff Distance</b>: Determined by:
    <p align="center">
    <img width="500px" alt="clouds_hausdorff" src="https://github.com/user-attachments/assets/fb31a7cf-8b0a-4745-a7c5-b7f1db5b45dc" />
    </p>
    where <img height="20px" alt="clouds_euclidean" src="https://github.com/user-attachments/assets/f6edbf97-da52-4b04-98e7-4fe497c29bef" /> is the euclidean distance between two points.
  - <b> Maximun Distance Error</b>: Determined by:
    <p align="center"> 
      <img width="400px" alt="clouds_max_error" src="https://github.com/user-attachments/assets/aa77f0b6-2347-4872-834b-1c9186b75172" />
    </p>
    where <img height="20px" alt="clouds_euclidean" src="https://github.com/user-attachments/assets/f6edbf97-da52-4b04-98e7-4fe497c29bef" /> is the euclidean distance between two points.
  - <b> Average Distance Error</b>: Determined by:
    <p align = "center">
      <img width="300px" alt="clouds_avg_error" src="https://github.com/user-attachments/assets/6d84bd0e-4a19-4f07-859f-9a0dcb8805aa" />
    </p>
    where <img height="20px" alt="clouds_euclidean2" src="https://github.com/user-attachments/assets/da64ea0b-6287-4868-ae7d-c1fe0719d89c" /> is the euclidean distance between two points and <img height="20px" alt="clouds_points_or_cloud" src="https://github.com/user-attachments/assets/b41bb213-661f-4eb2-988e-bd5b8c9cf70f" /> is the number of points in the original cloud.

## Open and Run 
To run the entire project sequentially, you can use the *testing.py* file, which outlines each step for preprocessing and optimizing the point clouds. 
To execute the code, it's necessary to download the four folders located in the repository: *Point_clouds_unprocessed*, *Point_clouds_processed*, *Point_clouds_optimized* and *Python_codes*.

If you want to test the procedure on an unused example, you need to place the clouds to be used in *Point_clouds_unprocessed*; placing the original cloud (high point density) in the *Original_Clouds* subfolder and the simplified cloud (low point density) in the *Simplified_Clouds* subfolder. Both in ply format.

Additionally, the *testing.py* file contains configuration variables that allow you to specify whether you only need to perform preprocessing or optimization itself; it also includes variables to determine whether you want to align the point clouds, whether you want to manually set the alignment (in the case of the examples used, this had to be done with the *Bunny* case), and even whether you want to calculate the metrics before/after optimization.

## Required Python Libraries
The entire projet was developed in Python 3.10, using the following external libraries
- *plyfile*
- *numpy*
- *pandas*
- *matplotlib*
- *math*
- *sklearn*

