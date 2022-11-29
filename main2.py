import base64
import pandas as pd
from Climatevizv2 import *
import plotly.express as px
import pandas as pd
import numpy as np

import pandas as pd
import streamlit as st
from prophet import Prophet
import cufflinks as cf
import plotly.express as px
import plotly.graph_objects as go
from prophet.plot import plot_plotly

import matplotlib.pyplot as plt
from matplotlib import dates
from datetime import datetime
from matplotlib import rcParams
from API import owm
from pyowm.commons.exceptions import NotFoundError


from neuralprophet import NeuralProphet # For forecasting
import datetime, json # For some other ops
from statsmodels.tsa.stattools import acf # For acf plotting

####
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
st.set_page_config(layout="wide")

# loading data and caching
data = load_data("data/Environment_Temperature_change_E_All_Data_NOFLAG.csv")

# Sidebar label
st.sidebar.title("Display options")

#Selecting visualization paths
viz_opt = st.sidebar.selectbox(label="Select what you wish to see!", options=["None","Land temperature anomaly comparisons", "CO2 Emmissions","Temperature Variation","Weather Forecaster", "Analysis"])

if viz_opt == "Land temperature anomaly comparisons":
    countries = st.sidebar.multiselect("Select countries to visualize (Max 3 recommended)", data["area"].unique()) # displaying list of available countries , default option is an empty list for flow control
    
    if len(countries) > 1:
        years = multic_year_range(data, countries) # extracting available year range for the country selected
        low, high = st.sidebar.slider("Select years from the available period", min_value = min(years), max_value = max(years), value = (min(years), max(years))) # creating slider to retrieve desired period based on available years
        period_list = list(data["months"].unique())
        period_list.append("")
        period = st.sidebar.selectbox("Period to visualize", period_list, index = (len(period_list) - 1)) # period to display from slider , default option is an empty string for flow control
        
        if period != "":

            parsed_data = config_data_multi(data, countries, low, high, period) # extracting countries specific data based on current parameters
            fig = plot_multic(parsed_data, countries, low, high) # creating figure

            # Decisions for responsiveness and better text representation
            if len(countries) < 4: 
                st.header(f"Visualizing **LAND** temperature anomalies for **{' & '.join(countries)}**")
                st.subheader(f"Period: **{low}**-**{high}**, **{period}**")
                col1, col2 = st.columns([5,1]) # creating display sections
                with col1:
                    st.write("If the plot is too small, click the expander button at the top-right of the chart")
                    st.plotly_chart(fig, use_container_width = True) # instantiating figure and sizing to container

                # discovering max and mins before finally passing the data
                filt_max = parsed_data.iloc[:,:len(countries)].max() ## creating max value filters
                filt_min = parsed_data.iloc[:,:len(countries)].min() ## creating min value filters

                max_data = parsed_data[filt_max.idxmax()] ## for better parsing of the data, retrieve the idxmax and slice a copy
                min_data = parsed_data[filt_min.idxmin()] ## for better parsing of the data, retrieve the idmxin and slice a copy

                with col2:
                    st.write("**Max** temperature anomaly in selected data")
                    st.table(max_data[max_data == filt_max.max()])
                    
                    st.write("**Min** temperature anomaly in selected data")
                    st.table(min_data[min_data == filt_min.min()])

                # hold data at the bottom of the app
                with st.expander(label = "Click to see data", expanded = False):
                    st.dataframe(parsed_data.iloc[:,:len(countries)]) # slicing away the color columns because for some reason i can't get rid of them in other way...
                
                # section below is related to download. Workaround found at 'awesome streamlit' https://discuss.streamlit.io/t/file-download-workaround-added-to-awesome-streamlit-org/1244
                df = parsed_data.iloc[:,len(countries)]
                csv = df.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
                href = f'<a href="data:file/csv;base64,{b64}">Download CSV File</a> (***IMPORTANT***: right-click and save as <your_name>.csv)'
                st.markdown(href, unsafe_allow_html=True)

            elif len(countries) >= 4:
                st.header(f"Visualizing **LAND** temperature anomalies for **many countries!**")
                st.subheader(f"Period: **{low}**-**{high}**, **{period}**")
                col1, col2 = st.columns([5,1]) # creating display sections
                with col1:
                    st.write("If the plot is too small, click the expander button at the top-right of the chart")
                    st.plotly_chart(fig, use_container_width = True) # instantiating figure and sizing to container
            
                # hold data at the bottom of the app
                with st.expander(label = "Click to see data", expanded = False):
                    st.dataframe(parsed_data.iloc[:,:len(countries)]) # slicing away the color columns because for some reason i can't get rid of them in other way...

                with col2:
                    st.write("**Max** temperature anomaly in selected data")
                    st.table(max_data[max_data == filt_max.max()])
                    
                    st.write("**Min** temperature anomaly in selected data")
                    st.table(min_data[min_data == filt_min.min()])

elif viz_opt == "One country":
    country_list = list(data["area"].unique())
    country_list.append("")
    country = st.sidebar.selectbox("Select a country to visualize", country_list, index= (len(country_list) - 1)) # displaying list of available countries, default option is an empty string for flow control
    
    # placeholder decision used for responsiveness and easier visualization 
    if country != "": 
        years = onec_year_range(data, country) # extracting available year range for the country selected
        low, high = st.sidebar.slider("Select years from the available period", min_value = min(years), max_value = max(years), value = (min(years), max(years))) # creating slider to retrieve desired period based on available years
        period_list = list(data["months"].unique())
        period_list.append("")
        period = st.sidebar.selectbox("Select period to visualize", period_list, index = (len(period_list) - 1)) # period to display from slider , default option is an empty string for flow control
        
        # placeholder decision used for responsiveness and easier visualization 
        if period != "": 
            parsed_data = config_data_onec(data, country, low, high, period) # extracting country specific data based on current parameters
            # extracting max and min indexes
            idxmax = parsed_data["Temperature Anomaly"].idxmax()
            idxmin = parsed_data["Temperature Anomaly"].idxmin()
            st.header(f"Visualizing **LAND** temperature anomalies for **{country}**")
            fig = plot_onec(parsed_data, low, high) # creating figure

            # creating display sections for better visualization. The syntax means the "portions" of the page width each col takes.
            col1, col2 = st.columns([5,1])
            
            # plot section
            with col1:
                st.plotly_chart(fig, use_container_width = True) # instantiating figure and sizing to container

            # small tables section
            with col2: 
                st.write("Year of **max** temperature anomaly")
                if isinstance(parsed_data.loc[idxmax]["Temperature Anomaly"], np.float64) == True:
                    st.table(pd.DataFrame({parsed_data.loc[idxmax]["Year"]:parsed_data.loc[idxmax]["Temperature Anomaly"]}, index = ["Temp. Anomaly"]))
                else:
                    st.table(parsed_data.loc[idxmax]["Temperature Anomaly"])

                st.write("Year of **min** temperature anomaly")
                if isinstance(parsed_data.loc[idxmin]["Temperature Anomaly"], np.float64) == True:
                    st.table(pd.DataFrame({parsed_data.loc[idxmin]["Year"]:parsed_data.loc[idxmin]["Temperature Anomaly"]}, index = ["Temp. Anomaly"]))
                else:
                    st.table(parsed_data.loc[idxmin]["Temperature Anomaly"])
            
            # hold data at the bottom of the app
            with st.expander(label = "Click to see data", expanded = False):
                st.dataframe(parsed_data.set_index("Year")["Temperature Anomaly"])
            
          
            #section below is related to download. Workaround found at 'awesome streamlit' https://discuss.streamlit.io/t/file-download-workaround-added-to-awesome-streamlit-org/1244
            #df = parsed_data.set_index("Year")
            #csv = df.to_csv(index=False)
            #b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
            #href = f'<a href="data:file/csv;base64,{b64}">Download CSV File</a> (***IMPORTANT***: right-click and save as <your_name>.csv)'
            #st.markdown(href, unsafe_allow_html=True)


elif viz_opt == "CO2 Emmissions":
    st.title("CO2 Emmissions")
    @st.cache
    def get_data(url):
        return pd.read_csv(url)
    @st.cache
    def get_co2_data(): 
        # OWID Data on CO2 and Greenhouse Gas Emissions
        # Creative Commons BY license
        url = 'https://github.com/owid/co2-data/raw/master/owid-co2-data.csv'
        return get_data(url)

    df_co2= get_co2_data()

    st.markdown("""
    # World CO2 emissions
    __The graphs below show the CO2 emissions per capita for the entire 
    world and individual countries over time.
    Select a year with the slider in the left-hand graph and countries 
    from the drop down menu in the other one.__
    __Scroll down to see charts demonstrating the correlation between 
    the level of CO2 and global warming.__
    __Hover over any of the charts to see more detail__
    ---
    """)

    col2, space2, col3 = st.columns((10,1,10))

    with col2:
        year = st.slider('Select year',1750,2020)
        fig = px.choropleth(df_co2[df_co2['year']==year], locations="iso_code",
                            color="co2_per_capita",
                            hover_name="country",
                            range_color=(0,25),
                            color_continuous_scale=px.colors.sequential.Reds)
        st.plotly_chart(fig, use_container_width=True)

    with col3: 
        default_countries = ['World','United States','United Kingdom','EU-27','China', 'Australia']
        countries = df_co2['country'].unique()

        selected_countries = st.multiselect('Select country or group',countries,default_countries)

        df3 = df_co2.query('country in @selected_countries' )

        fig2 = px.line(df3,"year","co2_per_capita",color="country")

        st.plotly_chart(fig2, use_container_width=True)

        
    # st.dataframe(get_warming_data())

    col4, space3, col5,space4,col6 = st.columns((10,1,10,1,10))
    with col4:
        st.markdown("""
        ## Corelation between CO2 emission and global warming
        This can be seen in the adjacent graphs. 
        
        The first show temperature
        has changed since 1850 and you can see that temperatures begin 
        to rise after the beginning of the twentieth century but there 
        is a sharp upturn in that rise about mid-way through (the scatter
        points are the actual figures for each year and the line is a 
        lowess smoothing of those points so that we can more easily see 
        the trend).
        The second graph shows the rise in total CO2 emissions over the 
        same period and a similar trend can be seen with a sharp rise in 
        emissions mid-twentieth century.
        """)
    with col5:
        st.subheader("Total world CO2 emissions")
        fig4 = px.line(df3.query("country == 'World' and year >= 1850"),"year","co2")
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown('__Data Source:__ _Our World in Data CC BY_')

elif viz_opt == "Temperature Variation":   #Aparna pls change language :(((  
    init_notebook_mode(connected=True)
    cf.go_offline()
    # Título
    st.title("Estudo da variação da temperatura planetária")
    st.write("Criado por Diego Batista, Rogério Chinen, Tsuyoshi Fukuda")

    # Avisos importantes
    st.markdown("**Avisos importantes:**")
    ## Aviso 1
    st.write(f"As análises abaixo foram geradas a partir do conjunto de dados **'Climate Change: Earth Surface Temperature Data'**. Para mais informações, acesse:")
    link_kaggle = '[Climate Change: Earth Surface Temperature Data](https://www.kaggle.com/berkeleyearth/climate-change-earth-surface-temperature-data)'
    st.markdown(link_kaggle, unsafe_allow_html=True)
    ## Aviso 2
    st.write("Informações sobre continentes e códigos dos países foram obtidas no DataHub.io, postado por **JohnSnowLabs**. Para mais informações, acesse:")
    link_datahub = "[Country and Continent Codes List](https://datahub.io/JohnSnowLabs/country-and-continent-codes-list#data)"
    st.markdown(link_datahub, unsafe_allow_html=True)
    ##############################################################################################################

    # Temperatura média na terra e oceano
    st.subheader("Variações na temperatura global ao longo dos anos")
    ## dataframes
    def dataframe_datetime(df):
            df.dt = pd.to_datetime(df.dt)
            return df

    df_land = dataframe_datetime(pd.read_csv("https://raw.githubusercontent.com/tvfukuda/LC-mod2-proj2/main/df_land.csv"))
    df_ocean = dataframe_datetime(pd.read_csv("https://raw.githubusercontent.com/tvfukuda/LC-mod2-proj2/main/df_ocean.csv"))

    ## Plotagem dos gráficos
    def plot_land(df_land):

            # formatação do hover
            text_1 = [f'Ano: {x}<br>Temperatura: {str(round(y,1)).replace(".", ",")}°C'
                for x, y in zip(df_land.dt.dt.year.tolist(),
                            df_land.LandAverageTemperature.tolist())]

            text_2 = [f'Ano: {x}<br>Temperatura: {str(round(y,1)).replace(".", ",")}°C'
                for x, y in zip(df_land.dt.dt.year.tolist(),
                            df_land.LandMovingAverageTemperature12.tolist())]

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_land["dt"], y=round(df_land["LandAverageTemperature"],1), name='Temperatura média mensal', mode="markers", marker=dict(size = 3.5), opacity = 0.5, text=text_1, hoverinfo="text"))

            fig.add_trace(go.Scatter(
                x=df_land['dt'], y=round(df_land["LandMovingAverageTemperature12"],1), name='Temperatura média anual móvel', text=text_2, hoverinfo="text"))

            fig.layout.update(title_text='Temperatura global média dos continentes',
                                xaxis_rangeslider_visible=True)

            fig.layout.update(
                xaxis=dict(
                        showline=True,
                        showgrid=False,
                        showticklabels=True,
                        linecolor='rgb(0, 0, 0)',
                        linewidth=2,
                        ticks='outside',
                        title_text = "Ano",
                        tickfont=dict(
                            family='Arial',
                            size=12,
                            color='rgb(82,82,82)')
                    ),
                yaxis=dict(
                        showline=True,
                        showgrid=False,
                        zeroline=True,
                        showticklabels=True,
                        ticks='outside',
                        title_text = "Temperatura em °C",
                        linecolor='rgb(0, 0, 0)',
                        linewidth=2,
                ),
                legend=dict(
                    orientation= "h",
                    title=dict(
                        font=dict(
                            color="#000000",
                            family="arial")),
                    x = 0.08, # move a legenda horizontalmente
                    y=1.05 # move a legenda verticalmente
            ),
                margin=dict( # altera as margens do gráfico
                autoexpand=False,
                r=20,
                l=100,
                t=100,
                b=80
            ),
                plot_bgcolor='rgb(255,255,255)',  # plot_bgcolor='white'   
                
                # alteração das cores das linhas do gráfico
                colorway=["#ff7f0e", "#162dc4"], # cores dos gráficos
            )
            st.plotly_chart(fig, use_container_width=True)

    def plot_ocean(df_ocean):
            # formatação do hover
            text_1 = [f'Ano: {x}<br>Temperatura: {str(round(y,1)).replace(".", ",")}°C'
                for x, y in zip(df_ocean.dt.dt.year.tolist(),
                            df_ocean.LandAndOceanAverageTemperature.tolist())]

            text_2 = [f'Ano: {x}<br>Temperatura: {str(round(y,1)).replace(".", ",")}°C'
                for x, y in zip(df_ocean.dt.dt.year.tolist(),
                            df_ocean.LandAndOceanMovingAverageTemperature12.tolist())]

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_ocean['dt'], y=round(df_ocean['LandAndOceanAverageTemperature'],1), name='Temperatura média mensal', mode="markers", marker=dict(size = 3.5), opacity = 0.5, text=text_1, hoverinfo="text"))

            fig.add_trace(go.Scatter(
                x=df_ocean['dt'], y=round(df_ocean['LandAndOceanMovingAverageTemperature12'],1), name='Temperatura média anual móvel', text=text_2, hoverinfo="text"))

            fig.layout.update(title_text='Temperatura global média dos continentes e oceanos',
                                xaxis_rangeslider_visible=True)

            fig.layout.update(
                xaxis=dict(
                        showline=True,
                        showgrid=False,
                        showticklabels=True,
                        linecolor='rgb(0, 0, 0)',
                        linewidth=2,
                        ticks='outside',
                        title_text = "Ano",
                        tickfont=dict(
                            family='Arial',
                            size=12,
                            color='rgb(82,82,82)'),
                    ),
                yaxis=dict(
                        showline=True,
                        showgrid=False,
                        zeroline=True,
                        showticklabels=True,
                        ticks='outside',
                        title_text = "Temperatura em °C",
                        linecolor='rgb(0, 0, 0)',
                        linewidth=2
                    ),
                legend=dict(
                    orientation= "h",
                    title=dict(
                        font=dict(
                            color="#000000",
                            family="arial")),
                    x = 0.08, # move a legenda horizontalmente
                    y=1.05 # move a legenda verticalmente
            ),
                margin=dict( # altera as margens do gráfico
                autoexpand=False,
                r=20,
                l=100,
                t=100,
                b=80
            ),
                plot_bgcolor='rgb(255,255,255)',  # plot_bgcolor='white'   
                
                # alteração das cores das linhas do gráfico
                colorway=["#162dc4", "#cf2c17"], # cores dos gráficos
            )
            st.plotly_chart(fig, use_container_width=True)

        
    # checknox
    is_land = st.radio("Escolha abaixo o gráfico das temperaturas médias globais para avaliação", ("Continentes", "Continentes + Oceanos"))
    #st.write(is_land)

    if is_land == "Continentes":
        plot_land(df_land)
    elif is_land == "Continentes + Oceanos":
        plot_ocean(df_ocean)
    else:
        pass

    ##############################################################################################################

    # temperatura continentes
    st.subheader("Temperaturas médias nos continentes")

    # Temperatura das cidades de 1901 a 2013
    df_city = pd.read_csv("https://raw.githubusercontent.com/tvfukuda/LC-mod2-proj2/main/Dataset_limpo_reduzido.csv")


    def continentes(df_continent):
            # Gerando os modelos para o hover
            text = [f'Continente: {x}<br>Ano: {y}<br>Temperatura: {str(round(z,2)).replace(".", ",")}°C'
                    for x, y, z in zip(df_continent.Continent_Name.tolist(), df_continent.Year.tolist(),
                                    df_continent.AverageTemperature.tolist())]

            # Gerando a visualização gráfica
            fig = go.Figure()

            # criando o plot para a África
            fig.add_trace(go.Scatter(x=df_continent.Year[df_continent.Continent_Name == "Africa"],
                                    y=df_continent.AverageTemperature[df_continent.Continent_Name == "Africa"],
                                    mode="lines+markers", name="Africa", text=text[:12], hoverinfo='text'))

            # Criando o plot para a Ásia
            fig.add_trace(go.Scatter(x=df_continent.Year[df_continent.Continent_Name == "Asia"],
                                    y=df_continent.AverageTemperature[df_continent.Continent_Name == "Asia"],
                                    mode="lines+markers", name="Asia", text=text[12:24], hoverinfo='text'))

            # Criando o plot para a Europa
            fig.add_trace(go.Scatter(x=df_continent.Year[df_continent.Continent_Name == "Europe"],
                                    y=df_continent.AverageTemperature[df_continent.Continent_Name == "Europe"],
                                    mode="lines+markers", name="Europa", text=text[24:36], hoverinfo='text'))

            # Criando o plot para a Oceania
            fig.add_trace(go.Scatter(x=df_continent.Year[df_continent.Continent_Name == "Oceania"],
                                    y=df_continent.AverageTemperature[df_continent.Continent_Name == "Oceania"],
                                    mode="lines+markers", name="Oceania", text=text[48:60], hoverinfo='text'))

            # Criando o plot para a América do Norte e Central
            fig.add_trace(go.Scatter(x=df_continent.Year[df_continent.Continent_Name == "North America"],
                                    y=df_continent.AverageTemperature[df_continent.Continent_Name == "North America"],
                                    mode="lines+markers", name="América do Norte", text=text[36:48], hoverinfo='text'))

            # Criando o plot para a América do Sul
            fig.add_trace(go.Scatter(x=df_continent.Year[df_continent.Continent_Name == "South America"],
                                    y=df_continent.AverageTemperature[df_continent.Continent_Name == "South America"],
                                    mode="lines+markers", name="América do Sul", text=text[60:72], hoverinfo='text'))

            ########################
            #fig.update_layout(title_text = "Variação da temperatura dos continentes por década entre 1901 e 2013")
            fig.update_layout(
                title=dict(
                    text = "Variação da temperatura por continente entre 1901 e 2013",
                    font=dict(
                        #color="#000000",
                        family="arial",
                    size = 18
                    ),
                x = 0.5),
            # trabalhando a legenda
            legend=dict(
                font=dict(
                    #color="#000000",
                    family="arial",
                    size = 10),
                
                orientation= "h",
                title=dict(
                    font=dict(
                        #color="#000000",
                        family="arial")),
                x=0.04, # move a legenda horizontalmente
                y=-0.2 # move a legenda verticalmente
            ),
            
            font=dict( # fonte geral do gráfico
                #color="#000000",
                family="arial",
                size=14
            ),
            
            separators=",", # separador dos decimais nas palhetas
                
            margin=dict( # altera as margens do gráfico
                autoexpand=False,
                r=50,
                l=70,
                t=100,
                b=130
            ),
            # alteração do fundo do gráfico
            plot_bgcolor="RGB(255, 255, 255)",
            
            # alteração das cores das linhas do gráfico
            colorway=["#ff7f0e", "#f0e516", "#4e51e6", "#d60b30", "#0f5410", "#710e9c"], # cores dos gráficos
            
            # alterações nos eixos x e y
            xaxis=dict(
                    showline=True,
                    showticklabels=True,
                    linecolor='rgb(204, 204, 204)',
                    linewidth=1,
                    ticks='outside',
                    title_text = "Décadas",
                    title_font = {"size": 15},
                    title_standoff = 60),
                    #rangeslider = dict(visible = True)
            yaxis=dict(
                    showline=True,
                    gridcolor='#ebebf0',
                    title_text = "Temperatura em °C",
                    title_font = {"size": 15}),
            
            #hovermode = "closest"
            )
            fig.update_yaxes(
                range=[5,25],  # sets the range of xaxis
                #constrain="domain"
            )
            st.plotly_chart(fig, use_container_width=True)

    continentes(df_city)
    # charts para a variação da temperatura
    st.write("**Variações das temperaturas médias por continente** (Cálculos a partir das temperaturas médias nas cidades em cada continente entre 1901 e 2013).")

    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    def variacao_temp(df, continent):
        valor_min = df[df.Continent_Name == continent]["AverageTemperature"].min()
        valor_max = df[df.Continent_Name == continent]["AverageTemperature"].max()
        return valor_min, valor_max

    # África
    v_min, v_max = variacao_temp(df_city, "Africa")
    col1.metric('África', v_max, round((v_max-v_min), 1))

    # América do Sul
    v_min, v_max = variacao_temp(df_city, "South America")
    col2.metric('América do Sul', v_max, round((v_max-v_min), 1))

    # Ásia
    v_min, v_max = variacao_temp(df_city, "Asia")
    col3.metric('Ásia', v_max, round((v_max-v_min), 1))

    # América do Norte
    v_min, v_max = variacao_temp(df_city, "North America")
    col4.metric('América do Norte', v_max, round((v_max-v_min), 1))

    # Oceania
    v_min, v_max = variacao_temp(df_city, "Oceania")
    col5.metric('Oceania', v_max, round((v_max-v_min), 1))

    # Europa
    v_min, v_max = variacao_temp(df_city, "Europe")
    col6.metric('Europa', v_max, round((v_max-v_min), 1))

    ##############################################################################################################

    # Temperaturas por países de escolha
    st.subheader("Comparativo entre países / cidades de interesse")
    by_countries = pd.read_csv("https://raw.githubusercontent.com/tvfukuda/LC-mod2-proj2/main/research_countries.csv")
    by_cities = pd.read_csv("https://raw.githubusercontent.com/tvfukuda/LC-mod2-proj2/main/by_cities.csv")

    is_countries = st.radio("Deseja comparar países ou cidades entre si?", ("Países", "Cidades"))

    if is_countries == "Países":
        countries = st.multiselect('Selecione o(s) país(es)', by_countries.Country.unique().tolist(), ['Brazil', 'Denmark'])

        marcar_tudo = st.checkbox('Selecionar todos os países da lista? (Não recomendado)')

        def research_by_country(df, countries, marcar_tudo):
            if marcar_tudo:
                df = df[df.Country.isin(df.Country.unique().tolist())]
                fig = px.line(
                    data_frame=df,
                    x = "Year",
                    y = "AverageTemperature",
                    color = "Country",
                    markers = True,
                    title = "Evolução da temperatura médias nos países selecionados",
                    labels={"AverageTemperature": f"Temperatura média em °C",
                            "Year": "Década",
                            "Country": "País"})
                st.plotly_chart(fig, use_container_width=True)
            else:
                df = df[df.Country.isin(countries)]
                fig = px.line(
                    data_frame=df,
                    x = "Year",
                    y = "AverageTemperature",
                    color = "Country",
                    markers = True,
                    title = "Evolução da temperatura médias nos países selecionados",
                    labels={"AverageTemperature": f"Temperatura média em °C",
                            "Year": "Década",
                            "Country": "País"})

                st.plotly_chart(fig, use_container_width=True)

        # chamando a função para exibição
        if st.button("Pronto"):
            research_by_country(by_countries, countries, marcar_tudo)

    else:
        cities = st.multiselect('Selecione a(s) cidade(s). Digite "País, cidade"', by_cities.City_Country.unique().tolist(), ['Afghanistan, Baglan', 'Brazil, São Paulo'])
            
        def research_by_city(df, cities):
            countries = [string.split(",")[0].strip() for string in cities]
            cities = [string.split(",")[1].strip() for string in cities]
            df = df[(df.Country.isin(countries)) & (df.City.isin(cities))]
            fig = px.line(
                data_frame=df,
                x = "Year",
                y = "AverageTemperature",
                color = "City",
                markers = True,
                title = "Evolução da temperatura médias nas cidades selecionadas",
                labels={"AverageTemperature": "Temperatura média em °C",
                        "Year": "Década",
                        "City": "Cidade"})

            st.plotly_chart(fig, use_container_width=True)

        # chamando a função para exibição
        if st.button("Pronto"):
            research_by_city(by_cities, cities)
        
        
    ##############################################################################################################

    st.subheader("Predição da variação da temperatura nos próximos anos")
    periodo = st.slider('Escolha quantos anos serão utilizados na previsão:', 0, 100, 10)    

    def predicao(df, periodo):
        df = df[['dt', 'LandAndOceanMovingAverageTemperature12']]
        df.rename(columns={'dt': 'ds', 'LandAndOceanMovingAverageTemperature12': 'y'}, inplace = True)
        m = Prophet()
        m.fit(df)
        future = m.make_future_dataframe(periods=(periodo * 365))
        forecast = m.predict(future)
        return m, forecast

    if st.button("Vai"):
        m, forecast = predicao(df_ocean, periodo)
        fig_1 = plot_plotly(m, forecast, xlabel="Anos", ylabel="Temperatura média em °C")
        st.plotly_chart(fig_1, use_container_width=True)

        st.write("**Métricas da predição**")
        fig_2 = m.plot_components(forecast)
        st.write(fig_2)


elif viz_opt == "Weather Forecaster":

    # Streamlit Display
    st.title(" WEATHER FORECASTER ")


    st.header("Enter the name of City and Select Temperature Unit")
    place = st.text_input("NAME OF THE CITY  ", " ")
    unit = st.selectbox(" SELECT TEMPERATURE UNIT 🌡 ", ("Celsius", "Fahrenheit"))
    g_type = st.selectbox("SELECT GRAPH TYPE ", ("Line Graph", "Bar Graph"))
    b = st.button("SUBMIT")

    # To deceive error of pyplot global warning
    st.set_option('deprecation.showPyplotGlobalUse', False)

    def plot_line(days, min_t, max_t):
        days = dates.date2num(days)
        rcParams['figure.figsize'] = 6, 4
        plt.plot(days, max_t, color='black', linestyle='solid', linewidth=1, marker='o', markerfacecolor='green',
                markersize=7)
        plt.plot(days, min_t, color='black', linestyle='solid', linewidth=1, marker='o', markerfacecolor='blue',
                markersize=7)
        plt.ylim(min(min_t) - 4, max(max_t) + 4)
        plt.xticks(days)
        x_y_axis = plt.gca()
        xaxis_format = dates.DateFormatter('%d/%m')

        x_y_axis.xaxis.set_major_formatter(xaxis_format)
        plt.grid(True, color='brown')
        plt.legend(["Maximum Temperature", "Minimum Temperature"], loc=1)
        plt.xlabel('Dates(dd/mm)')
        plt.ylabel('Temperature')
        plt.title('6-Day Weather Forecast')

        for i in range(5):
            plt.text(days[i], min_t[i] - 1.5, min_t[i],
                    horizontalalignment='center',
                    verticalalignment='bottom',
                    color='black')
        for i in range(5):
            plt.text(days[i], max_t[i] + 0.5, max_t[i],
                    horizontalalignment='center',
                    verticalalignment='bottom',
                    color='black')
        # plt.show()
        # plt.savefig('figure_line.png')
        st.pyplot()
        plt.clf()


    def plot_bars(days, min_t, max_t):
        # print(days)
        days = dates.date2num(days)
        rcParams['figure.figsize'] = 6, 4
        min_temp_bar = plt.bar(days - 0.2, min_t, width=0.4, color='r')
        max_temp_bar = plt.bar(days + 0.2, max_t, width=0.4, color='b')
        plt.xticks(days)
        x_y_axis = plt.gca()
        xaxis_format = dates.DateFormatter('%d/%m')

        x_y_axis.xaxis.set_major_formatter(xaxis_format)
        plt.xlabel('Dates(dd/mm)')
        plt.ylabel('Temperature')
        plt.title('6-Day Weather Forecast')

        for bar_chart in [min_temp_bar, max_temp_bar]:
            for index, bar in enumerate(bar_chart):
                height = bar.get_height()
                xpos = bar.get_x() + bar.get_width() / 2.0
                ypos = height
                label_text = str(int(height))
                plt.text(xpos, ypos, label_text,
                        horizontalalignment='center',
                        verticalalignment='bottom',
                        color='black')
        st.pyplot()
        plt.clf()


    # Main function
    def weather_detail(place, unit, g_type):
        mgr = owm.weather_manager()
        days = []
        dates_2 = []
        min_t = []
        max_t = []
        forecaster = mgr.forecast_at_place(place, '3h')
        forecast = forecaster.forecast
        obs = mgr.weather_at_place(place)
        weather = obs.weather
        temperature = weather.temperature(unit='celsius')['temp']
        if unit == 'Celsius':
            unit_c = 'celsius'
        else:
            unit_c = 'fahrenheit'

        for weather in forecast:
            day = datetime.utcfromtimestamp(weather.reference_time())
            date1 = day.date()
            if date1 not in dates_2:
                dates_2.append(date1)
                min_t.append(None)
                max_t.append(None)
                days.append(date1)
            temperature = weather.temperature(unit_c)['temp']
            if not min_t[-1] or temperature < min_t[-1]:
                min_t[-1] = temperature
            if not max_t[-1] or temperature > max_t[-1]:
                max_t[-1] = temperature

        obs = mgr.weather_at_place(place)
        weather = obs.weather
        st.title(f"Weather at {place[0].upper() + place[1:]} currently: ")
        if unit_c == 'celsius':
            st.write(f"## Temperature: {temperature} °C")
        else:
            st.write(f"## Temperature: {temperature} F")
        st.write(f"## Sky: {weather.detailed_status}")
        st.write(f"## 🌪  Wind Speed: {round(weather.wind(unit='km_hour')['speed'])} km/h")
        st.write(f"### Sunrise Time :     {weather.sunrise_time(timeformat='iso')} GMT")
        st.write(f"### Sunset Time :      {weather.sunset_time(timeformat='iso')} GMT")

        # Expected Temperature Alerts
        st.title("Expected Temperature Changes/Alerts: ")
        if forecaster.will_have_fog():
            st.write("### FOG ALERT!!")
        if forecaster.will_have_rain():
            st.write("### RAIN ALERT!!")
        if forecaster.will_have_storm():
            st.write("### STORM ALERT!!")
        if forecaster.will_have_snow():
            st.write("### SNOW ALERT!!")
        if forecaster.will_have_tornado():
            st.write("### TORNADO ALERT!!")
        if forecaster.will_have_hurricane():
            st.write("### HURRICANE ALERT")
        if forecaster.will_have_clear():
            st.write("### CLEAR WEATHER PREDICTED!!")
        if forecaster.will_have_clouds():
            st.write("### CLOUDY SKIES")

        st.write('                ')
        st.write('                ')

        if g_type == "Line Graph":
            plot_line(days, min_t, max_t)
        elif g_type == "Bar Graph":
            plot_bars(days, min_t, max_t)

        # To give max and min temperature
        i = 0
        st.write(f"# Date :  Max - Min  ({unit})")
        for obj in days:
            ta = (obj.strftime("%d/%m"))
            st.write(f'### ➡️ {ta} :\t   ({max_t[i]} - {min_t[i]})')
            i += 1


    if b:
        if place != "":
            try:
                weather_detail(place, unit, g_type)

            except NotFoundError:
                st.write("Please enter a Valid city name")



if viz_opt == "Analysis":
    
        # Loading and initializing all datasets


        df_global = pd.read_csv('datasets/GlobalTemperatures.csv',parse_dates=['dt'],index_col='dt')
        df_global = df_global[['LandAverageTemperature']]
        df_global.columns = ['AverageTemperature']

        df_countries = pd.read_csv('datasets/GlobalLandTemperaturesByCountry.csv',parse_dates=['dt'],index_col='dt')
        df_countries = df_countries[['AverageTemperature','Country']]

        df_states = pd.read_csv('datasets/GlobalLandTemperaturesByState.csv',parse_dates=['dt'],index_col='dt')
        df_states = df_states[['Country','State','AverageTemperature']]

        month = {1:'Janauary',2:'February',3:'March',4:'April',5:'May',6:'June',7:'July',
                8:'August',9:'September',10:'October',11:'November',12:'December'}




        # This function will take input on Country and State using a Dropdown selectbox from the user and return data on that particular selected country and state.


        def choose_location():
            country = st.selectbox('Select Country :',['All'] + list(df_countries.Country.unique()))
            
            state = st.selectbox('Select State :',['All'] + list(df_states[df_states['Country']==country]['State'].unique()))
            if country == 'All':
                df = df_global
            elif state == 'All':
                df = df_countries[df_countries['Country']==country][['AverageTemperature']]
            else :
                df = df_states[df_states['Country']==country]
                df = df[df['State']==state][['AverageTemperature']]
            
            return df, country, state



        # This Function will impute missing Values with the monthly mean temperatures


        def missing_value_imputer(df):
            monthly_mean = df['AverageTemperature'].groupby(df.index.month).mean().to_dict()
            df['monthly_mean'] = df.index.month.map(monthly_mean)
            df['AverageTemperature'].fillna(df['monthly_mean'],inplace=True)
            return df[['AverageTemperature']]




        # This Function create 2 slider input on frontend to take lower year and upper year from user and filter data based on that year range and return it.


        def time_ranger(df):
            
            min_value = int(df.index.year[0])
            max_value = int(df.index.year[-1])
            
            lower_year = st.slider('Lower Year Range :',min_value=min_value,max_value=max_value,value=min_value)
            upper_year = st.slider('Upper Year Range :',min_value=min_value,max_value=max_value,value=max_value)
            df = df.loc[str(lower_year):str(upper_year)]
            
            return df, lower_year, upper_year





        # This function will show the data and its statistical description on the frontend as well as a download button to download the data as csv


        def show_data(df,country,state,lower_year,upper_year):
            
            str_show = '##### Average Temperature Per Month Data of Country : ' + country + ' and State : ' + state + ' from ' + str(lower_year) + ' to ' + str(upper_year)
            st.markdown(str_show,unsafe_allow_html=True)
            
            df['year'] = df.index.year
            df['month'] = df.index.month.map(month)
            df['Month'] = df['year'].astype(str) + ' , ' + df['month'] 
            
            a,b = st.columns([5.5,5])
            a.markdown('**Average Temperatures Data :**')
            b.markdown('**Statistical Description :**')
            a,b = st.columns([5.5,5])
            a.dataframe(df.set_index('Month')[['AverageTemperature']])
            df = df[['AverageTemperature']]
            b.dataframe(df.describe())
            file = 'monthly_aver_temp_' + country + '_' + state + '_' + str(lower_year) + '_to_' + str(upper_year) + '.csv'
            st.download_button('Download this Data', df.to_csv(),file_name=(file))





        # This function will used to plot an interactive linear chart to visualize the trend based on the rolling window selected. 
        # The rolling window selected from a slider input on frontend by user and based on the selected value, it will apply rolling mean or moving averages on the given data and plot it.  


        def trend_plot(df,country,state,lower_year,upper_year):
            
            text = '''### Trend Plot :
                A trend Graph is a graph that is used to show the trends data over
                a period of time. It describes a functional representation of 
                two variables (x , y). In which the x is the time-dependent 
                variable whereas y is the collected data.
                
                Moving Averages : In statistics, a moving average is a calculation 
                to analyze data points by creating a series of averages of different 
                subsets of the full data set. It is also called a moving mean or 
                rolling mean and is a type of finite impulse response filter. '''
            
            st.markdown(text)
            
            win = st.slider('Rolling Window [ Rolling Window of 1 is Equal to Real Data ] :',min_value=1,max_value=20*12,value=1)
            st.warning('Note : The below Trend Plot depend on the above rolling window. Set rolling window = 1, to get plot on Real Data as per above. Set rolling window > 1 [ 60, 120, 180, 240 Recommended ] to view the trend.')

            str_show='##### Trend Plot on Average Temperature per Month with Moving Average of ' + str(win) + ' Months of Country : ' + country + ' and State : ' + state + ' from ' + str(lower_year) + ' to ' + str(upper_year)
            st.markdown(str_show,unsafe_allow_html=True)
            
            data = df['AverageTemperature'].rolling(window=win).mean()
            fig = px.line(data,title='Trend Plot', width=750, height=550,labels={'dt':'Date','ds':'Date','value':'Average Temperature'})
            fig.update_layout(title={'font_size':25,'x':0.5})
            st.plotly_chart(fig)





        # This function will used to plot an interactive bar chart to visualize the seasonality or monthly mean temperature from january to december on the given data. 


        def seasonal_plot(df,country,state,lower_year,upper_year):
            text = '''### Seasonal Bar Plot :
                
                What Is Seasonality?
                Seasonality is a characteristic of a time series in which the data
                experiences regular and predictable changes that recur every 
                calendar year. Any predictable fluctuation or pattern that recurs 
                or repeats over a one-year period is said to be seasonal. 
                
                A Seasonal Bar Plot is a bar chart similar to a time plot except 
                that the data are plotted against the individual “seasons” or
                "months" in which the data were observed. This plot visualize 
                the seasonality of the given Time Series.
        ''' 
            st.markdown(text)
            
            str_show='##### Seasonal Bar Plot on Average Temperature per Month of Country : ' + country + ' and State : ' + state + ' from ' + str(lower_year) + ' to ' + str(upper_year)
            st.markdown(str_show,unsafe_allow_html=True)
        
            temp = df['AverageTemperature'].groupby(df['AverageTemperature'].index.month).mean()
            temp.index = temp.index.map(month)
            fig = px.bar(temp,color=temp,title='Seasonal Bar Plot', width=750, height=550, labels={'dt':'Date','ds':'Date','value':'Average Temperature'})
            fig.update_layout(title={'font_size':25,'x':0.5})
            st.plotly_chart(fig)





        # This function will used to plot an interactive linear chart to visualize autocorrelation upto 100 lags on the given data 


        def autocorrelation_plot(df,country,state,lower_year,upper_year):
            text = '''### ACF or Autocorrelation plots : 

            Autocorrelation plots are a commonly used tool for checking randomness
            in a data set. This randomness is ascertained by computing 
            autocorrelations for data values at varying time lags. 
            It measures a set of current values against a set of past values and 
            finds whether they correlate.
            It is the correlation of one-time series data to another time series
            data which has a time lag.
            It varies from +1 to -1.
            An autocorrelation of +1 indicates that if time series one increases in
            value the time series 2 also increases in proportion to the change in 
            time series 1.
            An autocorrelation of -1 indicates that if time series one increases in
            value the time series 2 decreases in proportion to the change 
            in time series 1.'''
            
            st.markdown(text)
            str_show='##### Autocorrelation Plot on Average Temperature per Month of Country : ' + country + ' and State : ' + state + ' from ' + str(lower_year) + ' to ' + str(upper_year)
            st.markdown(str_show,unsafe_allow_html=True)
            
            acf_df = pd.DataFrame({'ACF':acf(df['AverageTemperature'],nlags=100,fft=False)})
            acf_df['Upper Level'] = 1.96 / 1.96 / (df.shape[0] ** 0.5 )
            acf_df['Lower Level'] = - 1.96 / 1.96 / (df.shape[0] ** 0.5 )
            fig = px.line(acf_df,title='Autocorrelation Plot',labels={'index':'Lags','value':'Correlation'})
            fig.update_layout(title={'font_size':25,'x':0.5})
            st.plotly_chart(fig)
            




        # This function will train the effing neural prophet model on time the based on the selected historical data and return forcast for next 20 years. This will may take 10 to 15 seconds while training.


        def training_and_forecasting(df):
            
            df = df.reset_index()
            df.columns = ['ds','y']
            

            prophet = NeuralProphet()
            
            st.info('Training. It takes only 10 to 15 seconds. Please Wait....')
            progress = st.progress(0)
            progress.progress(10)
            prophet.fit(df,freq='1m',epochs=10)
            
            progress.progress(100)
            st.success('Training Completed. See results..')
            
            today = str(datetime.datetime.today()).split()[0]
            dates = pd.date_range(today, periods=12*20, freq='1m')
            dates_df = pd.DataFrame({'ds':dates})
            dates_df['y'] = np.nan
            
            def add_dates(x):
                return x + datetime.timedelta(days=1)

            dates_df['ds'] = dates_df['ds'].apply(add_dates)
            dates_pred = prophet.predict(dates_df)
            df = dates_pred.set_index('ds')[['yhat1']]
            df.columns = ['AverageTemperature']
            
            return df



        # This function will show user an abstract about the application.


        
            
            
            
            text = '''
            
        Climate change is undoubtedly one of the biggest problems in the 21st century. Artificial Intelligence methods have recently contributed in the advancement of accurate prediction tools for the estimation and assessment of extreme environmental events and investigation of the climate change time series. The recent advancement in Artificial Intelligence including the novel machine learning and deep learning algorithms as well as soft computing applications have greatly empowered prediction methods. Through this project, we have explore, analyze the global Climatic trend and pattern on temperature component and forecast the future temperature trends using a state of art time series deep learning model. After the research, exploration and analysis on the historical data and modelling, we build and deploy this end to end web solution on the frontend to view and explore historical data as well as future forecasts generated through the deep learning model.
        <br><br>
        ##### <center> Get Historical Data and Analysis </center>

        >Select **"Historical Data and Plotting"** from the menu inside the sidebar. Then you will - <br><br>
        > 1) Get Historical Average Temperatures Per Month upto past 200 years as per the choice of Country, State and Time Range selected.<br><br>
        > 2) Able to download the same data as filtered. <br><br>
        > 3) View the interactive plots to analyze and conclude the Historical Temperature trend, Seasonality and Autocorrelation on the filtered Country, State and Time Range. <br><br>

        ##### <center> Get Future Forecasts and Analysis </center>

        >Select **"Future Data and Plotting"** from the menu inside the sidebar. Then you will - <br><br>
        > 1) Get Predicted Future Average Temperatures Per Month upto next 20 years as per the choice of Country, State and Time Range selected. <br><br>
        > 2) Able to download the same data as filtered. <br><br>
        > 3) View the interactive plots to analyze and conclude the Predicted Future Temperature trend, Seasonality and Autocorrelation on the filtered Country, State and Time Range. <br><br>

        ##### <center> Want to send Message or Feedback Us </center>
        <center>Select <strong>"Feedback Us"</strong> from the menu inside the sidebar.</center> <br><br>

        ##### <center> Want to known about Us </center>
        <center>Select <strong>"About Us"</strong> from the menu inside the sidebar.</center> <br><br>

        '''
            st.markdown(text,unsafe_allow_html=True)
            





        # This will create a page where user can view Historical data, description, plots based on selected country, state and time range


        def show_historical():
            
            st.header('Historical Average Temperature Per Month Data, Description and Visualization')
            
            df, country, state = choose_location()
            
            df = missing_value_imputer(df)
            
            df, lower_year, upper_year = time_ranger(df)
            
            show_data(df,country,state,lower_year,upper_year)
            
            trend_plot(df,country,state,lower_year,upper_year)
        
            seasonal_plot(df,country,state,lower_year,upper_year)
            
            autocorrelation_plot(df,country,state,lower_year,upper_year)
            





        # This will create a page where user can view future data, description, plots based on selected country, state and time range    
            
            
        def show_future():
            
            st.header('Future Average Temperature Per Month Data, Description and Visualization')
            
            df, country, state = choose_location()
            df = missing_value_imputer(df)
            
            df = training_and_forecasting(df)
            
            df, lower_year, upper_year = time_ranger(df) 
            
            
            show_data(df,country,state,lower_year,upper_year)
            
            trend_plot(df,country,state,lower_year,upper_year)
        
            seasonal_plot(df,country,state,lower_year,upper_year)
            
            autocorrelation_plot(df,country,state,lower_year,upper_year)
            
            
        
            
            
        # This will create another page where user can send feedback or message to the team.
            
        
                
                
                
        # This will used to create button using html and css to hyperlink
                
                
        def create_btn(text,link):
                
            btn_css =  '''
            <style>
            a.link-btn {
                color: #fff;
                background: #337ab7;
                display:inline-block;
                border: 1px solid #2e6da4;        
                font: bold 14px Arial, sans-serif;
                text-decoration: none;
                border-radius: 2px;
                padding: 6px 20px;
            }
            a.link-btn:hover {
                background-color: #245582;
                border-color: #1a3e5b;
            }
        </style>'''
            
            btn_html = '<a href={} class="link-btn" target="_blank">{}</a>'.format(link,text)

            return btn_css + btn_html
                


                
        # this will create a sidebar dropdown menu to controls page switching. okay

        res = st.sidebar.radio('You Want : ', ['Historical Data and Plotting' ,'Future Data and Plotting'])

        if res == 'Historical Data and Plotting' :
            show_historical()
        elif res == 'Future Data and Plotting' :
            show_future()

            
        # To hide streamlit default menu and footer
        hide_streamlit_style = """
                    <style>
                    #MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                    </style>
                    """
        st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
        

else:
    # Display at start
    st.title("Climate Change Dashboard currently displaying land temperature anomalies!")
    st.subheader('''Land temperature anomaly is defined as: *"The departure from the average temperature, positive or negative, over a certain period (day, week, month or year)"* ''')
    st.subheader('''To start exploring the data, please use the sidebar on the left side!''')
