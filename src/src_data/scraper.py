# This script scrapes https://www.bbc.com/food/ for all recipes and captures
# the ingredients of each recipe and the regional cuisine name
# of that recipe - this will be part of my training & test sets to augment
# Kaggle's What's Cooking dataset.
# Usage: python3 src/src_data/scraper.py data/raw/bbc_scraped.csv

# dependencies
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import time
import multiprocessing as mp
import argparse


# read in command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('output_file')
args = parser.parse_args()

# global variables
# ----------------

URL = "https://www.bbc.com/"
var = "food/cuisines"
main_page_req = urlopen(URL + var)
soup = BeautifulSoup(main_page_req, 'html.parser')

# create list of names of all cuisines listed on BBC.com website
regions = []
for cuisine in soup.find_all('h3'):
    regions.append(cuisine.text.lower().replace(" ", "_").replace("_recipes", ""))

# dataframe to be built with scraped recipe dataset
df = pd.DataFrame()

def parallelize_search(region):
    '''
    Given a region from the list of regions scraped from BBC.com, parse through
    each regional cuisine and collect all recipes, their ingredients, and the
    cuisine label.

    Keyword arguments
    regions -- (string) Region of cuisine to search and scrape recipes from.

    Returns:
    df -- (df) Pandas dataframe with all recipes from BBC.com with labeled cuisine type,
    recipe name, and ingredient list.
    '''
    #identify df as a global variable
    global df
    req = urlopen(URL+"food/search?cuisines=" + region)
    soup = BeautifulSoup(req, 'html.parser')

    # determine whether number of pages each cuisine has is > 1
    if soup.find('ul', {'class' : 'pagination__list'}) != None: #
        # Get last page occuring of recipes
        num_pages = int(soup.find('ul', {'class' : 'pagination__list'}).text[-1])

        # for each page(x) of recipes of the cuisine type
        for x in range(1,num_pages + 1):
            recipe_page = URL + "food/search?cuisines=" + region + "&page=" + str(x)
            recipe_r = urlopen(recipe_page)
            recipe_soup = BeautifulSoup(recipe_r, 'html.parser')

            # for each recipe on page #x
            # 24 recipes per page
            for recipe in recipe_soup.find_all('div', {'class' : 'gel-layout__item gel-1/2 gel-1/4@xl'}):
                recipe_page = urlopen(URL + recipe.find('a')['href'])
                recipe_soup = BeautifulSoup(recipe_page, 'html.parser')

                # create empty dictionary to capture page details to append to df
                mapping_dict = {'ingredients' : []}
                mapping_dict['cuisine'] = region
                mapping_dict['recipe'] = recipe_soup.find('h1').text

                #capture list of ingredients as a single item
                mapping_dict['ingredients'] = [item.text for item in recipe_soup.find_all('li', {'class' : 'recipe-ingredients__list-item'})]
                df = df.append(mapping_dict, ignore_index = True)
                time.sleep(1)

    # if cuisine type only has 1 page of recipes
    else:
        # for each recipe on page #x
        # 24 recipes per page
        for recipe in soup.find_all('div', {'class' : 'gel-layout__item gel-1/2 gel-1/4@xl'}):
            recipe_page = urlopen(URL + recipe.find('a')['href'])
            recipe_soup = BeautifulSoup(recipe_page, 'html.parser')

            # create empty dictionary to capture page details to append to df
            mapping_dict = {'ingredients' : []}
            mapping_dict['cuisine'] = region
            mapping_dict['recipe'] = recipe_soup.find('h1').text

            #capture list of ingredients as a single item
            mapping_dict['ingredients'] = [i.text for i in recipe_soup.find_all('li', {'class' : 'recipe-ingredients__list-item'})]
            df = df.append(mapping_dict, ignore_index=True)
            time.sleep(1)

    return df

def main():

    # create a  pool for parallel processing
    pool = mp.Pool(mp.cpu_count())
    results = pool.map(parallelize_search, regions)
    pool.close()
    pool.join()

    # combine the results returned from parallelize_search
    results_df = pd.concat(results)

    # write the df to a csv saved at the output arg
    results_df.to_csv(args.output_file, index = False)

main()
