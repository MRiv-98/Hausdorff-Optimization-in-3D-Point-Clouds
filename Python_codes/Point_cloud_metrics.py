from Python_codes.Point_cloud_optimization import PCLinkage


class PCHMetrics:
    @staticmethod
    def max_distance_error(alpha_radius, point_cloud_1, point_cloud_2):
        max_distance = 0
        for i in range(len(point_cloud_1)):
            x1 = point_cloud_1['x'][i]
            y1 = point_cloud_1['y'][i]
            z1 = point_cloud_1['z'][i]
            points = PCLinkage.detection_area(alpha_radius, x1, y1, z1, point_cloud_2)

            if points[0][1] > max_distance:
                max_distance = points[0][1]
        
        return max_distance

    @staticmethod
    def hausdorff_distance(alpha_radius, point_cloud_1, point_cloud_2):
        max_distance = PCHMetrics.max_distance_error(alpha_radius, point_cloud_1, point_cloud_2)

        for i in range(len(point_cloud_2)):
            x1 = point_cloud_2['x'][i]
            y1 = point_cloud_2['y'][i]
            z1 = point_cloud_2['z'][i]
            points = PCLinkage.detection_area(alpha_radius, x1, y1, z1, point_cloud_1)

            if points[0][1] > max_distance:
                max_distance = points[0][1]
        
        return max_distance
    
    @staticmethod
    def max_average_error(alpha_radius, point_cloud_1, point_cloud_2):
        sum_distances = 0
        for i in range(len(point_cloud_1)):
            x1 = point_cloud_1['x'][i]
            y1 = point_cloud_1['y'][i]
            z1 = point_cloud_1['z'][i]
            points = PCLinkage.detection_area(alpha_radius, x1, y1, z1, point_cloud_2)
            sum_distances += points[0][1]
        
        return sum_distances/len(point_cloud_1)
        