# This app was written with the help of Claude AI

"""
Streamlit app that (cont.)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import json

# 1. Configuration and Data Loading
st.set_page_config(layout="wide", page_title="Climate Change Wikipedia Analysis")

@st.cache_data
def load_data():
    """Load my CSV and language mapping JSON files."""
    # Load the CSV
    df = pd.read_csv('my_data/wiki_cc_subtopics.csv')

    # Load JSON 
    with open('my_data/subtopic_mapping.json', 'r', encoding='utf-8') as f:
        subtopic_mapping = json.load(f)

    return df, subtopic_mapping

df, subtopic_mapping = load_data()

# Language code to full name mapping
lang_map = {
    'en': 'English',
    'ar': 'Arabic',
    'fr': 'French',
    'es': 'Spanish',
    'de': 'German',
    'pt': 'Portuguese',
    'zh': 'Chinese',
    'ru': 'Russian',
    'uk': 'Ukrainian',
    'it': 'Italian'
}

# 2. Main Page stuff
st.title("Climate Change Subtopic Emphasis by Language")
st.subheader("Analyzing Wikipedia's Coverage of Climate Change Across Languages")

st.markdown("""
**Research Question:** How do different language editions of Wikipedia emphasize 
various climate change subtopics (Policy, Adaptation, Environment, Science, Sustainability)?

**Data Source:** This analysis examines climate change-related articles across the 
top 10 language editions of Wikipedia. Articles were categorized into subtopics based 
on keyword matching of titles and content.
""")

st.markdown("---")
st.subheader("Visualization Selections")

col1, col2 = st.columns(2)

with col1:
    # Widget 1: Select languages to display
    available_languages = df['language_code'].unique().tolist()
    language_options = ['All Languages'] + [f"{lang_map.get(x, x)} ({x})" for x in available_languages]
    selected_language = st.selectbox(
        "Select Language to Display:",
        options=language_options,
        index=0
    )

    # Convert selection back to list for filtering
    if selected_language == 'All Languages':
        selected_languages = available_languages
    else:
        # Extract language code from "English (en)" format
        lang_code = selected_language.split('(')[1].split(')')[0]
        selected_languages = [lang_code]

with col2:
    # Widget 2: Select subtopics to display
    available_subtopics = df['subtopic'].unique().tolist()
    subtopic_options = ['All Subtopics'] + available_subtopics
    selected_subtopic = st.selectbox(
        "Select Subtopic to Display:",
        options=subtopic_options,
        index=0
    )
    
    # Convert selection to list for filtering
    if selected_subtopic == 'All Subtopics':
        selected_subtopics = available_subtopics
    else:
        selected_subtopics = [selected_subtopic]

col3, col4 = st.columns(2)

with col3:
    # Widget 3: Chart type selection
    chart_type = st.radio(
        "Chart Type:",
        options=["Stacked Bar", "Grouped Bar", "Percentage Stacked"],
        index=0,
        horizontal=True
    )

with col4:
    # Widget 4: Sort options
    sort_option = st.selectbox(
        "Sort Languages By:",
        options=["Default Order", "Total Articles (Descending)", "Total Articles (Ascending)"]
    )

# Filter data based on selections
df_filtered = df[
    (df['language_code'].isin(selected_languages)) & 
    (df['subtopic'].isin(selected_subtopics))
].copy()

# Sort data based on selections
if sort_option == "Total Articles (Descending)":
    lang_totals = df_filtered.groupby('language_code')['article_count'].sum().sort_values(ascending=False)
    df_filtered['language_code'] = pd.Categorical(
        df_filtered['language_code'],
        categories=lang_totals.index.tolist(),
        ordered=True
    )
elif sort_option == "Total Articles (Ascending)":
    lang_totals = df_filtered.groupby('language_code')['article_count'].sum().sort_values(ascending=True)
    df_filtered['language_code'] = pd.Categorical(
        df_filtered['language_code'],
        categories=lang_totals.index.tolist(),
        ordered=True
    )
else:
    # Default order from original
    top10_langs = ['en', 'ar', 'fr', 'es', 'de', 'pt', 'zh', 'ru', 'uk', 'it']
    df_filtered['language_code'] = pd.Categorical(
        df_filtered['language_code'],
        categories=[l for l in top10_langs if l in selected_languages],
        ordered=True
    )

df_filtered = df_filtered.sort_values('language_code')

# Pivot df for plotting
df_wide = df_filtered.pivot(index=
                            'language_code', columns='subtopic', values='article_count')
df_wide = df_wide.fillna(0)

# Create visualization
st.markdown("---")
st.subheader("Article Distribution Across Languages and Subtopics")

if len(selected_languages) == 0:
    st.warning("Please select at least one language to display.")
elif len(selected_subtopics) == 0:
    st.warning("Please select at least one subtopic to display.")
else:
    # Prepare data for Plotly
    df_plot = df_filtered.copy()
    df_plot['language_name'] = df_plot['language_code'].map(lang_map)
    
    # Define color scheme
    color_map = {
        'Policy': '#1f77b4',
        'Adaptation': '#ff7f0e', 
        'Environment': '#2ca02c',
        'Science': '#d62728',
        'Sustainability': '#9467bd'
    }
    
    if chart_type == "Stacked Bar":
        fig = px.bar(
            df_plot,
            x='language_name',
            y='article_count',
            color='subtopic',
            title=f"Climate Change Articles by Language and Subtopic",
            labels={'language_name': 'Language', 'article_count': 'Number of Articles'},
            color_discrete_map=color_map,
            height=500
        )
        fig.update_layout(barmode='stack')
        
    elif chart_type == "Grouped Bar":
        fig = px.bar(
            df_plot,
            x='language_name',
            y='article_count',
            color='subtopic',
            title=f"Climate Change Articles by Language and Subtopic (Grouped)",
            labels={'language_name': 'Language', 'article_count': 'Number of Articles'},
            color_discrete_map=color_map,
            barmode='group',
            height=500
        )
        
    else:  # Percentage Stacked
        # Calculate percentages
        totals = df_plot.groupby('language_code')['article_count'].transform('sum')
        df_plot['percentage'] = (df_plot['article_count'] / totals * 100).round(1)
        
        fig = px.bar(
            df_plot,
            x='language_name',
            y='percentage',
            color='subtopic',
            title=f"Climate Change Article Distribution (Percentage) by Language",
            labels={'language_name': 'Language', 'percentage': 'Percentage of Articles'},
            color_discrete_map=color_map,
            height=500,
            text='percentage'
        )
        fig.update_layout(barmode='stack')
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='inside')
    
    fig.update_layout(
        xaxis_title="",
        font=dict(size=12),
        legend=dict(title="Subtopic", orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
    )
    
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("Summary Statistics")

col1, col2, col3 = st.columns(3)

with col1:
    total_articles = df_filtered['article_count'].sum()
    st.metric("Total Articles", f"{int(total_articles):,}")

with col2:
    num_languages = len(selected_languages)
    st.metric("Languages Analyzed", num_languages)

with col3:
    num_subtopics = len(selected_subtopics)
    st.metric("Subtopics Analyzed", num_subtopics)

# Detailed breakdown
with st.expander("Show Detailed Breakdown by Language"):
    st.markdown("### Articles by Language and Subtopic")
    
    # Create summary table
    summary_df = df_filtered.pivot_table(
        index='language_code',
        columns='subtopic',
        values='article_count',
        fill_value=0
    )
    summary_df['Total'] = summary_df.sum(axis=1)
    summary_df.index = summary_df.index.map(lambda x: f"{lang_map.get(x, x)} ({x})")
    
    st.dataframe(summary_df.style.format("{:.0f}"), use_container_width=True)


# Show subtopic keywords
with st.expander("Show Subtopic Keyword Definitions"):
    st.markdown("### Subtopic Classification Keywords")
    st.markdown("Articles were categorized into subtopics based on the presence of these keywords in their titles:")
    
    for subtopic in selected_subtopics:
        if subtopic in subtopic_mapping:
            st.markdown(f"**{subtopic}:**")
            
            # Show keywords for selected languages
            keywords_display = {}
            for lang_code in selected_languages:
                if lang_code in subtopic_mapping[subtopic]:
                    lang_name = lang_map.get(lang_code, lang_code)
                    keywords = ", ".join(subtopic_mapping[subtopic][lang_code])
                    keywords_display[lang_name] = keywords
            
            if keywords_display:
                st.write(keywords_display)
            st.markdown("")

# Show raw data
with st.expander("Show Raw Data"):
    st.markdown("### Raw Data Sample")
    display_df = df_filtered.copy()
    display_df['language_name'] = display_df['language_code'].map(lang_map)
    st.dataframe(
        display_df[['language_name', 'language_code', 'subtopic', 'article_count']]
        .sort_values(['language_code', 'subtopic']),
        use_container_width=True
    )

st.markdown("---")
# st.markdown("""
# **Methodology:** This analysis examined climate change-related Wikipedia articles 
# across the top 10 language editions by identifying articles whose titles contained 
# keywords related to five main subtopics: Policy, Adaptation, Environment, Science, 
# and Sustainability. The keyword lists were translated and adapted for each language 
# to capture culturally and linguistically appropriate terms.

# *Created by Beatrix Kim for CS 234 Final Project*
# """)