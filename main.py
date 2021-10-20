import numpy as np
import streamlit as st
import pandas as pd
import pydeck as pdk
from pydeck.types import String
import plotly.figure_factory as ff
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

path = 'AB_NYC_2019.csv'
df = pd.read_csv(path)
df['last_review'] = pd.to_datetime(df['last_review']).dt.date
st.set_page_config(layout="wide")
st.title('Analysis of the most reviewed listings in neighborhoods in NYC')
st.header('Table schema')
st.write(df.head())

def print_region(nbh_data, lat, lon, percent, zoom=11):
    st.title('Exploring most-reviewed listings in ' + nbh_select)
    data = nbh_data.sort_values(['number_of_reviews'], ascending=False)[:int(len(nbh_data) * percent / 100)]
    figs = list(st.columns((1, 1, 1)))
    for id, type in enumerate(room_types):
        temp_data = data[data['room_type'] == type]
        temp_nbh_data = nbh_data[nbh_data['room_type'] == type]

        with figs[id]:
            st.write(type)
            st.pydeck_chart(
                pdk.Deck(
                    map_style="mapbox://styles/mapbox/light-v9",
                    initial_view_state={
                        "latitude": lat,
                        "longitude": lon,
                        "pitch": 50,
                        'zoom': zoom
                    },
                    layers=[
                        pdk.Layer(
                            "HexagonLayer",
                            temp_data[['latitude', 'longitude']],
                            get_position=['longitude', 'latitude'],
                            auto_highlight=True,
                            radius=100,
                            elevation_scale=2,
                            pickable=True,
                            extruded=True,
                            aggregation=String('MEAN'),
                            # # coverage=1
                        )
                    ]
                )
            )
    st.title('Prices of most-reviewed listings in ' + nbh_select)
    figs = list(st.columns((1, 1, 1)))
    for id, type in enumerate(room_types):
        temp_data = data[data['room_type'] == type]
        temp_nbh_data = nbh_data[nbh_data['room_type'] == type]

        with figs[id]:
            st.write(type)
            fig = ff.create_distplot([temp_data['price'], temp_nbh_data['price']], group_labels=['Most-reviewed', 'All'],  bin_size=100)
            st.plotly_chart(fig, use_container_width=True)

    # check the most used words in these listings
    st.title('Most used phrases in most-reviewed listings in ' + nbh_select)
    list_names = data['name'].to_list()
    list_names = map(str, list_names)
    text = ','.join(list_names)

    other = {nbh_select}
    # Create and generate a word cloud image:
    wordcloud = WordCloud(stopwords=STOPWORDS.union(other), width=1000, height=400).generate(text)
    wordfreq = list(wordcloud.words_.keys())
    words = wordfreq[:int(len(wordfreq) / 2)]

    # Display the generated image:
    fig = plt.figure(figsize=(200, 2))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    st.pyplot(fig)

    locations = list(nbhs) + list(nbh_vals)
    neighborhood_names = []
    # common/
    for word in words:
        if word in nbhs:
            neighborhood_names.append(word)
    st.header('The most popular neighborhoods in ' + nbh_select)
    st.subheader(', '.join(neighborhood_names[:5]))


st.set_option('deprecation.showPyplotGlobalUse', False)

nbh_vals = df['neighbourhood_group'].unique()
nbhs = df['neighbourhood'].unique()

room_types = df['room_type'].unique()

nbh_select = st.sidebar.selectbox('Choose neighborhood group', nbh_vals)
percent = st.sidebar.slider("Choose the percentage of most-reviewed listings", min_value=1, max_value=100, value=30)
# type_select = st.sidebar.selectbox('choose room type', room_types)

selected_df = df[(df['neighbourhood_group'] == nbh_select)
    # & (df['room_type'] == type_select)
]
mean_lat, mean_lon = np.mean(selected_df[['latitude', 'longitude']])
print_region(selected_df, mean_lat, mean_lon, percent)
