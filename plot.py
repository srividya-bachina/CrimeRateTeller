import altair as alt
import pandas as pd
#import numpy as np
import folium
#import json
#from geopy.geocoders import Nominatim


data = pd.read_excel("Data/processed_data.xlsx")

def YearVsCrime():
    selection = alt.selection_single(empty='none', on='mouseover', fields=['city'])
    # create an Altair chart object
    line = alt.Chart(data).mark_line().encode(
        x = alt.X('report_year', axis=alt.Axis(format='Y')),
        y = 'crimes_percapita:Q',
        color = alt.Color('city:N', legend=None),
        opacity = alt.condition(selection, alt.value(1), alt.value(0.2)),
        tooltip=['city', 'state_codes', 'report_year', 'crimes_percapita']
    ).add_selection(
        selection
    ).properties(
        width=600,
        height=400,
        title='Crime percapita from 1975 to 2015'
    ).interactive()

    return line

def StateVsCrime():
    alt.data_transformers.enable('default', max_rows=None)
    stacked_data = pd.melt(data, id_vars=['state_codes'], value_vars=['homicides', 'rapes', 'assaults', 'robberies'], var_name='types', value_name='crimes')
    stacked_data['order'] = pd.Categorical(stacked_data['types'], ['homicides', 'rapes', 'assaults', 'robberies'])

    # create the stacked bar chart
    bar = alt.Chart(stacked_data).mark_bar().encode(
        x='state_codes:N',
        y=alt.Y('crimes:Q', stack='zero'),
        color=alt.Color('types:N', scale=alt.Scale(range=['#4c78a8', '#f58518', '#e45756', '#72b7b2'])),
        order=alt.Order('order', sort='ascending'),
        tooltip= ['crimes']
    ).properties(
        width=600,
        height=400,
        title='Crime Types by State'
    ).interactive()

    return bar


def CrimePercent():

    # Calculate total number of crimes
    total_crimes = data[['homicides', 'assaults', 'rapes', 'robberies']].sum().sum()

    # Calculate percentage of each crime type
    homicides_pct = (data['homicides'].sum() / total_crimes) * 100
    assaults_pct = (data['assaults'].sum() / total_crimes) * 100
    rapes_pct = (data['rapes'].sum() / total_crimes) * 100
    robberies_pct = (data['robberies'].sum() / total_crimes) * 100

    homicides_pct = round(homicides_pct, 2)
    assaults_pct = round(assaults_pct, 2)
    rapes_pct = round(rapes_pct, 2)
    robberies_pct = round(robberies_pct, 2)

    # Create a dataframe with the crime types and percentages
    crime_pct_df = pd.DataFrame({
        'Crime Type': ['Homicides', 'Assaults', 'Rapes', 'Robberies'],
        'Percentage': [homicides_pct, assaults_pct, rapes_pct, robberies_pct]
    })
    # Create a pie chart
    base = alt.Chart(crime_pct_df).mark_arc(innerRadius=50).encode(
        theta=alt.Theta("Percentage:Q"),#, stack=True), 
        color=alt.Color("Crime Type:N"),
        tooltip=['Percentage', 'Crime Type']
    ).properties(
        width=600,
        height=400,
        title='Crime Type Percentage'
    )

    pie = base.mark_arc(outerRadius=120)
    
    return pie

def ScatterPlot():
    # create a scatter plot
    scatter_plot = alt.Chart(data).mark_point().encode(
        x='crimes_percapita:Q',
        y='population:Q',
        color=alt.Color('state_codes:N'),
        size=alt.Size('crimes_percapita:Q'),
        tooltip= ['state_codes:N', 'crimes_percapita:Q', 'population:Q']
    ).properties(
        width=600,
        height=400,
        title='Population Vs Crime Percapita'
    ).interactive()

    return scatter_plot

def DynamicLine(year_min, year_max, state, city):
    # filter the data based on the given parameters
    filtered_data = data[(data['report_year'] >= year_min) & (data['report_year'] <= year_max)]
    if state:
        filtered_data = filtered_data[filtered_data['state_codes'] == state]
    if city:
        filtered_data = filtered_data[filtered_data['city'] == city]

    alt.data_transformers.enable('default', max_rows=None)
    stacked_data = pd.melt(filtered_data, id_vars=['report_year','state_codes'], value_vars=['homicides', 'rapes', 'assaults', 'robberies'], var_name='types', value_name='crimes')
    stacked_data['order'] = pd.Categorical(stacked_data['types'], ['homicides', 'rapes', 'assaults', 'robberies'])

    # create brushing and linking selection
    brush = alt.selection(type='interval')
    # create an Altair chart object
    line = alt.Chart(stacked_data).mark_line().encode(
            x = alt.X('report_year', axis=alt.Axis(format='Y')),
            y = 'sum(crimes):Q'
        ).properties(
            width=600,
            height=400,
            title=f'Crime Percapita in {city}, {state} ({year_min}-{year_max})'
        ).add_selection(
            brush
        )
    
    bar = alt.Chart(stacked_data).mark_bar().encode(
        x=alt.X('crimes:Q'),
        y=alt.Y('types:N'),
        color=alt.Color('types:N', scale=alt.Scale(range=['#4c78a8', '#f58518', '#e45756', '#72b7b2'])),
        order=alt.Order('order:O', sort='ascending'),
        tooltip= ['crimes:Q']
    ).properties(
        width=600,
        title='Crime by types'
    ).transform_filter(
        brush
    )

    # combine line chart and
    #  bar chart
    combined_chart = alt.vconcat(line, bar)

    # return the combined chart
    return combined_chart

def Map(state, city):
    df = pd.read_excel("Data/USCities.xlsx")
    if state:
        filtered_data = df[df['state_id'] == state]

    map = folium.Map(location=[filtered_data['lat'].mean(), filtered_data['lng'].mean()], zoom_start=4)
    for index, row in filtered_data.iterrows():
        tooltip = row['city']
        folium.Marker([row['lat'], row['lng']], tooltip=tooltip).add_to(map)
        if (row['city'] == city):
            folium.Marker([row['lat'], row['lng']], tooltip=tooltip, icon=folium.Icon(color='red')).add_to(map)


    return map #json.loads(map.to_json())

def StackedArea(year_min, year_max, state, city):
    crime_data = data[(data["report_year"] >= year_min) & (data["report_year"] <= year_max) & (data["state_codes"] == state) & (data["city"] == city)]
    stacked_data = pd.melt(crime_data, id_vars=['report_year'], value_vars=['homicides', 'rapes', 'assaults', 'robberies'], var_name='types', value_name='crimes')
    stacked_data['order'] = pd.Categorical(stacked_data['types'], ['homicides', 'rapes', 'assaults', 'robberies'])
    chart = alt.Chart(stacked_data).mark_area().encode(
                x=alt.X('report_year', title='Year', axis=alt.Axis(format='Y')),
                y=alt.Y('crimes:Q', stack='zero', title='Crime per capita'),
                color=alt.Color('types:N', legend=alt.Legend(title='Crime type')),
                order=alt.Order('order', sort='ascending')
            ).properties(
                width=600,
                height=400,
                title=f'Total Crimes in {city}, {state} ({year_min}-{year_max})'
                ).interactive()
    return chart

def NearByJurisdictions(state):
    if state:
        filtered_data = data[data['state_codes'] == state]
    
    bar = alt.Chart(filtered_data).mark_bar().encode(
        x=alt.X('city:N'),
        y=alt.Y('violent_crimes:Q'),
        color=alt.Color('city:N'),
        tooltip= ['violent_crimes:Q']
    ).properties(
        height=400,
        width=600,
        title=f'Crime in Other Cities in {state}'
    )

    return bar
