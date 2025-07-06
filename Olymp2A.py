#upgradation is needed have to add things in it to make it better#



import streamlit as st
import pandas as pd
import prep2A, helper
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff

# Load the data
df = pd.read_csv('athlete_events.csv')
region_df = pd.read_csv('noc_regions.csv')

# Preprocess the data
df = prep2A.preprocess(df, region_df)

# Streamlit sidebar setup
st.sidebar.title("Olympics Analysis")
st.sidebar.image(
    'https://assets.editorial.aetnd.com/uploads/2010/01/gettyimages-466313493-2.jpg')
user_menu = st.sidebar.radio(
    'Select an Option',
    ('Medal Tally', 'Overall Analysis', 'Country-wise Analysis', 'Athlete wise Analysis')
)

# Medal Tally Section
if user_menu == 'Medal Tally':
    st.sidebar.header("Medal Tally")
    years, country = helper.country_year_list(df)

    selected_year = st.sidebar.selectbox("Select Year", years)
    selected_country = st.sidebar.selectbox("Select Country", country)

    medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)

    # Title for the medal tally section
    if selected_year == 'Overall' and selected_country == 'Overall':
        st.title("Overall Tally")
    if selected_year != 'Overall' and selected_country == 'Overall':
        st.title("Medal Tally in " + str(selected_year) + " Olympics")
    if selected_year == 'Overall' and selected_country != 'Overall':
        st.title(selected_country + " overall performance")
    if selected_year != 'Overall' and selected_country != 'Overall':
        st.title(selected_country + " performance in " + str(selected_year) + " Olympics")

    st.table(medal_tally)

# Overall Analysis Section
if user_menu == 'Overall Analysis':
    editions = df['Year'].unique().shape[0] - 1
    cities = df['City'].unique().shape[0]
    sports = df['Sport'].unique().shape[0]
    events = df['Event'].unique().shape[0]
    athletes = df['Name'].unique().shape[0]
    nations = df['region'].unique().shape[0]

    # Displaying top statistics
    st.title("Top Statistics")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.header("Editions")
        st.title(editions)
    with col2:
        st.header("Hosts")
        st.title(cities)
    with col3:
        st.header("Sports")
        st.title(sports)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Events")
        st.title(events)
    with col2:
        st.header("Nations")
        st.title(nations)
    with col3:
        st.header("Athletes")
        st.title(athletes)

    # Participating Nations over the years
    nations_over_time = helper.data_over_time(df, 'region')
    fig = px.line(nations_over_time, x="Year", y="count")
    st.title("Participating Nations over the years")
    st.plotly_chart(fig)

    # Events over the years
    events_over_time = helper.data_over_time(df, 'Event')
    fig = px.line(events_over_time, x="Year", y="count")  # Fixed from "Edition" to "Year"
    st.title("Events over the years")
    st.plotly_chart(fig)

    # Athletes over the years
    athlete_over_time = helper.data_over_time(df, 'Name')
    fig = px.line(athlete_over_time, x="Year", y="count")  # Fixed from "Edition" to "Year"
    st.title("Athletes over the years")
    st.plotly_chart(fig)

    # No. of Events over time (Every Sport)
    st.title("No. of Events over time (Every Sport)")
    fig, ax = plt.subplots(figsize=(20, 20))
    x = df.drop_duplicates(['Year', 'Sport', 'Event'])
    ax = sns.heatmap(
        x.pivot_table(index='Sport', columns='Year', values='Event', aggfunc='count').fillna(0).astype('int'),
        annot=True)
    st.pyplot(fig)

    # Most successful Athletes
    st.title("Most successful Athletes")
    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'Overall')

    selected_sport = st.selectbox('Select a Sport', sport_list)
    x = helper.most_successful(df, selected_sport)
    st.table(x)

# Country-wise Analysis Section

if user_menu == 'Country-wise Analysis':
    st.sidebar.title('Country-wise Analysis')

    # Dropdown for country selection
    country_list = df['region'].dropna().unique().tolist()
    country_list.sort()

    selected_country = st.sidebar.selectbox('Select a Country', country_list)

    # 1. Medal Tally over the Years
    st.title(f"{selected_country} Medal Tally Over the Years")

    # Filter the data for the selected country and non-null medals
    country_df = df[(df['region'] == selected_country) & (df['Medal'].notna())]

    if not country_df.empty:
        # Group by year and count the number of medals won each year
        medal_tally_df = country_df.groupby('Year').size().reset_index(name='Medal Count')

        # Line plot for medal tally over the years
        fig = px.line(medal_tally_df, x="Year", y="Medal Count",
                      title=f"{selected_country} Medal Tally Over the Years",
                      labels={"Medal Count": "Number of Medals"})  # Renaming the label for clarity
        st.plotly_chart(fig)
    else:
        st.warning(f"No medal tally data available for {selected_country}.")

    # 2. Sports where the selected country excels (Sunburst Chart)
    st.title(f"Sports {selected_country} Excels In")

    # Prepare data for the sunburst chart
    sports_sunburst_data = df[(df['region'] == selected_country) & (df['Medal'].notna())]

    if not sports_sunburst_data.empty:
        sports_sunburst_data['Count'] = 1  # Adding a column for count of medals

        sunburst_fig = px.sunburst(
            sports_sunburst_data,
            path=['Sport', 'Event', 'Medal'],  # Hierarchical path
            values='Count',  # Use 'Count' as values to measure medal occurrences
            title=f'{selected_country} Performance in Sports (Sunburst Chart)',
            color='Sport',  # Color by sport category
            hover_data=['Medal'],  # Show medal type on hover
            color_discrete_sequence=px.colors.qualitative.Pastel,

            height=800,
            width=800


        )
        st.plotly_chart(sunburst_fig, use_container_width=True)
    else:
        st.warning(f"No performance data available for {selected_country}'s sports.")

    # 3. Top 10 Athletes of the Selected Country
    st.title(f"Top 10 Athletes from {selected_country}")

    # Fetch top 10 athletes data
    top10_df = helper.most_successful_countrywise(df, selected_country)

    if not top10_df.empty:
        st.table(top10_df)
    else:
        st.warning(f"No athlete data available for {selected_country}.")


# Athlete-wise Analysis Section
if user_menu == 'Athlete wise Analysis':
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])

    # Define sport_list here
    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'Overall')

    # Distribution of Age
    x1 = athlete_df['Age'].dropna()
    x2 = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna()
    x3 = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna()
    x4 = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()

    fig = ff.create_distplot([x1, x2, x3, x4], ['Overall Age', 'Gold Medalist', 'Silver Medalist', 'Bronze Medalist'],
                             show_hist=False, show_rug=False)
    fig.update_layout(autosize=False, width=1000, height=600)
    st.title("Distribution of Age")
    st.plotly_chart(fig)

    # Distribution of Age with respect to Sports (Gold Medalist)
    x = []
    name = []
    famous_sports = ['Basketball', 'Judo', 'Football', 'Tug-Of-War', 'Athletics',
                     'Swimming', 'Badminton', 'Sailing', 'Gymnastics',
                     'Art Competitions', 'Handball', 'Weightlifting', 'Wrestling',
                     'Water Polo', 'Hockey', 'Rowing', 'Fencing',
                     'Shooting', 'Boxing', 'Taekwondo', 'Cycling', 'Diving', 'Canoeing',
                     'Tennis', 'Golf', 'Softball', 'Archery',
                     'Volleyball', 'Synchronized Swimming', 'Table Tennis', 'Baseball',
                     'Rhythmic Gymnastics', 'Rugby Sevens',
                     'Beach Volleyball', 'Triathlon', 'Rugby', 'Polo', 'Ice Hockey']
    for sport in famous_sports:
        temp_df = athlete_df[athlete_df['Sport'] == sport]
        x.append(temp_df[temp_df['Medal'] == 'Gold']['Age'].dropna())
        name.append(sport)

    fig = ff.create_distplot(x, name, show_hist=False, show_rug=False)
    fig.update_layout(autosize=False, width=1000, height=600)
    st.title("Distribution of Age with respect to Sports (Gold Medalist)")
    st.plotly_chart(fig)

    # Height vs Weight analysis
    st.title('Height Vs Weight')
    selected_sport = st.selectbox('Select a Sport', sport_list)  # Ensure sport_list is defined
    temp_df = helper.weight_v_height(df, selected_sport)

    # Create a pair plot for Height vs Weight
    pair_plot_data = temp_df[['Weight', 'Height', 'Sex']].dropna()  # Ensure there are no NaN values

    # Create pair plot
    fig = sns.pairplot(pair_plot_data, hue='Sex', diag_kind='kde')
    st.pyplot(fig)

    # Men vs Women Participation Over the Years
    st.title("Men Vs Women Participation Over the Years")
    final = helper.men_vs_women(df)
    fig = px.line(final, x="Year", y=["Male", "Female"])
    fig.update_layout(autosize=False, width=1000, height=600)
    st.plotly_chart(fig)
