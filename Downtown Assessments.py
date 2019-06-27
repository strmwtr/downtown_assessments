#!/usr/bin/env python
# coding: utf-8

#Import pandas module
import pandas as pd 
import requests
import folium

#Path to the .xls retrieve from the GIS Viewer
f = r'./data/pin_exp.xls'
#Create a dataframe that reads the .xls file
df = pd.read_excel(f)

#Identify all rows in df where MULTIPIN column is not equal to 1
not_multipin = df['MULTIPIN'] != 1

#Create a new dataframe that only contains the rows identified in not_multipin
df = df[not_multipin]

# ## Access json file for parcel areas
formatted_gpins = [str(x) for x in df['GPIN'].unique()]
formatted_gpins = formatted_gpins
formatted_gpins = ','.join(formatted_gpins)

parcel_area_url = f"https://gisweb.charlottesville.org/arcgis/rest/services/OpenData_1/MapServer/43/query?where=GPIN%20in%20({formatted_gpins})&outFields=*&outSR=4326&f=json"

#Preparing annual assessment data
formatted_pins = [f'%27{x}%27' for x in df['PIN'].unique()]
formatted_pins = ','.join(formatted_pins)

assessment_url = f"https://gisweb.charlottesville.org/arcgis/rest/services/OpenData_2/MapServer/2/query?where=UPPER(ParcelNumber)%20in%20({formatted_pins})%20&outFields=ParcelNumber,LandValue,ImprovementValue,TotalValue,TaxYear&outSR=4326&f=json"
assessment_request = requests.get(assessment_url)
assessment_json = assessment_request.json()

# Create data series based on features
df1 = pd.DataFrame(assessment_json['features'])

# Create a data frame based on series data
assessments = pd.DataFrame([x for x in df1['attributes']], dtype = 'object')
assessments = assessments.astype({'TaxYear': 'int64', 'ImprovementValue': 'int64','LandValue': 'int64','TotalValue': 'int64', 'ParcelNumber': 'str'})

# Create data frame from df that holds PIN and GPIN. Will be used to joined assessments, so that parcel area can be joined with assessments
df_key = pd.DataFrame(df[['PIN','GPIN']], dtype = 'str')

# Join assessments and df_key
d = pd.merge(assessments, df_key, how='inner', left_on=['ParcelNumber'], right_on=['PIN'])

# Step 3: Analyze

#Create data frame of assessed values for all parcels by specified year
year_min = int(d['TaxYear'].min())
year_max = int(d['TaxYear'].max())

#year_col = [x for x in range(year_min, year_max + 1)]
#total_val_col = [d['TotalValue'][d['TaxYear'] == x].mean() for x in range(year_min, year_max + 1)]
#mean_vals = pd.DataFrame([[year_col, total_val_col]], columns = ['TaxYear','TotalValue'], dtype = 'int64')
#mean_vals = pd.DataFrame(columns = ['TotalValue', 'ImprovementValue', 'LandValue', 'TaxYear'])

#Plot single parcel by tax year vs total value
x = d['ParcelNumber'].str.contains('2800371C0')
y = d[x].sort_values('TaxYear')
y.plot(x='TaxYear', y='TotalValue', figsize=(15,10), grid=True)



