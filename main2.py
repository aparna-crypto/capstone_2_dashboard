import base64
import pandas as pd
from Climatevizv2 import *
import plotly.express as px
import pandas as pd
import numpy as np


st.set_page_config(layout="wide")

# loading data and caching
data = load_data("data/Environment_Temperature_change_E_All_Data_NOFLAG.csv")

# Sidebar label
st.sidebar.title("Display options")

#Selecting visualization paths
viz_opt = st.sidebar.selectbox(label="Select what you wish to see!", options=["None","One country", "Multiple countries", "CO2 Emmissions"])

if viz_opt == "Multiple countries":
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


else:
    # Display at start
    st.title("Climate Change Dashboard currently displaying land temperature anomalies!")
    st.subheader('''Land temperature anomaly is defined as: *"The departure from the average temperature, positive or negative, over a certain period (day, week, month or year)"* ''')
    st.subheader('''To start exploring the data, please use the sidebar on the left side!''')
