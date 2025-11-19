# This app was written by Geemini Flass2.5, on Nov 7, 2025.
# It was the response of this prompt:

"""
create a simple streamlit that does the following:
- uses the titanic dataset
- on the sidebar it has a menu of five different exploratory analysis that it can do with the dataset
- whenever one clicks a menu item, we see the analysis on the main page
- the main page should have some widget that allow for some control over the graphs, such as dropdown for choosing values, or something else
Do not write complex code, keep it simple.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuration and Data Loading
st.set_page_config(layout="wide", page_title="Titanic Exploratory Analysis")
st.subheader("BB's very own Titanic dataset analysis")

@st.cache_data
def load_data():
    """Loads the Titanic dataset and performs basic preprocessing for analysis."""
    # Load the well-known Titanic dataset from a public repository
    data_url = 'https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv'
    df = pd.read_csv(data_url)

    # Basic feature engineering for easier plotting
    df['Cabin_Deck'] = df['Cabin'].str[0].fillna('Unknown')
    df['Survived_Text'] = df['Survived'].map({0: 'No', 1: 'Yes'})
    df['Pclass_Text'] = df['Pclass'].map({1: 'First', 2: 'Second', 3: 'Third'})
    return df

df = load_data()

# 2. Sidebar Menu Setup
st.sidebar.title("Select Analysis")
analysis_options = {
    "1": "Survival Rate by Class",
    "2": "Age Distribution Analysis",
    "3": "Fare vs. Age Scatter Plot",
    "4": "Survival by Gender and Port",
    "5": "Cabin Deck vs. Survival"
}

# The radio buttons control which analysis is shown on the main page
option_key = st.sidebar.radio(
    "Choose an exploratory view:",
    list(analysis_options.keys()),
    format_func=lambda x: analysis_options[x] # Display the friendly name in the sidebar
)

st.title(f"Titanic Dataset Explorer: {analysis_options[option_key]}")

# 3. Main Page Logic based on Selection
if option_key == "1":
    # --- Analysis 1: Survival Rate by Class (Bar Chart) ---

    st.header("1. Survival Rate by Passenger Class")
    st.markdown("Examine the proportion of survivors across the three passenger classes.")

    # Widget: Dropdown to select the class to filter/highlight
    highlight_class = st.selectbox(
        "Filter Data by Class:",
        ['All'] + df['Pclass_Text'].unique().tolist(),
        key='a1_select_class'
    )

    df_filtered = df.copy()
    if highlight_class != 'All':
        df_filtered = df_filtered[df_filtered['Pclass_Text'] == highlight_class]

    # Calculate survival proportion for plotting
    survival_data = df_filtered.groupby(['Pclass_Text', 'Survived_Text']).size().unstack(fill_value=0)
    survival_data['Total'] = survival_data.sum(axis=1)
    # Avoid division by zero if a class has no data (only relevant if filter used)
    survival_data['Survival_Rate'] = survival_data.apply(
        lambda row: (row['Yes'] / row['Total'] * 100) if row['Total'] > 0 else 0, axis=1
    )
    survival_data = survival_data.reset_index()

    # Create the chart
    fig = px.bar(
        survival_data,
        x='Pclass_Text',
        y='Survival_Rate',
        color='Pclass_Text',
        title=f'Survival Rate (%) by Class (Filter: {highlight_class})',
        labels={'Pclass_Text': 'Passenger Class', 'Survival_Rate': 'Survival Rate (%)'},
        color_discrete_map={'First': '#1f77b4', 'Second': '#ff7f0e', 'Third': '#2ca02c'}
    )
    st.plotly_chart(fig, use_container_width=True)

elif option_key == "2":
    # --- Analysis 2: Age Distribution (Histogram) ---

    st.header("2. Age Distribution Analysis")
    st.markdown("Visualize the frequency distribution of passengers' ages.")

    # Widget: Slider to control the bin size of the histogram
    bin_size = st.slider(
        "Select Number of Bins:",
        min_value=10,
        max_value=50,
        value=30,
        step=5,
        key='a2_bin_slider'
    )

    fig = px.histogram(
        df.dropna(subset=['Age']), # Drop NaNs for Age only
        x='Age',
        nbins=bin_size,
        color='Survived_Text',
        title=f'Age Distribution (Bins: {bin_size})',
        opacity=0.7,
        marginal="box", # Adds a box plot on top for better statistics
        color_discrete_map={'No': '#ef553b', 'Yes': '#636efa'}
    )
    fig.update_layout(bargap=0.1)
    st.plotly_chart(fig, use_container_width=True)

elif option_key == "3":
    # --- Analysis 3: Fare vs. Age (Scatter Plot) ---

    st.header("3. Fare vs. Age Scatter Plot")
    st.markdown("Explore the relationship between passenger age and the fare they paid, colored by survival status.")

    # Widget: Checkbox to filter by sex
    selected_sex = st.multiselect(
        "Filter by Sex:",
        df['Sex'].unique().tolist(),
        default=df['Sex'].unique().tolist(),
        key='a3_sex_filter'
    )

    df_plot = df[df['Sex'].isin(selected_sex)].dropna(subset=['Age', 'Fare'])

    fig = px.scatter(
        df_plot,
        x='Age',
        y='Fare',
        color='Survived_Text',
        hover_data=['Pclass_Text', 'Sex'],
        title=f'Fare vs. Age Colored by Survival (Sexes: {", ".join(selected_sex)})',
        labels={'Survived_Text': 'Survived'},
        color_discrete_map={'No': '#ef553b', 'Yes': '#636efa'}
    )
    st.plotly_chart(fig, use_container_width=True)

elif option_key == "4":
    # --- Analysis 4: Survival by Gender and Port (Count Plot) ---

    st.header("4. Survival Count by Gender and Embarkation Port")
    st.markdown("Compare the number of survivors and non-survivors based on gender and port of embarkation.")

    # Widget: Dropdown to filter by Pclass
    selected_pclass = st.multiselect(
        "Filter by Passenger Class:",
        df['Pclass_Text'].unique().tolist(),
        default=df['Pclass_Text'].unique().tolist(),
        key='a4_pclass_filter'
    )

    df_plot = df[df['Pclass_Text'].isin(selected_pclass)].dropna(subset=['Embarked'])

    # Create stacked bar chart using the grouped counts
    plot_data = df_plot.groupby(['Embarked', 'Sex', 'Survived_Text']).size().reset_index(name='Count')

    fig = px.bar(
        plot_data,
        x='Embarked',
        y='Count',
        color='Survived_Text',
        facet_col='Sex', # Separate columns for male and female
        title=f'Survival Counts by Port and Gender (Filtered Classes: {", ".join(selected_pclass)})',
        labels={'Embarked': 'Port of Embarkation', 'Survived_Text': 'Survived'},
        category_orders={"Sex": ["male", "female"]},
        color_discrete_map={'No': '#ef553b', 'Yes': '#636efa'}
    )
    st.plotly_chart(fig, use_container_width=True)

elif option_key == "5":
    # --- Analysis 5: Cabin Deck vs. Survival (Count Plot) ---

    st.header("5. Cabin Deck vs. Survival")
    st.markdown("The first letter of the 'Cabin' often indicates the deck. Let's see survival by deck.")

    # Widget: Checkbox to filter for only 'Survived' in the plot data
    show_survived_only = st.checkbox(
        "Show Survivors Only",
        key='a5_survived_filter'
    )

    df_plot = df[df['Cabin_Deck'] != 'Unknown'].copy()
    if show_survived_only:
        df_plot = df_plot[df_plot['Survived_Text'] == 'Yes']

    deck_counts = df_plot.groupby(['Cabin_Deck', 'Survived_Text']).size().reset_index(name='Count')

    # Create the chart
    fig = px.bar(
        deck_counts,
        x='Cabin_Deck',
        y='Count',
        color='Survived_Text',
        title=f"Passenger Counts by Cabin Deck (Mode: {'Survivors Only' if show_survived_only else 'All Passengers'})",
        labels={'Cabin_Deck': 'Cabin Deck', 'Survived_Text': 'Survived'},
        category_orders={"Cabin_Deck": sorted(df_plot['Cabin_Deck'].unique())},
        color_discrete_map={'No': '#ef553b', 'Yes': '#636efa'}
    )
    st.plotly_chart(fig, use_container_width=True)