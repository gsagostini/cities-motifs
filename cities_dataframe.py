'''                    Creating the dataframe of cities                    '''

#This script reads a list of cities and creates a dataframe with their names,
# countries, continents alongside the other columns we will need.

#############################################################################
#If the city graph files are already downloaded, then they must be on a
# directory "./Data/Country/City" and the Boolean below must be True:

downloaded = False

#############################################################################

import pandas as pd
import networkx as nx
import osmnx as ox
import csv

from datetime import datetime

import mcount

if downloaded == False:
    import getdata

#############################################################################

#The following function collects network information (nodes, edges, selfloops,
# and motifs) for a city string---that is, "city, country":
def get_network_info(city_str, verbose=False, draw=False, downloaded=False):
    if verbose == True:
        print("city:", city_str)
    start = datetime.now()
    #First we must get the graph from Open Street Maps. Either we already have
    # it on our system or we need to run getdata script:
    if downloaded == True:
        pass
    else:
        graph = getdata.get_graph(city_str)
    #Maybe there was a problem in finding the graph, in which case this city
    # is not good and we have to do something else with it.
    if graph == None:
        if verbose == True:
            print("We couldn't find a graph for this city.")
        return None, None, None, None, None
    if draw == True:
        ox.plot_graph(graph)
    if verbose == True:
        print("Took", datetime.now()-start, "seconds to get the graph")
    n = graph.order()
    m = graph.size()
    sl = nx.number_of_selfloops(graph)
    #Now we prepare the graph for our data through removing multiple edges
    # and self-loops:
    new_graph = nx.Graph(graph)
    new_graph.remove_edges_from(nx.selfloop_edges(new_graph))
    #We collect the new number of edges and the motif vector:
    m_simp = new_graph.size()
    motif_vector = mcount.get_motifvector(new_graph)
    if verbose == True:
        print("Took", datetime.now()-start, "seconds for everything")
    return n, m, m_simp, sl, motif_vector

#The following function takes the cities csv list and produces lists we will
# use in our dataframe:
def read_cities(cities_file, dlm=";"):
    cities = []
    countries = []
    continents = []
    with open(cities_file) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=dlm)
        next(readCSV)
        for row in readCSV:
            cities.append(row[1])
            countries.append(row[2])
            continents.append(row[3])
    return cities, countries, continents

#The following function takes the cities csv list and creates the dataframe
# with all information we want:
def get_dataframe(cities_file, dlm=";", verbose=False):
    #First we create an empty dataframe with the columns we want:
    column_names = ["City", "Country", "Continent", "Nodes", "Edges",
                    "Essential edges", "Self-loops", "3-paths", "Triangles",
                    "4-paths", "4-complete", "4-star", "Squares", "Diamonds",
                    "Tadpoles"]
    df = pd.DataFrame(columns = column_names)
    #We get the basic information from the list of cities that we have:
    cities, countries, continents = read_cities(cities_file, dlm)
    #Now we will iterate over this list of cities and get the network info
    # for each of them, appending it to our dataframe.
    for idx in range(len(cities)):
        city = cities[idx]
        country = countries[idx]
        continent = continents[idx]
        city_str = city.replace("_", " ") + ", " + country.replace("_", " ")
        n, m, m_simp, sl, mf = get_network_info(city_str, verbose, False)
        if n != None:
            new_row = [city, country, continent, n, m, m_simp, sl,
                       mf[0], mf[1], mf[2], mf[3], mf[4], mf[5], mf[6], mf[7]]
            df.loc[idx] = new_row 
        else: 
            df.loc[idx] = [city, country, continent, None, None, None, None,
                           None, None, None, None, None, None, None, None]
        if verbose == True:
                print("Row", idx, "appended!\n")
        df.to_csv('cities.csv')
    return df

#############################################################################

file = "list_of_cities.csv"
df = get_dataframe(file, verbose=True)

print(df)

df.to_csv('cities.csv')