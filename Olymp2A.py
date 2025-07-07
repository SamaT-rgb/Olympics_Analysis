#still have to check athlete.csv for better work

import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff
from preprocess import preprocess
from helper import (fetch_medal_tally, country_year_list, data_over_time,
                   yearwise_medal_tally, most_successful, most_successful_countrywise,
                   weight_v_height, country_event_heatmap, men_vs_women)

@st.cache_data
def load_data():
    """Load and preprocess the Olympic data."""
    try:
        df = pd.read_csv('athlete_events.csv')
        region_df = pd.read_csv('noc_regions.csv')
        return preprocess(df, region_df)
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def main():
    # Page configuration
    st.set_page_config(page_title="Olympics Analysis Dashboard", layout="wide")

    # Load data
    with st.spinner("Loading data..."):
        df = load_data()

    if df.empty:
        st.error("Failed to load data. Please check the data files.")
        return

    # Sidebar setup
    st.sidebar.title("Olympics Analysis Dashboard")
    st.sidebar.image(
        'https://assets.editorial.aetnd.com/uploads/2010/01/gettyimages-466313493-2.jpg',
        use_column_width=True
    )
    user_menu = st.sidebar.radio(
        'Select an Option',
        ('Medal Tally', 'Overall Analysis', 'Country-wise Analysis', 'Athlete-wise Analysis')
    )

    # Medal Tally Section
    if user_menu == 'Medal Tally':
        st.header("Medal Tally")
        years, countries = country_year_list(df)

        with st.sidebar:
            selected_year = st.selectbox("Select Year", years)
            selected_country = st.selectbox("Select Country", countries)

        with st.spinner("Calculating medal tally..."):
            medal_tally = fetch_medal_tally(df, selected_year, selected_country)

        title = f"{selected_country} performance in {selected_year} Olympics" if selected_year != 'Overall' and selected_country != 'Overall' else \
                f"{selected_country} overall performance" if selected_year == 'Overall' and selected_country != 'Overall' else \
                f"Medal Tally in {selected_year} Olympics" if selected_year != 'Overall' else "Overall Tally"
        st.title(title)

        if not medal_tally.empty:
            st.dataframe(medal_tally, use_container_width=True)
        else:
            st.warning("No medal data available for the selected combination.")

    # Overall Analysis Section
    if user_menu == 'Overall Analysis':
        st.title("Overall Olympic Analysis")

        editions = df['Year'].unique().shape[0] - 1
        cities = df['City'].unique().shape[0]
        sports = df['Sport'].unique().shape[0]
        events = df['Event'].unique().shape[0]
        athletes = df['Name'].unique().shape[0]
        nations = df['region'].unique().shape[0]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Editions", editions)
            st.metric("Events", events)
        with col2:
            st.metric("Hosts", cities)
            st.metric("Nations", nations)
        with col3:
            st.metric("Sports", sports)
            st.metric("Athletes", athletes)

        with st.spinner("Generating visualizations..."):
            st.subheader("Participating Nations Over Time")
            nations_over_time = data_over_time(df, 'region')
            fig = px.line(nations_over_time, x="Year", y="count", title="Participating Nations")
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Events Over Time")
            events_over_time = data_over_time(df, 'Event')
            fig = px.line(events_over_time, x="Year", y="count", title="Events")
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Athletes Over Time")
            athlete_over_time = data_over_time(df, 'Name')
            fig = px.line(athlete_over_time, x="Year", y="count", title="Athletes")
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Events by Sport Over Time")
            fig, ax = plt.subplots(figsize=(20, 20))
            x = df.drop_duplicates(['Year', 'Sport', 'Event'])
            sns.heatmap(
                x.pivot_table(index='Sport', columns='Year', values='Event', aggfunc='count').fillna(0).astype('int'),
                annot=True, fmt='d', cmap='YlOrRd'
            )
            st.pyplot(fig)

            st.subheader("Most Successful Athletes")
            sport_list = ['Overall'] + sorted(df['Sport'].unique().tolist())
            selected_sport = st.selectbox('Select a Sport', sport_list, index=0)
            x = most_successful(df, selected_sport)
            if not x.empty:
                st.dataframe(x, use_container_width=True)
            else:
                st.warning(f"No successful athletes data available for {selected_sport}. Check if the sport has medal data.")

    # Country-wise Analysis Section
    if user_menu == 'Country-wise Analysis':
        st.sidebar.header('Country-wise Analysis')
        country_list = ['Overall'] + sorted(df['region'].dropna().unique().tolist())
        selected_country = st.sidebar.selectbox('Select a Country', country_list)

        if selected_country != 'Overall':
            st.subheader(f"{selected_country} Medal Tally")
            medal_tally_df = yearwise_medal_tally(df, selected_country)
            if not medal_tally_df.empty:
                fig = px.line(medal_tally_df, x="Year", y="Medal", title=f"{selected_country} Medal Tally")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"No medal data available for {selected_country}")

            st.subheader(f"{selected_country} Sports Performance")
            sports_data = df.loc[(df['region'] == selected_country) & (df['Medal'].notna())].copy()
            if not sports_data.empty:
                fig = px.sunburst(
                    sports_data, path=['Sport', 'Event', 'Medal'], values='Medal_Gold',
                    title=f'{selected_country} Performance in Sports',
                    height=600
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"No sports performance data available for {selected_country}")

            st.subheader(f"Top Athletes from {selected_country}")
            top10_df = most_successful_countrywise(df, selected_country)
            if not top10_df.empty:
                st.dataframe(top10_df, use_container_width=True)
            else:
                st.warning(f"No top athletes data available for {selected_country}")

    # Athlete-wise Analysis Section
    if user_menu == 'Athlete-wise Analysis':
        st.title("Athlete Analysis")

        st.subheader("Age Distribution of Athletes")
        athlete_df = df.drop_duplicates(subset=['Name', 'region'])
        x1 = athlete_df['Age'].dropna()
        x2 = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna()
        x3 = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna()
        x4 = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()

        fig = ff.create_distplot(
            [x1, x2, x3, x4],
            ['Overall Age', 'Gold Medalist', 'Silver Medalist', 'Bronze Medalist'],
            show_hist=False, show_rug=False
        )
        fig.update_layout(width=1000, height=600)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Age Distribution by Sport (Gold Medalists)")
        famous_sports = sorted([
            'Basketball', 'Judo', 'Football', 'Tug-Of-War', 'Athletics',
            'Swimming', 'Badminton', 'Sailing', 'Gymnastics', 'Handball',
            'Weightlifting', 'Wrestling', 'Water Polo', 'Hockey', 'Rowing',
            'Fencing', 'Shooting', 'Boxing', 'Taekwondo', 'Cycling', 'Diving',
            'Canoeing', 'Tennis', 'Golf', 'Softball', 'Archery', 'Volleyball',
            'Synchronized Swimming', 'Table Tennis', 'Baseball', 'Rhythmic Gymnastics',
            'Rugby Sevens', 'Beach Volleyball', 'Triathlon', 'Rugby', 'Polo', 'Ice Hockey'
        ])
        x = [athlete_df[athlete_df['Sport'] == sport][athlete_df['Medal'] == 'Gold']['Age'].dropna()
             for sport in famous_sports]
        fig = ff.create_distplot(x, famous_sports, show_hist=False, show_rug=False)
        fig.update_layout(width=1000, height=600)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader('Height vs Weight Analysis')
        sport_list = ['Overall'] + sorted(df['Sport'].unique().tolist())
        selected_sport = st.selectbox('Select a Sport', sport_list)
        temp_df = weight_v_height(df, selected_sport)
        if not temp_df.empty:
            plot_df = temp_df.dropna(subset=['Age', 'Weight', 'Height'])
            if not plot_df.empty:
                fig = px.scatter(
                    plot_df,
                    x='Weight',
                    y='Height',
                    color='Medal',
                    size=plot_df['Age'].clip(lower=1),
                    hover_data=['Name', 'Sport'],
                    title=f'Height vs Weight ({selected_sport})',
                    size_max=20
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"No valid data available for Height vs Weight analysis in {selected_sport}")
        else:
            st.warning(f"No data available for {selected_sport}")

        st.subheader("Men vs Women Participation")
        final = men_vs_women(df, selected_sport)
        fig = px.line(final, x="Year", y=["Male", "Female"],
                     title="Men vs Women Participation Over Time")
        fig.update_layout(width=1000, height=600)
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
