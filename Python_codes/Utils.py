from plyfile import PlyData, PlyElement, PlyData
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class Utils:
    @staticmethod
    def read_point_clouds(directory, point_cloud_object):

        route = f"Point_clouds_{directory}/{point_cloud_object}.ply"
        pc_ply = PlyData.read(route)

        return pc_ply['vertex'].data
    
    @staticmethod
    def save_point_clouds(vertex_coordinates, directory, pc_object, pc_type):
        vertex_list = []
        for i in range(len(vertex_coordinates['x'])):
            vertex_list.append( (vertex_coordinates['x'][i], 
                                 vertex_coordinates['y'][i], 
                                 vertex_coordinates['z'][i]) )

        vertex_data = np.array(vertex_list, 
                               dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4')])

        vertex_element = PlyElement.describe(vertex_data, 'vertex')

        ply_data = PlyData([vertex_element], text=True)

        ply_data.write(f"Point_clouds_{directory}/{pc_object}_{pc_type}.ply")

    @staticmethod
    def create_csv(vertex_coordinates, directory, pc_object, pc_type):
        dataframe =  pd.DataFrame(
            {'x': vertex_coordinates['x'], 
             'y': vertex_coordinates['y'], 
             'z': vertex_coordinates['z']})
        dataframe.to_csv(
            f'Point_clouds_{directory}/{pc_object}_{pc_type}.csv')
        
    @staticmethod
    def plot_point_clouds(orig_cloud, simp_cloud):
        # Visualizing point clouds after scalling and centering
        fig = plt.figure(figsize=plt.figaspect(0.5))
        
        # Original point cloud
        ax = fig.add_subplot(1, 2, 1, projection='3d')
        ax.scatter(xs = orig_cloud['x'], ys = orig_cloud['y'], zs=orig_cloud['z'], s=1)
        ax.view_init(0,45,0)
        
        # Simplified point cloud
        ax = fig.add_subplot(1, 2, 2, projection='3d')
        ax.scatter(xs = simp_cloud['x'], ys = simp_cloud['y'], zs=simp_cloud['z'], s=2, c="#30ED1F")
        ax.view_init(0,45,0)
        plt.show()
        
    @staticmethod
    def read_csv(directory, pc_object, pc_type):
        return pd.read_csv(
            f'Point_clouds_{directory}/{pc_object}_{pc_type}.csv')