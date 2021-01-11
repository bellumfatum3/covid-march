# -*- coding: utf-8 -*-
"""
Created on Sat Mar 14 18:23:52 2020
https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series
@author: pwnrz
"""

# Imports to set up for validation scripts
import matplotlib.pyplot as plt
import glob
import time
import datetime
import pandas as pd
from sklearn.linear_model import LinearRegression

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)

etl_time = datetime.datetime.now().strftime("%Y%m%d%H%M")
layout_descriptor = 'covid19'
start = time.time()
now = datetime.datetime.today().strftime('%Y%m%d')

# Get a list of all the file paths that ends with .txt from in specified directory
file_list_txt = glob.glob('*.csv')

counter = 0

input_file_full = r'C:\Users\pwnrz\Documents\Python Scripts\output_covid19 03\time_series_covid19_confirmed_global.csv'
print("Line Counter Starting.")
with open(input_file_full) as f:
    i = 0
    for line in f:
        i += 1
print(f"Line Counter Finished with a total of {i} lines. \n Starting loads.")
f.close()
print(f'Loading file for COVID 19 %s' % input_file_full)
df = pd.read_csv(input_file_full,
                         encoding='utf8',
                        #dtype='str',
                         parse_dates=False,
                         keep_default_na=False,
                         na_values='',
                         index_col=None,
                         header = 'infer')
df.drop('Lat', axis=1, inplace=True)
df.drop('Long', axis=1, inplace=True)
df.drop('Province/State', axis=1, inplace=True)

# Primary Dataframes. Minimimal transformation
df.rename(columns = {'Country/Region':'country'}, inplace = True) 
valuelist = ['US','USA','United States','United States of America']
#valuelist = ['Italy']
usa = df[df.country.isin(valuelist)]


# Pivoting and cleaning up data for preparation of inflection point analysis. 
intermed = usa.pivot_table(columns=['country','1/22/20'])
usa_pivoted = intermed.to_frame()
usa_pivoted.reset_index(inplace=True)
usa_pivoted.drop('country', axis=1, inplace=True)
usa_pivoted.drop('1/22/20', axis=1, inplace=True) # This value always be a constant. 
usa_pivoted = usa_pivoted.rename(columns = {
    'level_0':'date',
    0: 'number_infected'
})
usa_pivoted['date'] = pd.to_datetime(usa_pivoted['date'])
usa_pivoted['daily_inflection_rate'] = usa_pivoted.number_infected.pct_change()*100
usa_pivoted['average'] = usa_pivoted.daily_inflection_rate.mean()
usa_pivoted['moving_average'] = usa_pivoted.rolling(window=5)['daily_inflection_rate'].mean()

usa_pivoted_ir = usa_pivoted.plot(style = '-',linewidth = 4,x='date', y=['daily_inflection_rate','average','moving_average'], fontsize = 30, figsize=(40,24), grid=True,title = 'Inflection Rate of Confirmed COVID19 Cases in the United States')
# usa_pivoted_ir.set(xlabel="Date",ylabel="Inflection Rate")

plt.xlabel('Date',fontsize = 32)
plt.ylabel('Inflection Rate',fontsize = 32)
plt.title('Inflection Rates of Confirmed COVID19 Cases in the United States, \n March 29th, 2020', fontsize=50)
plt.legend(fontsize = 30)
usa_pivoted_ir.figure.savefig('D:/usa_pivoted_ir.png')



# Filtering out older dates to make it easier to graph
mask = (usa_pivoted['date'] > '2019-02-20')
usa_pivoted_filtered = usa_pivoted.loc[mask]

# Plots 
usa_plotted = usa.plot(kind="bar",legend = False,grid = True,title = 'Cumulative Infected COVID19 Cases in the United States')
usa_plotted.set(xlabel="Days Since First Confirmed Case", ylabel="Number Infected")


usa_pivoted.set_index(['date'],inplace=True)
usa_pivoted.number_infected.plot()

usa_pivoted_filtered.set_index(['date'],inplace=True)
usa_pivoted_filtered.number_infected.plot()


# Excel Outputs for Analysis
df.to_excel("D:/all.xlsx",index = False)
usa.to_excel("D:/usa.xlsx",index = False)
usa_pivoted.to_excel('D:/usa_pivoted.xlsx')
print("Script finished.")