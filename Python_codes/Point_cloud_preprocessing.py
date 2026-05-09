from sklearn.preprocessing import MinMaxScaler
 
class PCPreprocessing: 
    @staticmethod
    def checking_negatives(values_list):
        minor = min(values_list)
        if minor < 0:
            return [v + abs(minor) for v in values_list]
        else:
            return values_list

    @staticmethod
    def linking_axis(axis_original, axis_simp):
        original_axis_ranges = []
        simp_axis_ranges = []
        for i in range(len(axis_original)):
            axis_range = max(axis_original[i]) - min(axis_original[i])
            original_axis_ranges.append(axis_range)

            axis_range = max(axis_simp[i]) - min(axis_simp[i])
            simp_axis_ranges.append(axis_range)

        aux_original_ranges = original_axis_ranges[0:]
        aux_simp_ranges = simp_axis_ranges[0:]
        sequence_high = []
        sequence_low = []
        while(len(sequence_high) < len(axis_original)):
            minor = aux_original_ranges.pop(aux_original_ranges.index(min(aux_original_ranges)))
            sequence_high.append(original_axis_ranges.index(minor))

            minor = aux_simp_ranges.pop(aux_simp_ranges.index(min(aux_simp_ranges)))
            sequence_low.append(simp_axis_ranges.index(minor))
            
        return {
                "x_axis": PCPreprocessing.checking_negatives(axis_original[sequence_high[0]]),
                "y_axis": PCPreprocessing.checking_negatives(axis_original[sequence_high[1]]),
                "z_axis": PCPreprocessing.checking_negatives(axis_original[sequence_high[2]]),
            },{
                "x_axis": PCPreprocessing.checking_negatives(axis_simp[sequence_low[0]]),
                "y_axis": PCPreprocessing.checking_negatives(axis_simp[sequence_low[1]]),
                "z_axis": PCPreprocessing.checking_negatives(axis_simp[sequence_low[2]])
            }

    @staticmethod
    def min_max_scalling(axis_original, axis_simp, scalling_range = [0,1]):
        print("Original Cloud Before scalling")
        aux_x = [[i] for i in axis_original['x_axis']]
        aux_y = [[i] for i in axis_original['y_axis']]
        aux_z = [[i] for i in axis_original['z_axis']]
    
        min_x, max_x = min(axis_original['x_axis']), max(axis_original['x_axis'])
        min_y, max_y = min(axis_original['y_axis']), max(axis_original['y_axis'])
        min_z, max_z = min(axis_original['z_axis']), max(axis_original['z_axis'])
    
        print(f"x range = [{min_x}, {max_x}], with a length of {max_x-min_x}")
        print(f"y range = [{min_y}, {max_y}], with a length of {max_y-min_y}")
        print(f"z range = [{min_z}, {max_z}], with a length of {max_z-min_z}\n")
    
        max_length = max_z-min_z
    
        print("Original Cloud After scalling")
        min_x, max_x = min_x/max_length, max_x/max_length
        min_y, max_y = min_y/max_length, max_y/max_length
        min_z, max_z = scalling_range[0], scalling_range[1]
    
        axis_original_scalled = {
            "x": [i[0] for i in MinMaxScaler(feature_range = (min_x, max_x)).fit_transform(aux_x)],
            "y": [i[0] for i in MinMaxScaler(feature_range = (min_y, max_y)).fit_transform(aux_y)],
            "z": [i[0] for i in MinMaxScaler(feature_range = (min_z, max_z)).fit_transform(aux_z)]
        }
    
        min_x, max_x = min(axis_original_scalled['x']), max(axis_original_scalled['x'])
        min_y, max_y = min(axis_original_scalled['y']), max(axis_original_scalled['y'])
        min_z, max_z = min(axis_original_scalled['z']), max(axis_original_scalled['z'])
    
        print(f"x range = [{min_x}, {max_x}]")
        print(f"y range = [{min_y}, {max_y}]")
        print(f"z range = [{min_z}, {max_z}]\n")
    
    
        print("Simplified Cloud Before scalling")
        min_x_simp, max_x_simp = min(axis_simp['x_axis']), max(axis_simp['x_axis'])
        min_y_simp, max_y_simp = min(axis_simp['y_axis']), max(axis_simp['y_axis'])
        min_z_simp, max_z_simp = min(axis_simp['z_axis']), max(axis_simp['z_axis'])
        print( f"x range = [{min_x_simp}, {max_x_simp}],with a length of {max_x_simp-min_x_simp}")
        print(f"y range = [{min_y_simp}, {max_y_simp}], with a length of {max_y_simp-min_y_simp}")
        print(f"z range = [{min_z_simp}, {max_z_simp}], with a length of {max_z_simp-min_z_simp}\n")
    
        print("Simplified Cloud After scalling")
        aux_x = [[i] for i in axis_simp['x_axis']]
        aux_y = [[i] for i in axis_simp['y_axis']]
        aux_z = [[i] for i in axis_simp['z_axis']]
    
        axis_simp_scalled = {
            "x": [i[0] for i in MinMaxScaler(feature_range = (min_x, max_x)).fit_transform(aux_x)],
            "y": [i[0] for i in MinMaxScaler(feature_range = (min_y, max_y)).fit_transform(aux_y)],
            "z": [i[0] for i in MinMaxScaler(feature_range = (min_z, max_z)).fit_transform(aux_z)]
        }
    
        
        print(f"x range = [{min(axis_simp_scalled['x'])}, {max(axis_simp_scalled['x'])}]")
        print(f"y range = [{min(axis_simp_scalled['y'])}, {max(axis_simp_scalled['y'])}]")
        print(f"z range = [{min(axis_simp_scalled['z'])}, {max(axis_simp_scalled['z'])}]\n")
    
        return axis_original_scalled, axis_simp_scalled
    
    @staticmethod
    def taking_coordinate_values(vertex_coordinates):
        x, y, z = [], [], []
        for coord in vertex_coordinates:
            x.append(coord[0])
            y.append(coord[1])
            z.append(coord[2])
        return [x, y, z]


    @staticmethod
    def scalling_point_clouds(vertex_orig_cloud, vertex_simp_cloud):
        # Linking axis of both clouds
        axis_original, axis_simp = PCPreprocessing.linking_axis(
            PCPreprocessing.taking_coordinate_values(vertex_orig_cloud),
            PCPreprocessing.taking_coordinate_values(vertex_simp_cloud))
        
        # Scalling point clouds
        vertex_original_scalled, vertex_simp_scalled = PCPreprocessing.min_max_scalling(axis_original, axis_simp)
        
        # Returning values
        return vertex_original_scalled, vertex_simp_scalled

    @staticmethod
    def centering_coordinates(vertex_values):
        for axis in ['x', 'y', 'z']:
            print(f"Axis: {axis}")
            minor = min(vertex_values[axis])
            higher = max(vertex_values[axis])
            print(f"before: [{minor}, {higher}]")
            axis_range = higher- minor
            
            # closest to 0
            if  minor < 1-higher:
                diference = ((1- axis_range)/2) - minor
                vertex_values[axis] = [v + diference for v in vertex_values[axis]]

            # closest to 1
            else:
                diference = higher - (1 - ((1- axis_range)/2))
                vertex_values[axis] = [v - diference for v in vertex_values[axis]]
                
            print(f"after: [{min(vertex_values[axis])}, {max(vertex_values[axis])}] with centered by = {diference}\n")