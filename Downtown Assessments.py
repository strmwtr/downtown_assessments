#!/usr/bin/env python
# coding: utf-8

# # Analyzing Assessed Value of the Downtown Mall

# ## Goals: 
# 
#     *Provide descriptive statistics of assessed value over time for the City of Charlottesville's downtown mall
# 
#     *Map and chart assessed values over time

# ## Step 1: Aquire Data

# ### Assessment Values
#     Charlottesville's Open Data Portal : http://opendata.charlottesville.org/
# 
#     Real Estate (All Assessments) Dataset : http://opendata.charlottesville.org/datasets/real-estate-all-assessments
# 
#         * On the Real Estate dataset page, in the upper right corner of the window under the map click the APIs             drop down
#         * Copy the GeoJSON link
#         * Use the GeoJSON link to pull data directly from the Open Data portal using the code below
# 
#     Parcel Area Data : http://opendata.charlottesville.org/datasets/parcel-boundary-area
# 
# ### List of properties to use in analysis
# 
# Charlottesville GIS Viewer: https://gisweb.charlottesville.org/GisViewer/
# 
#     * Under Map option, turn on 'Parcels & Buildings' > 'Parcels'. Turn everything else off.
# 
#     * Zoom to area of interest on map
# 
#     * Under 'Tools' select 'Identify'
# 
#     * In 'Identify' toolbar select 'Custom Shape' and under 'Layer' select 'Parcels'
# 
#     * Using mouse on map, click boundary around area of interest
# 
#     * A list will appear in the left panel of the web page
# 
#     * In the panel click 'Tools' > 'Export All to Excel'
# 
#     * A window named 'Export Results' will open when your download is ready.
# 
#     * Click 'View Export' and save file to your project directory
# 
# <img src="https://github.com/strmwtr/downtown_assessments/blob/master/img/getting_pin_list.png?raw=true">

# # Step 2: Prepare Data

# ## Import .xls retrieved from the GIS Viewer into pandas

# In[1]:


#Import pandas module
import pandas as pd 

#Path to the .xls retrieve from the GIS Viewer
f = r'./data/pin_exp.xls'

#Create a dataframe that reads the .xls file
df = pd.read_excel(f)


# #### Remove all MULTIPIN parcels from df

# In[2]:


#Identify all rows in df where MULTIPIN column is not equal to 1
not_multipin = df['MULTIPIN'] != 1
#Create a new dataframe that only contains the rows identified in not_multipin
df = df[not_multipin]
df.head()


# ## Access json file for parcel areas

# In[3]:


formatted_gpins = [str(x) for x in df['GPIN'].unique()]
formatted_gpins = formatted_gpins
formatted_gpins = ','.join(formatted_gpins)

parcel_area_url = f"https://gisweb.charlottesville.org/arcgis/rest/services/OpenData_1/MapServer/43/query?where=GPIN%20in%20({formatted_gpins})&outFields=*&outSR=4326&f=json"

print(parcel_area_url)


# ## Preparing annual assessment data
# 
# Charlottesville's Open Data Portal : http://opendata.charlottesville.org/
# 
# Real Estate (All Assessments) Dataset : http://opendata.charlottesville.org/datasets/real-estate-all-assessments
# 
# * On the Real Estate dataset page, in the upper right corner of the window under the map click the 'API Explorer' tab
# * Copy the Query URL link and augment the link to match your query
# * Use the augmented link to pull data directly from the Open Data portal using the code below

# In[4]:


# importing the requests library 
import requests

formatted_pins = [f'%27{x}%27' for x in df['PIN'].unique()]
formatted_pins_1 = formatted_pins
formatted_pins_1 = ','.join(formatted_pins_1)

url1 = f"https://gisweb.charlottesville.org/arcgis/rest/services/OpenData_2/MapServer/2/query?where=UPPER(ParcelNumber)%20in%20({formatted_pins_1})%20&outFields=ParcelNumber,LandValue,ImprovementValue,TotalValue,TaxYear&outSR=4326&f=json"

r1 = requests.get(url1)

d1 = r1.json()

print(r1)


# After testing the requests.get(url), I can request up to 120 parcels at a time before recieving a 404 Error. I have 126 parcels of interest. I will break my request up into 2 parts, [:75] and [75:].

# ## Create data series based on features and combine data frames into a single df

# In[5]:


df1 = pd.DataFrame(d1['features'])


# ## Create a single data frame based on combined series data

# In[6]:


assessments = pd.DataFrame([x for x in df1['attributes']], dtype = 'object')
assessments = assessments.astype({'TaxYear': 'int64', 'ImprovementValue': 'int64','LandValue': 'int64','TotalValue': 'int64', 'ParcelNumber': 'str'})
assessments.head()


# ## Create data frame from df that holds PIN and GPIN. Will be used to joined assessments, so that parcel area can be joined with assessments

# In[7]:


df_key = pd.DataFrame(df[['PIN','GPIN']], dtype = 'str')
df_key.head()


# In[12]:


d = pd.merge(assessments, df_key, how='inner', left_on=['ParcelNumber'], right_on=['PIN'])
print(assessments.shape, d.shape)


# # Step 3: Analyze

# In[50]:


#Create data frame of assessed values for all parcels by specified year
year_min = int(d['TaxYear'].min())
year_max = int(d['TaxYear'].max())


#year_col = [x for x in range(year_min, year_max + 1)]
#total_val_col = [d['TotalValue'][d['TaxYear'] == x].mean() for x in range(year_min, year_max + 1)]
mean_vals = pd.DataFrame([[year_col, total_val_col]], columns = ['TaxYear','TotalValue'], dtype = 'int64')
#mean_vals = pd.DataFrame(columns = ['TotalValue', 'ImprovementValue', 'LandValue', 'TaxYear'])
mean_vals

#print(d[['TotalValue', 'ImprovementValue', 'LandValue', 'TaxYear' ]][d['TaxYear'] == x].mean())

#x = d['ParcelNumber'].str.contains('2800371C0')
#y = d[x].sort_values('TaxYear')
#y.plot(x='TaxYear', y='TotalValue', figsize=(15,10), grid=True)


# In[11]:


#Plot single parcel by tax year vs total value

x = d['ParcelNumber'].str.contains('2800371C0')
y = d[x].sort_values('TaxYear')
y.plot(x='TaxYear', y='TotalValue', figsize=(15,10), grid=True)


# print("\nassessments['ParcelNumber'].describe()\n", assessments['ParcelNumber'].describe())
# 
# print("\nassessments['TaxYear'].describe()\n", assessments['TaxYear'].describe())
# 
# print("\nassessments['TaxYear'].min(), assessments['TaxYear'].max()\n", assessments['TaxYear'].min(), assessments['TaxYear'].max())
# 
# print("\nassessments['ImprovementValue'].describe()\n", assessments['ImprovementValue'].describe())
# 
# print("\nassessments['LandValue'].describe()\n", assessments['LandValue'].describe())
# 
# print("\nassessments['TotalValue'].describe()\n", assessments['TotalValue'].describe())

# taxyearmin = assessments['TaxYear'] == assessments['TaxYear'].min()
# assessments[taxyearmin].describe()

# taxyearmax = assessments['TaxYear'] == assessments['TaxYear'].max()
# assessments[taxyearmax].describe()

# ## assessments[taxyearmax].describe()-assessments[taxyearmin].describe()

# import folium
# 
# print(parcel_area_url)
# 
# m = folium.Map(location=[38.0309,-78.4804],tiles='Stamen Terrain',zoom_start=17)
# folium.GeoJson(parcel_area_url,name='Parcels', style_function=style_function).add_to(m)
# folium.LayerControl().add_to(m)
# m

# # Plot each parcels total, land, and improvement value across all years on 3 line graphs, one for each assessment type
# 
# # Map the same data as above via folium
# 
# # Create time lapse of maps

# In[ ]:




