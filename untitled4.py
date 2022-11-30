import numpy as np 
import pandas as pd
import streamlit as st

pd.set_option('display.max_columns', None) 
pd.set_option('display.max_rows', 66) 

import plotly.express as px
import plotly.offline as pyo
pyo.init_notebook_mode()
import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv("data/FAOSTAT_data_11-24-2020.csv", encoding='cp1252')

df3 = pd.read_csv("data/Environment_Temperature_change_E_All_Data_NOFLAG.csv" , encoding='cp1252')

temp_df =  df3.copy()

#temp_df.info()

#temp_df.isnull().sum()

temp_df = temp_df.rename(columns = {'Area Code':'area_code', 'Area':'area', 'Months Code':'months_code','Months':'months','Element Code':'element_code','Element':'element','Unit':'unit'})

temp_df.drop(temp_df[temp_df.element_code == 6078].index , inplace = True)

#temp_df.head()

temp_df.drop(temp_df[temp_df.element_code == 6078].index , inplace = True)

months = ['January','February','March','April','May','June','July','August','September','October','November','December']
temp_months = temp_df[temp_df['months'].isin(months)]

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

def plot_g():
  plt.figure(figsize=(20,10))
  sns.lineplot(x=temp_months.months.loc[temp_months.element=='Temperature change'],y=temp_months.Y1961.loc[temp_months.element=='Temperature change'], label='Y1961')
  sns.lineplot(x=temp_months.months.loc[temp_months.element=='Temperature change'],y=temp_months.Y1971.loc[temp_months.element=='Temperature change'], label='Y1971')
  sns.lineplot(x=temp_months.months.loc[temp_months.element=='Temperature change'],y=temp_months.Y1981.loc[temp_months.element=='Temperature change'], label='Y1981')
  sns.lineplot(x=temp_months.months.loc[temp_months.element=='Temperature change'],y=temp_months.Y1991.loc[temp_months.element=='Temperature change'], label='Y1991')
  sns.lineplot(x=temp_months.months.loc[temp_months.element=='Temperature change'],y=temp_months.Y2001.loc[temp_months.element=='Temperature change'], label='Y2001')
  sns.lineplot(x=temp_months.months.loc[temp_months.element=='Temperature change'],y=temp_months.Y2010.loc[temp_months.element=='Temperature change'], label='Y2010')
  sns.lineplot(x=temp_months.months.loc[temp_months.element=='Temperature change'],y=temp_months.Y2019.loc[temp_months.element=='Temperature change'], label='Y2019')
  plt.xlabel('months')
  plt.ylabel('Temperature change (C)')
  plt.title('Temperature Change in Worldwide last few decades')
#plot_g()

def plot_g2():
    temp_year = temp_df[(temp_df["months"]=="Meteorological year")]
    temp_year = temp_year.drop(["area_code","months_code","months","element","element_code","unit"],axis=1)
    temp_year = temp_year.T
    temp_year.columns = temp_year.loc['area']
    temp_year.drop('area', inplace = True)
    Continents = temp_year[["Africa","Asia","Europe","Northern America","South America","Australia","Antarctica"]] 
    Continents=Continents.rename(columns={"Northern America":"N_America","South America":"S_America"})
    Continents.reset_index(level=0, inplace=True)
    Continents=Continents.rename(columns={"index":"Year"})
    idx = Continents.columns[1:].tolist()

    fig = px.line(Continents, x=Continents.Year, y=Continents.columns[1:],
                title='Temperature in °C over countries', width=1500)

    fig.update_layout(
        updatemenus=[
            dict(
                active=0,
                buttons=list([dict(label="None",
                        method="update",
                        args=[{"visible": [True for _ in range(186)]},
                            {"title": "Temperature in °C over continents",
                                "annotations": []}])]) + list([
                    dict(label=f"{j}",
                        method="update",
                        args=[{"visible": [True if i==idx else False for i in range(186)]},
                            {"title": f"{j}",
                                "annotations": []}]) for idx,j in enumerate(Continents.columns[1:])])
                )])

    st.plotly_chart(fig, use_container_width=True)

temp = temp_df.melt(id_vars=['area_code','area','months','months_code', 'element','element_code',
       'unit'],var_name='Year', value_name='temperature')
temp = temp.drop(columns = ['area_code', 'months_code',  'element_code'])
temp = temp[temp['months'] == 'Meteorological year']

Top_countries = temp.groupby('area',).sum().sort_values('temperature', ascending=False)[:10].reset_index()['area']

Top_countries= (Top_countries).to_frame(name="Countries")
