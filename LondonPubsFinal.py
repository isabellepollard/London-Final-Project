"""
Name: Isabelle Pollard
CS230: Section 4
Data: London Pubs
URL:

Description:
This program looks at the data of London Pubs. There are many different features as well as different ways to view the
data. The first is that you can see where the pubs are located in a bar chart, and the top 3 most populated
neighborhoods also in a chart. Then, you can see what percent of pubs start with the letter the user selects through a
pie chart. On the next dropdown you can select the histogram to see how far the pubs are from the famous landmark, the
London Bridge. You can also view the overall map that shows all the pubs in the data on the map and the pubs in the top 3
most populated areas.

This changed a bit from my original idea in that I only chose one of the famous landmarks because the formulation got a
bit complicated in the code.
"""

import pandas as pd
import pydeck as pdk
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np


st.set_page_config(page_title="Pubs in London", page_icon="🍺", layout="wide", initial_sidebar_state="expanded")
st.set_option('deprecation.showPyplotGlobalUse', False)

def read_data_file():
    columns = ["fsa_id", "name", "address", "postcode", "easting", "northing", "latitude", "longitude",
               "local_authority"]
    columns = [column.lower() for column in columns]
    return pd.read_csv("C:/Users/Isabelle/Downloads/CS2304/FinalProj/open_pubs2.csv", names=columns)


def filter_pubs_neighborhood(df, neighborhoods, letters):  # [PY1] Function with 2 or more parameters
    df["latitude"] = pd.to_numeric(df["latitude"].replace("\\N", pd.NA), errors="coerce")    #[DA1] cleaning data #CH. 11
    df["longitude"] = pd.to_numeric(df["longitude"].replace("\\N", pd.NA), errors="coerce")
    pub_names_df = df[["name"]].copy()
    df = df.dropna(subset=["latitude",
                           "longitude"])  # [DA7] Use of drop to get rid of cells with no values (subset makes sure only the Lat & Long are the ones dropped )
    neighborhood_df = df[df["local_authority"].isin(neighborhoods)]  # [DA4]  filter data by one condition

    long_mean = df["longitude"].mean()  # used to get n average map view
    lat_mean = df["latitude"].mean()

    st.write(  # Chatgbt
        """
    <div style="font-size: 60px; color: red; display: inline;"> Welcome </div>
     <div style="font-size: 60px; color: blue; display: inline;"> to </div>
    <div style="font-size: 60px; color: red;display: inline;"> London! </div>
    <div style="font-size: 35px; color: black;">
    
     </div>
    """,
        unsafe_allow_html=True)

    data_or_photos = st.sidebar.selectbox('Select Data or Images', ['Data of Pubs', 'Photo Gallery']) #[ST4]
    if data_or_photos == "Photo Gallery":
        image_display("Local Authority Chart", caption="Pub in Bedford")
        image_display("Histogram Chart", caption="London Bridge")
        image_display("", caption="Pub in London")
    elif data_or_photos == "Data of Pubs":
        user_page_selection = st.selectbox("Select what data you would like to find out about pubs in London",
                                           ["Home Page", "Local Authority Chart", "Alphabet Chart", "Overall Map",
                                            "Histogram Chart"])  # [ST1]  selectbox

        if user_page_selection == "Home Page":  # [PY4]
            pub_names = pub_names_df['name'].sort_values(ascending=True) # [DA2]  sorting data in ascending order
            data = {'Name': ['London Pub'], 'Path': ['C:/Users/Isabelle/Downloads/CS2304/FinalProj/pub_image.jpg']}
            df = pd.DataFrame(data)
            names_inline = ", ".join([name_of_pub for name_of_pub in pub_names])  # [PY4] List comprehension


            pub_image_path = df['Path'].iloc[0]
            st.image(pub_image_path, caption='London Pub', width=600)
            st.write("Below is a list of all the pubs in the dataset. Click the dropdown bar above to filter through the data.")
            st.write("There are 1000 pubs in this London dataset. ")
            st.write(names_inline)

        elif user_page_selection == "Local Authority Chart":
            neighborhoods = df.groupby("local_authority").size()   #cited on line 209
            neighborhoods.plot(kind="bar", figsize=(12, 6), color="pink")  # [VIZ1] bar chart
            plt.title("Pubs in Each Local Authority")
            plt.xlabel("Neighborhoods", color="pink")
            plt.ylabel("Number of Pubs", color="pink")
            st.pyplot()
            st.write()
            neighborhoods = df.groupby("local_authority").size().nlargest(3)  # [DA3] filtered by largest values      #cited
            neighborhoods.plot(kind="bar", figsize=(12, 6))
            plt.title("3 Most Pubs Dense Local Authorities")
            plt.xlabel("Neighborhoods", color="blue")
            plt.ylabel("Number of Pubs", color="blue")
            plt.xticks(
                rotation=0)  # used: https://discuss.streamlit.io/t/how-to-get-x-axis-values-to-be-vertical/12607/2 to turn the axis
            st.pyplot()
            image_display(user_page_selection)
        elif user_page_selection == "Alphabet Chart":
            letters = st.radio(
                "Select a letter to find out how many bars start with that letter and where they are located on a map:",
                "ABCDEFGHIJKLMNOPQRSTUVWXYZ")  # [ST2] radio

            pubs_with_letter = df[df["name"].str.startswith(letters)]   #boolean index that is able to filter the data by what it starts with
            num_pubs_with_letter = len(pubs_with_letter)
            num_pubs_without_letter = len(df) - num_pubs_with_letter

            st.write(
                "Below displays a chart of how many pubs in London start with that letter in comparison to the other bars. "
                "You can always click a different letter to find out more.")

            fig, ax = plt.subplots(figsize=(8, 4))    #cited below fig the new figure while ax is the subplot
            ax.pie([num_pubs_with_letter, num_pubs_without_letter],  # [VIZ2] pice chart
                   labels=[f"Starts with {letters}", f"Pubs that start with letters other than {letters}"],
                   autopct='%1.1f%%', startangle=90)  #tilts chart so it starts at 90 degrees
            st.pyplot()
        elif user_page_selection == "Overall Map":
            st.write("The map displayed below shows all the pubs in the London area.")
            filtered_df = df[df["name"].str.startswith(letters)]
            view_london = pdk.ViewState(  # [VIZ1] map
                latitude=lat_mean,
                longitude=long_mean,
                zoom=8,
                pitch=0)

            dots = pdk.Layer(type='ScatterplotLayer',
                             data=df,
                             get_position=["longitude", "latitude"],
                             get_radius=350,
                             get_color=[0, 200, 0],
                             pickable=True
                             )

            neighborhood_layer = pdk.Layer(type='ScatterplotLayer',
                                           data=neighborhood_df,
                                           get_position=["longitude", "latitude"],
                                           get_radius=350,
                                           get_color=[0, 0, 225],
                                           pickable=True
                                           )
           # letter_layer = pdk.Layer(
            #    type='ScatterplotLayer',
            #    data=filtered_df,
            #    get_position=["longitude", "latitude"],
            #    get_radius=350,
            #    get_color=[255, 0, 0],  # Red color for filtered pubs
            #    pickable=True
            #)

            user_layer_select = st.multiselect("Select the layers you would like to display on the map", ["All Pubs",
                             "Pubs in Most Dense Neighborhoods"])  # [ST3] multiselect

            layers = []
            if "All Pubs" in user_layer_select:
                layers.append(dots)
            if "Pubs in Most Dense Neighborhoods" in user_layer_select:
                layers.append(neighborhood_layer)
            #if "First Letter of Pubs" in user_layer_select:
            #    layers.append(letter_layer)

            tool_tip = {"html": "Pub Name:<br/> <b>{name}</b>",
                        "style": {"backgroundColor": "pink",
                                  "color": "white"}
                        }

            map = pdk.Deck(
                map_style='mapbox://styles/mapbox/streets-v12',
                initial_view_state=view_london,
                layers=layers,
                tooltip=tool_tip
            )
            st.pydeck_chart(map)


        elif user_page_selection == "Histogram Chart": # [VIZ3] Histogram
            londonbridge_lat = 51.3029
            londonbridge_long = 0.0516
            distance_away = []
            for index, row in df.iterrows():  # [DA8] Use of iterrows()
                latitude_pub = row['latitude']
                longitude_pub = row['longitude']
                # coordinates = (latitude_pub, longitude_pub)
                distance_between = np.sqrt((londonbridge_lat - latitude_pub) ** 2 + (
                        londonbridge_long - longitude_pub) ** 2)  # [DA9] Performed Calculation on columns
                distance_away.append(distance_between)

            st.write("Histogram of Distances from the London Bridge to all the Pubs in the data set")
            plt.hist(distance_away, bins=5, edgecolor='cyan') #bins are the nonoverlapping intervals
            plt.xlabel('Distance (km)', color= "cyan")
            plt.ylabel('Number of Pubs within the Distance ', color= "cyan")
            st.pyplot()
            image_display(user_page_selection)
    return df, neighborhood_df, long_mean, lat_mean, pub_names_df  # [PY2]


df = read_data_file()




def image_display(user_page_selection, caption=None):  # [PY3]
    image_path = {
        "Local Authority Chart": "C:/Users/Isabelle/Downloads/CS2304/FinalProj/Bedford_pub.jpg",
        "Histogram Chart": "C:/Users/Isabelle/Downloads/CS2304/FinalProj/london_bridge_pic.jpg"
    }  # [PY5]
    paths = image_path.get(user_page_selection, "C:/Users/Isabelle/Downloads/CS2304/FinalProj/pub_image.jpg")
    st.image(paths, caption=caption, width=400)
    return paths


neighborhoods = ["Bedford", "Braintree", "Central Bedfordshire"]

df, neighborhood_df, mean_latitude, mean_longitude, pub_names_df = filter_pubs_neighborhood(df, neighborhoods, letters = "A")


#.groupby from https://realpython.com/pandas-groupby/#using-lambda-functions-in-groupby
#nlargest from https://www.geeksforgeeks.org/python-pandas-dataframe-nlargest/
#subplot on pie chart https://www.geeksforgeeks.org/plot-a-pie-chart-in-python-using-matplotlib/
#histogram from https://www.geeksforgeeks.org/plotting-histogram-in-python-using-matplotlib/
#set_page_config from https://docs.streamlit.io/develop/api-reference/configuration/st.set_page_config