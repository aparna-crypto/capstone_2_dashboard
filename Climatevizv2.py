import pandas as pd
import numpy as np
from plotly import plot
import plotly.graph_objects as go
import streamlit as st

########################################################## DATA LOADING AND CLEANING SECTION ##########################################################

@st.cache
def load_data(path):
    data = pd.read_csv(path, encoding= "latin1")

    # ELIMINATING USELESS COLUMNS
    data = data.drop(labels = ["Unit", "Months Code"], axis=1)

    # STANDARIZING COLUMN NAMES

    # standard coumn cleaning cleaning
    data.columns = [column.lower().strip() for column in list(data.columns)]

    # eliminating "Y" from year columns and casting them as integers
        ## retrieving years with "y"
    years = [year for year in list(data.columns) if year[0] == "y"]
        ## creating fixed years
    f_years = [int(year.replace("y","")) for year in years]
        ## merging lists
    mapped_years = zip(years, f_years)
        ## dictionary comprehension for creating new_cols dictionary. This is the argument of the name method
    new_cols = {key:int(value) for key,value in mapped_years}
        ## executing rename
    data = data.rename(columns = new_cols)
        ## cleaining temp variables
    del years
    del mapped_years
    del new_cols

    # STANDARIZING COUNTRY NAMES
        ## extracting countries with paranthesis in their name and creating df
    country_df = data["area"].str.extract("(?P<country>.*)(?P<other>\(.*\))").dropna()
        ## eliminating annoying whitespace
    country_df["country"] = country_df["country"].str.strip()
        ## extracting indexes 
    indexes = (index for index in country_df.index)
        ## replacing indicated indeces in parent df
    for index in indexes:
        data.loc[index,"area"] = country_df.loc[index,"country"]

    # CLEANING MONTHS NAMES
        ## Cleaning Quarters with encoding difficulties
    data["months"] = data["months"].str.replace("\x96", "-")

    # ELIMINATING STANDARD DEVIATION
    data = data[data["element"] != "Standard Deviation"]
        
    return data

########################################################## RETRIVING AVAILABLE YEARS DATAFRAME SECTION ##########################################################
def onec_year_range(data = None, country = "Nicaragua"):
    if data is None:
        raise FileNotFoundError("ERROR LOADING DATA, ENDING.")
    country_data = data[(data["area"] == country)] # boolean masking based on country
    country_data = country_data.T # tranposing
    country_data = country_data.drop(index = ['area code','area','months','element code','element']) #dropping unnnecessary indexes
    country_data = country_data.dropna() # removing indexes with no data
    return country_data.index

def multic_year_range(data = None, countries = ["Nicaragua", "Costa Rica"] ):
    if data is None:
        raise FileNotFoundError("ERROR LOADING DATA, ENDING.")
    country_data = data[data["area"].apply(lambda x: x in countries)] # creating boolean mask by verifying if countries are inside the list
    country_data = country_data.T # tranposing
    country_data = country_data.drop(index = ['area code','area','months','element code','element']) #dropping unnnecessary indexes
    country_data = country_data.count(axis=1) # creating count of columns with data in them
    country_data = country_data[country_data >= 17] # removing all indexes where, for ANY country, there's no data
    return country_data.index

########################################################## SLICING DATAFRAME SECTION ##########################################################

def config_data_onec(data = None, country = None, year_bottom = None, year_top = None, period = None):
    '''
    Function to parse data in the one_country scenario.
    '''
    if data is None:
        raise FileNotFoundError("DATA NOT LOAD FAILURE, ENDING.")
    data = data[(data["area"] == country) & (data["months"] == period)] ## filtering
    data = data.T
    data = data.drop(index = ['area code','area','months','element code','element']) ## deleting unnecesary data.
    data.columns = ["Temperature Anomaly"] ## reassigning column and adjusting type again
    data = data.loc[year_bottom:year_top] ## filtering based on desired years
    data = data.astype("float")
    data.index = data.index.astype(int) ## fixing index dtype
        ## creating color map of result for easier plotting
    data["color"] = np.where(data["Temperature Anomaly"] > 0, "red", "blue")
        ## setting index as column for plot purposes
    data = data.reset_index()
    data = data.rename(columns={"index":"Year"})
    return data

def config_data_multi(data = None, country_list = [], year_bottom = None, year_top = None, period = None):
    '''
    Function to parse data in the multi_country scenario.
    '''
    if data is None:
        raise FileNotFoundError("DATA NOT LOAD FAILURE, ENDING.")
    data = data[data["area"].apply(lambda x: x in country_list)]
    data = data[data["months"] == period]
    data = data.T
    area_order = list(data.loc["area"]) # since column names are lost and not in order, we'll get them before dropping unnecesary stuff
    data = data.drop(index = ['area code', 'area', 'months','element code','element']) #dropping unnnecessary indexes
    data.columns = area_order # manually setting the column names in the correct order
    data = data.loc[year_bottom:year_top] ## filtering based on desired years
    data = data.astype("float") # fixing dtypes
    data.index = data.index.astype(int)
    for column in list(data.columns): # setting colors in order of appearance
        data[column+"_color"] = np.where(data[column] > 0, "red", "blue")
    return data

def max_multi_display(data = None):
    if data is None:
        raise NotImplementedError("ERROR LOADING DATA")
    pass
########################################################## PLOT SECTION ##########################################################

def plot_onec(data, bottom, top):

    fig = go.Figure() # instantiate parent figure

    # create line to visualize actual data points
    fig.add_scatter(
    x = data["Year"], 
    y = data["Temperature Anomaly"], 
    mode="lines+markers", 
    marker=dict(
        color = data["color"],
        size = 10), 
    line=dict(color="grey")
    )

    # creating a reference line at 0 (ALTERNATIVE METHOD)
    fig.add_shape(
    type="line",
    x0= bottom,
    y0= 0,
    x1= top,
    y1= 0,
    line=dict(
        color='rgba(0, 0, 0, 0.3)', # reference line through RGBA to add transparency
        width=2,
        dash="dot"
        )
    )

    # creating reference line at max value (RECOMMENDED METHOD)
    fig.add_hline(
        y = data["Temperature Anomaly"].max(),
        line_dash = "dash",
        opacity = 0.5,
        line_color = "red",
        annotation_text = "Max Temp Anomaly",
        annotation_position = "top right",
        annotation_font_size = 14,
        annotation_font_color = "red"
    )

    # creating reference line at min value (RECOMMENDED METHOD)
    fig.add_hline(
        y = data["Temperature Anomaly"].min(),
        line_dash = "dash",
        opacity = 0.5,
        line_color = "blue",
        annotation_text = "Min Temp Anomaly",
        annotation_position = "bottom right",
        annotation_font_size = 14,
        annotation_font_color = "blue"
    )

    fig.update_layout(
        yaxis_title = "Temperature Anomaly",
        xaxis_title = "Year",
        xaxis = dict(
            tickmode = 'linear',
            tick0 = bottom,
            dtick = 2), # setting ticks to be every 2nd year in the existing range for easier read
        font = dict(
            size=14)
        )
    
    return fig

def plot_multic(data, countries, bottom, top):

    fig = go.Figure() # instantiating parent figure

    fig.add_shape(
    type="line", # adding reference line at axis 0
    x0 = bottom,
    y0 = 0,
    x1 = top,
    y1 = 0,
    line=dict(
        color='rgba(0, 0, 0, 0.3)', # reference line through RGBA to add transparency
        width=2,
        dash="dot"
        )
    )

     # creating reference line at max value (RECOMMENDED METHOD)
    fig.add_hline(
        y = data.iloc[:,:len(countries)].max().max(),
        line_dash = "dash",
        opacity = 0.5,
        line_color = "red",
        annotation_text = "Max Temp Anomaly",
        annotation_position = "top right",
        annotation_font_size = 14,
        annotation_font_color = "red"
    )

    # creating reference line at min value (RECOMMENDED METHOD)
    fig.add_hline(
        y = data.iloc[:,:len(countries)].min().min(),
        line_dash = "dash",
        opacity = 0.5,
        line_color = "blue",
        annotation_text = "Min Temp Anomaly",
        annotation_position = "bottom right",
        annotation_font_size = 14,
        annotation_font_color = "blue"
    )

    if len(countries) < 4:
        line_types = ['dash', 'dot', 'dashdot']
        line_colors = ["black", "purple", "darkgreen"]
        for i,country in enumerate(countries):
            fig.add_scatter(
                x = data.index,
                y = data[country],
                mode = "lines+markers",
                marker = dict(
                    color = data.iloc[:,len(countries)+i],
                    size = 10),
                line = dict(
                    color = line_colors[i],
                    dash = line_types[i],
                    width = 3),
                name = country
            )
    
    else:
        for i,country in enumerate(countries):
            fig.add_scatter(
                x = data.index,
                y = data[country],
                mode = "lines+markers",
                marker = dict(
                    color = data.iloc[:,len(countries)+i],
                    size = 10),
                line = dict(color = "grey"),
                name = country
            )
    
    fig.update_layout(
    yaxis_title = "Temperature Anomaly",
    xaxis_title = "Year",
    xaxis = dict(
        tickmode = 'linear',
        tick0 = bottom,
        dtick = 2), # setting ticks to be every 2nd year in the existing range for easier read
    font = dict(
        size=14)
    )

    return fig

''' DEPRECATED
def plot_chart(country_data, low = 1961, high = 2019):

    # setting figsize and titles
    fig = plt.figure()

    # setting X tick range dynamically and label
        # deprecated solution
        # ax = plt.gca()
        # ax.set_xticks("lowerbound", "upperbound", "step"))

    # setting a dynamic step size for visibility
    x_step = int((high - low) / 10)

    ax = plt.gca()
    ax.xaxis.set_major_locator(ticker.MultipleLocator(x_step))
    ax.set_xlabel("Year", fontdict = {"fontsize": 16})

    # setting Y tick range to a fixed lenght
    ax.yaxis.set_major_locator(ticker.MaxNLocator())
    ax.set_ylabel("Temperature Anomaly", fontdict = {"fontsize": 16})

    # creating general line plot
    plt.plot(country_data.index, country_data["Temperature Anomaly"], alpha = 0.3, color = "black", label = "Temperature Anomaly")
    plt.plot(country_data.index, [0]*country_data.index.shape[0], color="black", linewidth = 1)

    # adding points above 0 in red and rest in blue
    plt.scatter(country_data.index, country_data["Temperature Anomaly"], c = country_data["color"], s = 50)

    # adding signal to the highest and lowest values in the plot
    plt.axhline(country_data["Temperature Anomaly"].max(), linestyle = "--", color = "red", linewidth = 1)
    plt.axhline(country_data["Temperature Anomaly"].min(), linestyle = "--", color = "blue", linewidth = 1)

    return fig

'''