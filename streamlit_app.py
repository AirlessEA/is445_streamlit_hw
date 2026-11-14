import streamlit as st
import altair as alt
import pandas as pd
from vega_datasets import data

st.set_page_config(page_title="Bigfoot Reports", page_icon=":footprints:")

st.title('Bigfoot Sighting Reports Across the US')
st.subheader('IS 445 Homework: Streamlit App')

bfro_url = 'https://raw.githubusercontent.com/UIUC-iSchool-DataViz/is445_data/main/bfro_reports_fall2022.csv'

st.markdown("""
This app uses the [BFRO reports dataset](https://raw.githubusercontent.com/UIUC-iSchool-DataViz/is445_data/main/bfro_reports_fall2022.csv), which has 4,747 Bigfoot reports collected by the Bigfoot Field Researchers Organization. Every report is tagged with the state and season it happened in, plus a report class. Class A reports are clear sightings and Class B reports are sounds or things seen from far away or in bad light. The few Class C reports are secondhand stories. Reports with a date also come with a location and the weather for that day.
""")

df = pd.read_csv(bfro_url)

# year of the sighting (reports with no date get NaN and drop out of the year filter below)
df['year'] = pd.to_datetime(df['date']).dt.year

#######################################################
# Visualization 1: timeline linked to a map
#######################################################

st.header('1. When and where were reports made?')

st.markdown("""
Click and drag across the bar chart to pick a range of years and the map will only show reports from those years. Double-click the bar chart to reset it, and hover over a point to see the report's title.
""")

df_years = df[df['year'] >= 1950]
df_years = df_years[['year', 'date', 'state', 'classification', 'latitude', 'longitude', 'title']]
df_years['year'] = df_years['year'].astype(int)

# three reports (Montana, Washington, Idaho) have longitudes out in the Pacific, so they're left off the map
df_map = df_years[(df_years['longitude'] > -125) | (df_years['state'] == 'Alaska')]

brush = alt.selection_interval(encodings=['x'])

class_color = alt.Color('classification:N', scale=alt.Scale(scheme='dark2'), title='Report class')

timeline = alt.Chart(df_years[['year', 'classification']]).mark_bar().encode(
    alt.X('year:Q', bin=alt.Bin(maxbins=70), title='Year of sighting', axis=alt.Axis(format='d')),
    alt.Y('count()', title='Number of reports'),
    color=class_color
).properties(
    width=540,
    height=150
).add_params(
    brush
)

states = alt.topo_feature(data.us_10m.url, feature='states')

background = alt.Chart(states).mark_geoshape(
    fill='lightgray',
    stroke='white'
).properties(
    width=540,
    height=340
).project('albersUsa')

points = alt.Chart(df_map).mark_circle().encode(
    longitude='longitude:Q',
    latitude='latitude:Q',
    color=class_color,
    size=alt.value(18),
    opacity=alt.value(0.6),
    tooltip=['title:N', 'date:N', 'state:N']
).transform_filter(
    brush
)

chart1 = alt.vconcat(timeline, background + points)

st.altair_chart(chart1, theme='streamlit')

st.subheader('Write-up')
st.markdown("""
For the first visualization I wanted to look at when and where people were seeing Bigfoot, so I made a bar chart of reports per year that's linked to a map of the US. Dragging across the bar chart picks a range of years and the map only shows reports from those years. The biggest thing that jumps out is how many reports come from the 2000s. Out of the 3,783 dated reports since 1950, 1,543 are from 2000 to 2009, and 2004 alone has 241. Brushing the 1970s and then the 2010s also shows the report classes flipping. About 61% of the 1970s reports are Class A, but by the 2010s that drops to around 35% and most reports are Class B. I used bars with one bin per year on a linear count scale and formatted the year axis so 1950 doesn't show up as "1,950." For the map I used the albersUsa projection so Alaska still fits in the corner, and I made the points small with 0.6 opacity since places like western Washington get crowded fast. The report classes use the same dark2 colors in both charts so one legend covers both, and the teal and orange are easy to tell apart. I also cut the 14 reports from before 1950 because they stretched the axis out with almost empty bars, and I left 3 reports off the map because their longitudes put them in the Pacific Ocean (one of them is supposed to be in Montana). If I had more time I'd add a state map colored by reports per person. Right now I think the dots mostly follow where people live and hike, so a crowded area doesn't mean much on its own. I'd also like the link to go both ways so clicking a state filters the bar chart too.
""")

#######################################################
# Visualization 2: weather on the day of the report
#######################################################

st.header('2. What was the weather like?')

st.markdown("""
Pick a weather variable with the buttons and pick one or more seasons from the list. If the season list is empty, all four seasons show up.
""")

df['humidity_pct'] = df['humidity'] * 100
df['cloud_pct'] = df['cloud_cover'] * 100

weather_vars = {
    'High temperature (°F)': 'temperature_high',
    'Humidity (%)': 'humidity_pct',
    'Cloud cover (%)': 'cloud_pct',
    'Moon phase (0 = new moon, 0.5 = full moon)': 'moon_phase',
    'Wind speed (mph)': 'wind_speed'
}

seasons = ['Spring', 'Summer', 'Fall', 'Winter']
df_weather = df[df['season'].isin(seasons)]

col1, col2 = st.columns(2)
var_label = col1.radio('Weather variable:', list(weather_vars.keys()))
seasons_selected = col2.multiselect('Which seasons do you want to view?', seasons)

if len(seasons_selected) > 0:
    df_sub = df_weather[df_weather['season'].isin(seasons_selected)]
else:
    df_sub = df_weather

var_col = weather_vars[var_label]

hist = alt.Chart(df_sub[[var_col, 'season']]).mark_bar().encode(
    alt.X(var_col + ':Q', bin=alt.Bin(maxbins=20), title=var_label),
    alt.Y('count()', title='Number of reports'),
    alt.Color('season:N',
              scale=alt.Scale(domain=seasons, range=['#59a14f', '#edc948', '#b5562b', '#4e79a7']),
              title='Season')
).properties(
    height=350
)

st.altair_chart(hist, theme='streamlit', width='stretch')

st.subheader('Write-up')
st.markdown("""
So what was the weather like when people reported seeing Bigfoot? The dataset has the weather for the day of each dated report, so the second visualization is a histogram where you pick a weather variable with the radio buttons and pick seasons with the multiselect. Moon phase was the one I was most curious about. I kind of expected a spike around the full moon, but the bars are pretty flat the whole way across and the bins around the full moon aren't any taller than the ones around the new moon. Temperature is a different story. It moves a lot with the season, with most summer reports between 70 and 90°F and winter reports centered around 50°F. Cloud cover piles up at both ends, and about 23% of reports happened on days with 10% cloud cover or less. I used up to 20 bins for every variable so the bin width stays readable whether the range is 0 to 1 or 0 to 100, with the count on a linear y axis. I also converted humidity and cloud cover from fractions to percents since a humidity of 0.73 doesn't mean much to most people. The seasons get the colors you'd expect (green for spring, yellow for summer, rust for fall and blue for winter), and I fixed the color domain so a season keeps its color when you add or remove the others. I left out the 91 reports with an unknown season, and reports without weather data just don't get a bar, which is around a third of them depending on the variable. Honestly the stacking is what I'd change first. Only the bottom season sits on a flat baseline, so it's hard to compare the shapes of summer and fall when they're piled on top of winter. With more time I'd switch to small multiples with one histogram per season, or show percents so summer's bigger count doesn't drown out winter.
""")

st.header('Note on Homework #5')
st.markdown("""
Neither visualization is reused from Homework #5. That homework used the UFO dataset with a stacked area chart and a month by hour heatmap, while this app uses the BFRO dataset with new plot types and none of the write-up is copied over.
""")
