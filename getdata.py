'''                Functions for downloading city networks                '''

#This script contains all functions necessary to correctly download the graph
# of a city from Open Street Maps. If requested, one can also save all the
# data in specified directories. We first collect city outlines, and then
# get the graphs from polygons.

#############################################################################

import osmnx as ox

#############################################################################

#This function takes a gdf file and inspects it. It is called a few times by
# the get_outline function, so it is convenient to keep it apart from it:
def inspect(gdf, success = False, error = None):
    #The result must be a Polygon or Multipolygon in type:
    gdf_type = gdf.geometry.geom_type[0]
    if gdf_type == 'Polygon' or gdf_type == 'MultiPolygon':
        #The result must have a reasonable size:
        gdf_area = gdf.area[0]
        if gdf_area > 1 or gdf_area < 0.0001:
            #The shapefile is too small or too large to be correct.
            error = "SizeError"
        else:
            #It worked!
            success = True
    #If the result is not of the correct type, that is our error:
    else:
        error = "NoPolygonError"
    return gdf, success, error


#The first get function will get the gdf file from OSMnx, which corresponds
# to a city outline. There are several exceptions we should handle:
def get_outline(city_str, i_max = 4):
    #We define a success flag and an error message in case we can't find the
    # city outline:
    success = False
    error = None
    #Ideally, we should get it very simply from OSMnx:
    gdf = ox.gdf_from_place(city_str)
    #If there are no result, then there is nothing we can do:
    if gdf.size == 0:
        error = "NoResultError"
    #In case there is at least one result, we should inspect it to know if it
    # is good or if we need to search for other results:
    else:
        gdf, success, error = inspect(gdf)
        #In case we did not achieve success, we can check other results of
        # the gdf search:
        if success == "False":
            i = 2
            while i < i_max and success == False:
                try:
                    gdf = ox.gdf_from_place(city_str, which_result=i)
                    if gdf.size != 0:
                        gdf, success, error = inspect(gdf)
                        i += 1
                    else:
                        #In this case there are no more significant results:
                        i = i_max
                #Of course, there may not be i results. In this case there is
                # no need on iterating further:
                except:
                    i = i_max
    return success, error, gdf
    

#Now, given a city string, we can call the function above and get the graph
# from an outline, which is more precise than the typical graph_from_place:
def get_graph(city_str):
    success, error, gdf = get_outline(city_str)
    if success == True:
        graph = ox.graph_from_polygon(gdf.geometry[0])
        return graph
    else:
        return None

#############################################################################