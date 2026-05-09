from math import pow, sqrt
from sklearn.cluster import AgglomerativeClustering


class PCLinkage:
    @staticmethod
    def detection_area(alpha_radius, x1, y1, z1, pc_to_search):
        there_are_points = False
        r = alpha_radius
        while(there_are_points != True):
            # Se encuentran los vecinos dentro de un rango cúbico de r
            points = pc_to_search[(pc_to_search['x'] >= x1-r) & (pc_to_search['x'] <= x1+r)\
                & (pc_to_search['y'] >= y1-r) & (pc_to_search['y'] <= y1+r)\
                & (pc_to_search['z'] >= z1-r) & (pc_to_search['z'] <= z1+r)]

            if len(points) != 0:
                # Se almacenan los id's de los points
                ids = points.index[points['x'] != -1]
                points_distances = []

                # Se calcula la distancia con todos los points
                for ind in ids:
                    d = pow(points['x'][ind] - x1, 2) + pow(points['y'][ind] - y1, 2) + pow(points['z'][ind] - z1, 2)
                    
                    d = sqrt(d)
                    # si la distancia es menor igual a r, está dentro de la esfera
                    if d <= r:
                        points_distances.append([ind,d]) 

                # Se ordenan los vecinos de distancia cercana a lejana
                points_distances.sort(key = lambda distance: distance[1])
                if len(points_distances) != 0:
                    there_are_points = True
                else:
                    r = r + alpha_radius
            else:
                r = r + alpha_radius
                
        return points_distances
    
    
    @staticmethod
    def making_neighborhoods(or_cloud_csv, simp_cloud_csv, alpha_radius):
        # asignando todos los puntos de la nube original a un punto de la simplificada
        neighborhoods_or = [-1 for _ in range(len(or_cloud_csv['x']))]
        neighborhoods_simp = [-1 for _ in range(len(simp_cloud_csv['x']))]

        # se recorren todos los puntos de la nube original
        for i in range(len(or_cloud_csv['x'])):
            coord = or_cloud_csv.iloc[i, :]
            x1, y1, z1 = coord['x'], coord['y'], coord['z']
            
            # se buscan sus vecinos cercanos
            points = PCLinkage.detection_area(alpha_radius, x1, y1, z1, simp_cloud_csv)
            
            # se empiezan a construir los vecindarios
            neighborhoods_or[i] = f'V{points[0][0]}'
            neighborhoods_simp[points[0][0]] = f'V{points[0][0]}'

        return neighborhoods_or, neighborhoods_simp
    
    @staticmethod
    def linking_unliked_simplified_points(or_cloud, simp_cloud, alpha_radius, neighborhoods_or, neighborhoods_simp):
        unliked = simp_cloud.index[simp_cloud['Neighborhood'] == -1]

        # se recorren todos los puntos de la nube simplificada
        for i in unliked:
            coord = simp_cloud.iloc[i, :]
            x1, y1, z1 = coord['x'], coord['y'], coord['z']

            points = PCLinkage.detection_area(alpha_radius, x1, y1, z1, or_cloud)
            linked = False
            multiplier = 1

            while linked != True:
                for v in points:
                    if neighborhoods_or.count(neighborhoods_or[v[0]]) >= neighborhoods_simp.count(neighborhoods_or[v[0]]) +1:
                        neighborhoods_simp[i] = neighborhoods_or[v[0]]
                        linked = True
                        break

                # si no se logro ubicar con los primeros vecinos, se obtienen más
                if linked != True:
                    multiplier = multiplier+1
                    points_2 = PCLinkage.detection_area(alpha_radius*multiplier, x1, y1, z1, or_cloud)
                    for v in points:
                        points_2.remove(v)
                    points = points_2


class PCReassignement:
    @staticmethod
    def distance_between_points(x1, y1, z1, neighborhood, original_cloud, reference):
        ids_dist = []
        for index in neighborhood:
            coord = original_cloud.iloc[index, :]
            x2, y2, z2 = coord['x'], coord['y'], coord['z']
            distance = sqrt(pow(x2 - x1, 2) + pow(y2 - y1, 2) + pow(z2 - z1, 2))
            if distance > reference:
                ids_dist.append([index, distance])

        return ids_dist
    
    @staticmethod
    def neighbors_analysis(neighbors, original_cloud):
        greatest_dist = -1
        for v in range(len(neighbors)):
            # se crea vecindario auxiliar sin el vecino actual
            aux_vec = [v1 for v1 in neighbors]
            aux_vec.remove(neighbors[v])
            
            # se checan las distancias entre el vecino actual y los demás vecinos
            # y se elige la distancia mayor (distancia de hausdorf)
            coord = original_cloud.iloc[neighbors[v], :]
            x1, y1, z1 = coord['x'], coord['y'], coord['z'] 

            id_dist = PCReassignement.distance_between_points(x1, y1, z1,
                                                             aux_vec, original_cloud, 
                                                             greatest_dist)
            if len(id_dist) > 0:
                # reordenar
                id_dist.sort(key = lambda distance: distance[1], reverse = True)                
                # seleccionar datos de la mayor distancia
                greatest_dist = id_dist[0][1]
                id1 = neighbors[v]
                id2 = id_dist[0][0]

        return greatest_dist, id1, id2
    
    @staticmethod
    def search_around_center_mass(ids, or_cloud):
        x = [or_cloud['x'][id] for id in ids]
        y = [or_cloud['y'][id] for id in ids]
        z = [or_cloud['z'][id] for id in ids]
        aux_y = (sum(y))/len(y) # center of mass on the y-axis
        aux_z = (sum(z))/len(z) # center of mass on the z-axis
        cuts_number = 20

        for coord in [x, y, z]:
            first_round = True
            minor_dist_ref = 200
            minor_found = False
            upper_limit = max(coord)
            lower_limit = min(coord)

            while(minor_found != True):
                length = upper_limit - lower_limit
                if first_round == True:
                    limits = [lower_limit]
                    for n in range(1, cuts_number):
                        limits.append((length*n/cuts_number)+lower_limit)
                    limits.append(upper_limit)
                    first_round = False
                else:
                    limits = []
                    for n in range(1, cuts_number):
                        if n != 5:
                            limits.append((length*n/cuts_number)+lower_limit)
                if coord == x:
                    limits_distances = []
                    for lim in limits:
                        aux_x = lim
                        max_dist_lim = 0
                        for c1 in range(len(x)):
                            dist = round(sqrt(
                                pow(aux_x - x[c1],2) + pow(aux_y - y[c1],2) + pow(aux_z - z[c1],2)), 4)
                            if dist > max_dist_lim:
                                max_dist_lim = dist
                        limits_distances.append(max_dist_lim)
                elif coord == y:
                    limits_distances = []
                    for lim in limits:
                        aux_y = lim
                        max_dist_lim = 0
                        for c1 in range(len(x)):
                            d = round(sqrt(pow(x_asign - x[c1],2) + pow(aux_y - y[c1],2) + pow(aux_z - z[c1],2)), 4)
                            if d > max_dist_lim:
                                max_dist_lim = d
                        limits_distances.append(max_dist_lim)
                else:
                    limits_distances = []
                    for lim in limits:
                        aux_z = lim
                        max_dist_lim = 0
                        for c1 in range(len(x)):
                            d = round(sqrt(pow(x_asign - x[c1],2) + pow(y_asign - y[c1],2) + pow(aux_z - z[c1],2)), 4)
                            if d > max_dist_lim:
                                max_dist_lim = d
                        limits_distances.append(max_dist_lim)

                minor_dist_lim = min(limits_distances)
                index_lim = limits_distances.index(minor_dist_lim)
                
                if minor_dist_ref > minor_dist_lim:
                    minor_dist_ref = minor_dist_lim
                    if coord == x:
                        x_asign = limits[index_lim]
                    elif coord == y:
                        y_asign = limits[index_lim]
                    else:
                        z_asign = limits[index_lim]

                    if index_lim == 0:
                        lower_limit = limits[index_lim] - (length/4)
                        upper_limit = limits[index_lim + 1]
                    elif index_lim == len(limits)-1:
                        lower_limit = limits[index_lim - 1]
                        upper_limit = limits[index_lim] + (length/4)
                    else:
                        lower_limit = limits[index_lim - 1]
                        upper_limit = limits[index_lim + 1]
                    
                else:
                    minor_found = True
                    
        return x_asign, y_asign, z_asign, minor_dist_ref
    
    @staticmethod
    def assigning_one_to_some(or_cloud, neighbors):
        # si hay más de dos vecinos, se recorren todos los vecinos
        # y se asignan los datos de la distancia mayor
        greater_dist, id1, id2 = PCReassignement.neighbors_analysis(neighbors, or_cloud)
        greater_dist = greater_dist/2
        
        # se crea posición a la mitad de la distancia mayor
        x_asign = (or_cloud['x'][id1] + or_cloud['x'][id2]) / 2
        y_asign = (or_cloud['y'][id1] + or_cloud['y'][id2]) / 2
        z_asign = (or_cloud['z'][id1] + or_cloud['z'][id2]) / 2

        # Si la nueva posición tiene las dist mayores con respecto a los dos puntos anteriores, 
        # ya no se podrá reducir la dist de haus
        id_dist = PCReassignement.distance_between_points(
            x_asign, y_asign, z_asign, neighbors, or_cloud, greater_dist)
        if len(id_dist) > 0:
            for i in range(len(id_dist)-1, -1, -1):
                if id_dist[i][0] in [id1, id2]:
                    id_dist.pop(i)

        # Pero si hay al menos un punto que no deja reducirla, se tomara(n) en cuenta
        # para reposicionar la asignación
        if len(id_dist) > 0:
            ids = [k[0] for k in id_dist]
            ids.append(id1)
            ids.append(id2)
            x_asign, y_asign, z_asign, greater_dist = PCReassignement.search_around_center_mass(ids, or_cloud)
        return [x_asign, y_asign, z_asign], greater_dist
    
    @staticmethod
    def assigning_nearest(or_cloud, simp_cloud, simplified_points, neighbors):
        # se trabajan con tres listados
        # dos con las asignaciones finales a los puntos de la n_original
        prev_assignments = []
        prev_distances = []
        aux_ids_neighbors = [id_x for id_x in neighbors]
        
        # otro de la n_simpl para ir calculando distancias mínimas
        aux_simplified_points = [id_x for id_x in simplified_points]
        aux_assignments = []
        for id_1 in neighbors:
            # se determina cuál es el punto de la n_simp más cercano a este punto
            # de la n_original
            coord = or_cloud.iloc[id_1, :]
            x1, y1, z1 = coord['x'], coord['y'], coord['z']
            distance = 100
            
            # mientras queden puntos de la n_simp
            if len(aux_simplified_points) > 0:
                # si quedan,
                for id_2 in aux_simplified_points:
                    coord = simp_cloud.iloc[id_2, :]
                    x2, y2, z2 = coord['x'], coord['y'], coord['z']

                    d = round(sqrt(pow(x1 - x2,2) + pow(y1 - y2,2) + pow(z1 - z2,2)), 4)
                    if d < distance and id_2 not in prev_assignments:
                        distance = d
                        id_assign = id_2
                
                # entonces se asigna al punto más cercano
                prev_assignments.append(id_assign)
                prev_distances.append(distance)
                # y este ya no se tomará en cuenta
                aux_simplified_points.remove(id_assign)
                aux_dist = 0
            else:
                # si ya no quedan,
                for id_2 in simplified_points:
                    coord = simp_cloud.iloc[id_2, :]
                    x2, y2, z2 = coord['x'], coord['y'], coord['z']

                    d = round(sqrt(pow(x1 - x2,2) + pow(y1 - y2,2) + pow(z1 - z2,2)), 4)
                    if d < distance:
                        id_assign = id_2
                        distance = d
                
                # se busca hacer la asignación entre este punto y su hermano que comparte asignación
                id_3 = aux_ids_neighbors[prev_assignments.index(id_2)]
                
                x_assign = (or_cloud['x'][id_1] + or_cloud['x'][id_3]) / 2
                y_assign = (or_cloud['y'][id_1] + or_cloud['y'][id_3]) / 2
                z_assign = (or_cloud['z'][id_1] + or_cloud['z'][id_3]) / 2
                aux_dist = pow(
                    or_cloud['x'][id_1] - or_cloud['x'][id_3],2)
                aux_dist = aux_dist + pow(
                    or_cloud['y'][id_1] - or_cloud['y'][id_3],2)
                aux_dist = aux_dist + pow(
                    or_cloud['z'][id_1] - or_cloud['z'][id_3],2)
                aux_dist = sqrt(aux_dist)/2

                aux_assignments.append([x_assign, y_assign, z_assign])

                
                # y ya no se toman en cuenta para las asignaciones que faltan
                aux_ids_neighbors.remove(id_3)
                aux_ids_neighbors.remove(id_1)
                prev_assignments.remove(id_2)

        # ahora se acomodan los puntos que irán directamente sobre uno de la nube original
        for i in range(len(prev_assignments)):
            coord = or_cloud.iloc[aux_ids_neighbors[i], :]
            x_assign, y_assign, z_assign = coord['x'], coord['y'], coord['z']
            aux_assignments.append([x_assign, y_assign, z_assign])

        return aux_assignments, aux_dist
    
    @staticmethod
    def assigning_some_to_some(or_cloud, simp_cloud, ids_simp, neighbors):
        # se forma la lista de coordenadas para hacer el clústering
        coordinates = []
        for id_1 in neighbors:
            coord = or_cloud.iloc[id_1, :]
            x, y, z = coord['x'], coord['y'], coord['z']
            coordinates.append([x,y,z])

        # se hace el clustering
        clusters = AgglomerativeClustering(
            n_clusters=len(ids_simp), linkage="single").fit(coordinates)
        
        # se juntan los vecinos que pertenecen a un clúster
        aux_neighbors = []
        for i in range(len(neighbors)):
            aux_neighbors.append([neighbors[i], clusters.labels_[i]])

        # se determina cuál clúster corresponderá a cada punto de n_simp
        aux_clusters = [c for c in range(len(ids_simp))]
        clust_assign = []
        for i in range(len(ids_simp)):
            if len(aux_clusters) > 1 :
                coord = simp_cloud.iloc[ids_simp[i], :]
                x1, y1, z1 = coord['x'], coord['y'], coord['z']
                distance = 100
                closest_cluster = -1

                # determinar el punto más cercano
                for id_0 in neighbors:
                    coord = or_cloud.iloc[id_0, :]
                    x2, y2, z2 = coord['x'], coord['y'], coord['z']
                    
                    d = round(sqrt(pow(x1-x2, 2) + pow(y1-y2, 2) + pow(z1-z2, 2)), 4)
                    clus = list(filter(lambda x: x[0] == id_0, aux_neighbors))[0][1]
                    if d < distance and clus not in clust_assign:
                        distance = d
                        closest_cluster = clus
                # se asigna al punto más cercano
                clust_assign.append(closest_cluster)

                # y este cluster ya no se tomará en cuenta
                aux_clusters.remove(closest_cluster)

            else:
                clust_assign.append(aux_clusters[0])

        # se hacen las asignaciones correspondientes a cada clúster
        aux_assignments = []
        for i in range(len(ids_simp)):
            cluster_members = list(filter(lambda x: x[1] == clust_assign[i], aux_neighbors))
            ids_cluster = [i[0] for i in cluster_members]

            aux_assign, aux_dist = PCReassignement.first_general_scenario(or_cloud, ids_cluster)
            aux_assignments.append(aux_assign)
        
        return aux_assignments, aux_dist
    
    @staticmethod
    def first_general_scenario(or_cloud, neighbors):
        # si solo hay un vecino
        if len(neighbors) == 1:
            # se asigna al unico vecino
            coord = or_cloud.iloc[neighbors[0], :]
            x_assign, y_assign, z_assign = coord['x'], coord['y'], coord['z']
            return [x_assign, y_assign, z_assign], 0
        # si solo hay dos vecinos
        elif len(neighbors) == 2:
            x_asign = (or_cloud['x'][neighbors[0]] + or_cloud['x'][neighbors[1]]) / 2
            y_asign = (or_cloud['y'][neighbors[0]] + or_cloud['y'][neighbors[1]]) / 2
            z_asign = (or_cloud['z'][neighbors[0]] + or_cloud['z'][neighbors[1]]) / 2
            aux_dist = pow(
                or_cloud['x'][neighbors[1]] - or_cloud['x'][neighbors[0]],2)
            aux_dist = aux_dist + pow(
                or_cloud['y'][neighbors[1]] - or_cloud['y'][neighbors[0]],2)
            aux_dist = aux_dist + pow(
                or_cloud['z'][neighbors[1]] - or_cloud['z'][neighbors[0]],2)
            aux_dist = sqrt(aux_dist)/2
            return [x_asign, y_asign, z_asign], aux_dist
        # if there are more than 2
        else:
            return PCReassignement.assigning_one_to_some(or_cloud, neighbors)
        
    @staticmethod
    def second_general_scenario(or_cloud, simp_cloud, simplified_points, neighbors):
        if len(simplified_points) == len(neighbors):
            aux_assignments = []
            for i in range(len(simplified_points)):
                coord = or_cloud.iloc[neighbors[i], :]
                aux_assignments.append([coord['x'], coord['y'], coord['z']])
            return aux_assignments, 0

        elif len(simplified_points) == len(neighbors)-1:
            return PCReassignement.assigning_nearest( 
                or_cloud, simp_cloud, simplified_points, neighbors)
        
        else:
            return PCReassignement.assigning_some_to_some( 
                or_cloud, simp_cloud, simplified_points, neighbors)
    

    @staticmethod
    def reassigning_point_cloud(or_cloud, simp_cloud, neighborhoods_or):
        neighborhoods = set(neighborhoods_or)
        assignments = []
        local_hausdorff = []

        # recorriendo los puntos de la simplificada
        for neigh in neighborhoods:
            # se toman los vecinos formados
            neighbors = or_cloud.index[or_cloud['Neighborhood'] == neigh]
            # se toman los puntos de la simplificada a reacomodar
            simplified_points = simp_cloud.index[simp_cloud['Neighborhood'] == neigh]
            
            if len(simplified_points) == 1:
                aux_assign, aux_dist = PCReassignement.first_general_scenario(or_cloud, neighbors)
                assignments.append([aux_assign])
                local_hausdorff.append(aux_dist)
            
            # si hay más
            else:
                aux_assign, _ = PCReassignement.second_general_scenario(
                    or_cloud, simp_cloud, simplified_points, neighbors)
                assignments.extend([aux_assign])
                    
        return assignments, local_hausdorff
    
    @staticmethod
    def iterative_reassigning(or_cloud, simp_cloud, assignments, neighborhoods_or, local_hausdorf):
        points_used = len(assignments)
        neighborhoods_list = list(set(neighborhoods_or))
        is_all_used = False
        

        while not is_all_used:
            # se obtiene el vecindario con la distancia mayor y se aumenta en 10
            # sus asignaciones si no excede el número de puntos
            to_increase = 10
            index = local_hausdorf.index(max(local_hausdorf))
            or_points = or_cloud.index[or_cloud['Neighborhood'] == neighborhoods_list[index]]

            if len(assignments[index])+to_increase > len(or_points):
                to_increase = len(or_points) - len(assignments[index])
                
            if points_used + to_increase > len(simp_cloud):
                to_increase = len(simp_cloud['x'])- points_used
                is_all_used = True

            points_used += to_increase
            simp_points = simp_cloud.index[simp_cloud['Neighborhood'] == neighborhoods_list[index]].tolist()
            unliked_simp_points = simp_cloud.index[simp_cloud['Neighborhood'] == -1].tolist()
            for i in range(to_increase):
                simp_points.append(unliked_simp_points[i])
                simp_cloud.iloc[int(unliked_simp_points[i]), -1] = neighborhoods_list[index]

            aux_assign, aux_dist = PCReassignement.second_general_scenario(
                    or_cloud, simp_cloud, simp_points, or_points)
                    
            assignments[index] = aux_assign
            local_hausdorf[index] = aux_dist