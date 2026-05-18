
from Python_codes.Utils import Utils
from Python_codes.Point_cloud_preprocessing import PCPreprocessing as PCPrep
from Python_codes.Point_cloud_optimization import PCLinkage as PCLink, PCReassignement as PCReass
from Python_codes.Point_cloud_metrics import PCHMetrics as PCMet
from timeit import default_timer as timer


####################################################################################################################################
### Settings
## File name of point clouds
pc_name = "Brain" # Unprocessed files must be on directory 'Point_clouds_unprocessed' in ply format


## Preprocessing parameters 
do_preprocessing = True # Preprocessing always plot point clouds to ensure alignment, save processed files and calculate Hau(Or<->Simp)
aling_axes = True # if axes in orig and simp clouds are already aligned, set this value to false.
axes_orders = False # if proposed method to align axes doesn't work, set manually the orders into a dictionary as shown below
""" 
axes_orders = {
    'original': [2,0,1],
    'simplified': [0,2,1]
} # this order is necessary to work with "Bunny" point clouds
"""

## Optimizing parameters
do_optimizing = True
alpha_radius = 0.1 # higher value will take more time execution with same results
approach = 'first' # possible values: 'first', 'second', 'third'
save_point_clouds = True


## Metrics parameter
calculate_metrics_before = True # Hau(Or <-> Simp), max_error(Or <-> Simp) and avg_error(Or <-> Simp)
calculate_metrics_after = True # Hau(Or <-> Opt), max_error(Or <-> Opt) and avg_error(Or <-> Opt)



####################################################################################################################################
### Prerprocessing
print(f"### Process in point cloud: {pc_name}\n")
if do_preprocessing:
    print("### Prerprocessing Process")
    # Getting coordinates vertex from both point clouds 
    print("## Reading point clouds")
    vertex_orig_cloud = Utils.read_point_clouds(
        directory="unprocessed/Original_Clouds", point_cloud_object=pc_name)
    vertex_simp_cloud = Utils.read_point_clouds(
        directory="unprocessed/Simplified_Clouds", point_cloud_object=pc_name)
    print(f"Original cloud coordinates: {vertex_orig_cloud[0:10]}")
    print(f"Simplified cloud coordinates: {vertex_simp_cloud[0:10]} \n")


    # Scalling point clouds coordinates
    print("## Scalling point clouds")
    vertex_orig_cloud, vertex_simp_cloud = PCPrep.scalling_point_clouds(vertex_orig_cloud, vertex_simp_cloud, 
                                                                        aling_axes=aling_axes, axes_orders=axes_orders)

    # Superimposing point clouds coordinates by centering them
    print("## Superimposing point clouds")
    PCPrep.centering_coordinates(vertex_orig_cloud)
    PCPrep.centering_coordinates(vertex_simp_cloud)

    # Saving ply files of scalled point clouds
    Utils.save_point_clouds(vertex_orig_cloud, directory = "processed/Original_Clouds", 
                            pc_object = pc_name, pc_type= "original_scalled")
    Utils.save_point_clouds(vertex_simp_cloud, directory = "processed/Simplified_Clouds",     
                            pc_object = pc_name, pc_type= "simplified_scalled")

    # Saving or reading csv files of scalled point clouds
    Utils.create_csv(vertex_orig_cloud, directory = "processed/Original_Clouds", 
                            pc_object = pc_name, pc_type= "scalled")
    Utils.create_csv(vertex_simp_cloud, directory = "processed/Simplified_Clouds", 
                            pc_object = pc_name, pc_type= "scalled")
    
    # Ploting point clouds
    Utils.plot_point_clouds(vertex_orig_cloud, vertex_simp_cloud)
            
    

####################################################################################################################################
### Metrics before optimization process
# Reading csv files
or_cloud_csv = Utils.read_csv(directory = "processed/Original_Clouds", pc_object = pc_name, pc_type= "scalled")
simp_cloud_csv = Utils.read_csv(directory = "processed/Simplified_Clouds", pc_object = pc_name, pc_type= "scalled")


# Calculating Metrics (Original_cloud <-> Simplified_cloud)
if calculate_metrics_before:
    # Calculating Hausdorff Distance (Hau(Or <-> Simp))
    print("## Calculating Hausdorff Distance (Original <-> Simplified)")
    Haus_Or_to_Simp = PCMet.hausdorff_distance(alpha_radius, or_cloud_csv, simp_cloud_csv)
    print(f"Hausdorf Distance Original to Simplified: {Haus_Or_to_Simp} \n")
    MaxError_Or_to_Simp = PCMet.max_distance_error(alpha_radius, or_cloud_csv, simp_cloud_csv)
    print(f"Maximun distance error Original to Optimized: {MaxError_Or_to_Simp}")
    AvgError_to_Simp = PCMet.max_average_error(alpha_radius, or_cloud_csv, simp_cloud_csv)
    print(f"Average Error Original to Optimized: {AvgError_to_Simp}")

####################################################################################################################################
### Optimization process
if do_optimizing:
    print("### Optimization Process")

    # Reading point clouds (csv)
    or_cloud_csv = Utils.read_csv(directory = "processed/Original_Clouds", pc_object = pc_name, pc_type= "scalled")
    simp_cloud_csv = Utils.read_csv(directory = "processed/Simplified_Clouds", pc_object = pc_name, pc_type= "scalled")
    print(f"Original cloud: {len(or_cloud_csv)} points")
    print(f"Simplified cloud: {len(simp_cloud_csv)} points \n")

    # Making neighborhoods and linking first simplified point
    print("## Making neighborhoods")
    start_timer = timer()
    neighborhoods_or, neighborhoods_simp = PCLink.making_neighborhoods(or_cloud_csv, simp_cloud_csv, alpha_radius)
    or_cloud_csv['Neighborhood'] = neighborhoods_or
    simp_cloud_csv['Neighborhood'] = neighborhoods_simp

    print(f"Neighborhoods_or: {neighborhoods_or[:20]}")
    print(f"Neighborhoods_simp: {neighborhoods_simp[:20]}\n")

    # First approach
    if approach == 'first':
        print("# First Approach")
        assignments, _ = PCReass.reassigning_point_cloud(
            or_cloud_csv, simp_cloud_csv, neighborhoods_or, 
        )
        
    # Second approach
    elif approach == 'second':
        print("# Second Approach")
        PCLink.linking_unliked_simplified_points(
            or_cloud_csv, simp_cloud_csv, alpha_radius, neighborhoods_or, neighborhoods_simp
        )
        or_cloud_csv['Neighborhood'] = neighborhoods_or
        simp_cloud_csv['Neighborhood'] = neighborhoods_simp

        assignments, _ = PCReass.reassigning_point_cloud(
            or_cloud_csv, simp_cloud_csv, neighborhoods_or, 
        )

    # Third approach
    elif approach == 'third':
        print("# Third Approach")
        assignments, local_hausdorff = PCReass.reassigning_point_cloud(
            or_cloud_csv, simp_cloud_csv, neighborhoods_or
        )

        PCReass.iterative_reassigning(
            or_cloud_csv, simp_cloud_csv, assignments, neighborhoods_or,
            local_hausdorff
        )

    total_time = (timer()-start_timer)

    x, y, z = [], [], []
    for assign in assignments:
        for i in assign:
            x.append(i[0])
            y.append(i[1])
            z.append(i[2])

    print(f"{len(x)} assignments were made in {total_time} seconds (optimization process) \n")


    # Saving optimized point cloud as ply and csv
    if save_point_clouds: 
        vertex_opt_cloud ={'x': x, 'y': y,'z': z}

        Utils.save_point_clouds(vertex_opt_cloud, directory = "optimized", 
                                pc_object = pc_name, pc_type= f"{approach}_approach")
        Utils.create_csv(vertex_opt_cloud, directory = "optimized/csv", 
                                pc_object = pc_name, pc_type= f"{approach}_approach")

####################################################################################################################################
### Metrics after optimization process
# Calculating Metrics (Original_cloud <-> Optimized_cloud)
if calculate_metrics_after:
    opt_cloud_csv = Utils.read_csv(directory = "optimized/csv", pc_object = pc_name, pc_type= f"{approach}_approach")
    print("## Calculating Metrics (Original cloud <-> Optimized cloud)")
    Haus_Or_to_Opt = PCMet.hausdorff_distance(alpha_radius, or_cloud_csv, opt_cloud_csv)
    print(f"Hausdorf distance Original to Optimized: {Haus_Or_to_Opt}")
    MaxError_Or_to_Opt = PCMet.max_distance_error(alpha_radius, or_cloud_csv, opt_cloud_csv)
    print(f"Maximun distance error Original to Optimized: {MaxError_Or_to_Opt}")
    AvgError_to_Opt = PCMet.max_average_error(alpha_radius, or_cloud_csv, opt_cloud_csv)
    print(f"Average Error Original to Optimized: {AvgError_to_Opt}")