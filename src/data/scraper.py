# This script scrapes https://www.bbc.com/food/ for all recipes and captures
# the ingredients of each recipe and the regional cuisine name
# of that recipe - this will be part of my training & test sets to augment
# Kaggle's What's Cooking dataset.

import requests
from bs4 import BeautifulSoup
import pandas as pd
import multiprocessing as mp
import time

URL = "https://www.bbc.com/"
var = "food/cuisines"
df = pd.DataFrame()

regions = []
r = requests.get(URL + var)
soup = BeautifulSoup(r.text)

for i in soup.find_all('h3'):
    regions.append(i.text.lower().replace(" ", "_").replace("_recipes", ""))
