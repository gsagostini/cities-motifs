'''                   Collecting the Population Data                    '''

#This script reads the dataframe of cities from "cities_dataframe.py" and 
# adds a column with the population of the city, fetched from a csv list
# provided by UN-Habitat.

#############################################################################

import pandas as pd

#############################################################################

#We need the list of cities population and the dataframe:
    
population_file = "UNdata_Export_20181015_151853664.csv"
cities_df_file = "cities.csv"

#We also need a .csv file that relates names in our dataframe to the ones by
# UN when different. This happens because some cities have different ways of 
# transliterating their names into English:
    
altnames_file = "list_of_cities_altnames.csv"

#############################################################################

#The first function simply checks whether the population was already added to
# the dataframe. Returns a Boolean.
def check_pop(cities_df):
    if "Population" in cities_df.keys():
        print("Population data already added")
        return True
    else:
        return False

#The following function checks whether a city has an alternative name as for
# the UN data. If it does, it returns this other name.
def check_altname(city, altnames_df):
    if city in altnames_df["currName"]:
        altname = altnames_df[altnames_df['currName']==city]
        return altname
    else:
        return city

#The follow function gets and cleans the population dataframe from the UN
# list. We will take only the overallpopulation, not the one divided by sex.
def get_population_df(population_file):
    pop_df_raw = pd.read_csv(population_file, delimiter=";")
    population_df = pop_df_raw[pop_df_raw["Sex"] == "Both Sexes"]
    return population_df

#Now a function that, given the name of a city as it is in the UN list, gets
# its population. Returns a float or None:
def get_population(city, population_df):
    #First we try the straightforward version. We would like to get all the
    # cells that represent the city, then we will filter them.
    city_name = city.replace("_", " ")
    city_df = population_df[population_df["City"]==city_name]
    #In case there were no cells, we can still try upper case:
    if len(city_df) == 0:
        city_df = population_df[population_df["City"]==city_name.upper()]
    #If there is only one entry, that is the row we must use:
    if len(city_df) == 1:
        pop = city_df["Value"].iloc[0]
    #In case we found multiple rows, we select the most appropriate one:
    elif len(city_df) > 1:
        #The first thing we need to do is select the newest data. We sort the
        # dataframe extract by year, then select the entries corresponding to
        # the latest year available:
        city_df = city_df.sort_values(by="Year")#, ascending=False)
        latest_year = city_df["Year"].iloc[0]
        city_df = city_df[city_df["Year"] == latest_year]
        #Again, if there is only one row available after this filtering, we
        # have it:
        if len(city_df) == 1:
            pop = city_df["Value"].iloc[0]
        #There may be different values still. Namely, we must look at the 
        # type of area in consideration. We prefer the urban agglomeration:
        else:
            urbagg = city_df[city_df["City type"]=="Urban agglomeration"]
            if len(urbagg) > 0:
                pop = urbagg["Value"].iloc[0]
            #If this does not work, we get the first result and report it.
            else:
                #print("There may be multiple results")
                pop = city_df["Value"].iloc[0]
    #In case we still haven't found a population, we must return None:
    else: 
        pop = None
    return  pop

#The final function iterates over the cities in our dataframe and collects
# their population values, so that we can append the column
def append_population(cities_df, altnames_df, pop_df, verbose=False):
    cities_list = cities_df["City"].tolist()
    pop_list = []
    for city in cities_list:
        if verbose==True:
            print("City:", city)
        city_name = check_altname(city, altnames_df)
        pop = get_population(city_name, pop_df)
        pop_list.append(pop)
        if verbose==True:
            if pop != None:
                print("Population:", pop)
            else:
                print("Population not found")
            print("-"*30)
    pop_column = pd.DataFrame({'Population': pop_list})
    #reset index: 
    cities_df = cities_df.reset_index(drop=True)
    pop_column = pop_column.reset_index(drop=True)
    #concatenate both:
    cities_df = pd.concat([cities_df, pop_column], axis=1)
    cities_df.to_csv('cities_with_population.csv')
    return  cities_df

#############################################################################

pop_df = get_population_df(population_file)
altnames_df = pd.read_csv(altnames_file, delimiter=";")
cities_df = pd.read_csv(cities_df_file)

cities_df_new = append_population(cities_df, altnames_df, pop_df, True)

    