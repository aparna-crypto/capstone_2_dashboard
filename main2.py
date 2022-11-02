import base64
import pandas as pd
from Climatevizv2 import *

st.set_page_config(layout="wide")

# loading data and caching
data = load_data("data/Environment_Temperature_change_E_All_Data_NOFLAG.csv")

# Sidebar label
st.sidebar.title("Display options")

#Selecting visualization paths
viz_opt = st.sidebar.selectbox(label="Select what you wish to see!", options=["None","One country", "Multiple countries"])

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

            if len(countries) < 4: # Decisions for responsiveness and better text representation
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
    
    if country != "": # placeholder decision used for responsiveness and easier visualization 
        years = onec_year_range(data, country) # extracting available year range for the country selected
        low, high = st.sidebar.slider("Select years from the available period", min_value = min(years), max_value = max(years), value = (min(years), max(years))) # creating slider to retrieve desired period based on available years
        period_list = list(data["months"].unique())
        period_list.append("")
        period = st.sidebar.selectbox("Select period to visualize", period_list, index = (len(period_list) - 1)) # period to display from slider , default option is an empty string for flow control
        
        if period != "": # placeholder decision used for responsiveness and easier visualization 
            parsed_data = config_data_onec(data, country, low, high, period) # extracting country specific data based on current parameters
            # extracting max and min indexes
            idxmax = parsed_data["Temperature Anomaly"].idxmax()
            idxmin = parsed_data["Temperature Anomaly"].idxmin()
            st.header(f"Visualizing **LAND** temperature anomalies for **{country}**")
            fig = plot_onec(parsed_data, low, high) # creating figure

            col1, col2 = st.columns([5,1]) # creating display sections for better visualization. The syntax means the "portions" of the page width each col takes.

            with col1: # plot section
                st.plotly_chart(fig, use_container_width = True) # instantiating figure and sizing to container

            with col2: # small tables section
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
            
else:
    # Display at start
    st.title("Climate Change Dashboard currently displaying land temperature anomalies!")
    st.subheader('''Land temperature anomaly is defined as: *"The departure from the average temperature, positive or negative, over a certain period (day, week, month or year)"* ''')
    st.subheader('''To start exploring the data, please use the sidebar on the left side!''')