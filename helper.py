#helper file#


import numpy as np


def fetch_medal_tally(df, year, country):
    medal_df = df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])
    flag = 0
    if year == 'Overall' and country == 'Overall':
        temp_df = medal_df
    elif year == 'Overall' and country != 'Overall':
        flag = 1
        temp_df = medal_df[medal_df['region'] == country]
    elif year != 'Overall' and country == 'Overall':
        temp_df = medal_df[medal_df['Year'] == int(year)]
    else:
        temp_df = medal_df[(medal_df['Year'] == int(year)) & (medal_df['region'] == country)]

    if flag == 1:
        x = temp_df.groupby('Year').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Year').reset_index()
    else:
        x = temp_df.groupby('region').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Gold',
                                                                                      ascending=False).reset_index()

    x['total'] = x['Gold'] + x['Silver'] + x['Bronze']
    x[['Gold', 'Silver', 'Bronze', 'total']] = x[['Gold', 'Silver', 'Bronze', 'total']].astype(int)
    return x


def country_year_list(df):
    years = df['Year'].unique().tolist()
    years.sort()
    years.insert(0, 'Overall')

    countries = np.unique(df['region'].dropna().values).tolist()
    countries.sort()
    countries.insert(0, 'Overall')

    return years, countries


def data_over_time(df, col):
    # Drop duplicates based on 'Year' and the specified column
    nations_over_time = df.drop_duplicates(['Year', col])

    # Count occurrences of each year
    count_df = nations_over_time['Year'].value_counts().reset_index()
    count_df.columns = ['Year', 'count']  # Rename columns for clarity

    # Sort the DataFrame by 'Year'
    count_df = count_df.sort_values('Year')

    return count_df


def yearwise_medal_tally(df, country):
    temp_df = df.dropna(subset=['Medal'])
    temp_df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'], inplace=True)
    new_df = temp_df[temp_df['region'] == country]
    final_df = new_df.groupby('Year').count()['Medal'].reset_index()
    return final_df


def most_successful_countrywise(df, country):
    temp_df = df.dropna(subset=['Medal'])
    temp_df = temp_df[temp_df['region'] == country]
    x = temp_df['Name'].value_counts().reset_index().head(10)
    x.columns = ['Name', 'Count']
    merged_df = x.merge(df, left_on='Name', right_on='Name', how='left')[
        ['Name', 'Count', 'Sport', 'Medal']].drop_duplicates('Name')
    return merged_df


# New Function to Get Most Successful Athletes
def most_successful(df, sport):
    if sport != 'Overall':
        temp_df = df[df['Sport'] == sport]
    else:
        temp_df = df

    # Group by Name and count medals
    most_successful_df = temp_df[temp_df['Medal'].notnull()].groupby('Name').count()['Medal'].reset_index()
    most_successful_df.columns = ['Name', 'Medal Count']

    # Sort by Medal Count and get top athletes
    most_successful_df = most_successful_df.sort_values(by='Medal Count', ascending=False).head(10)

    # Merge with original DataFrame to get Sport and Medal details
    most_successful_df = most_successful_df.merge(df[['Name', 'Sport', 'Medal']], on='Name',
                                                  how='left').drop_duplicates('Name')

    return most_successful_df


def weight_v_height(df, sport):
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])
    athlete_df['Medal'].fillna('No Medal', inplace=True)
    if sport != 'Overall':
        temp_df = athlete_df[athlete_df['Sport'] == sport]
        return temp_df
    else:
        return athlete_df


def country_event_heatmap(df, selected_country):
    temp_df = df.dropna(subset=['Medal'])  # Remove rows without medals
    temp_df = temp_df[temp_df['region'] == selected_country]  # Filter for the selected country
    pt = temp_df.pivot_table(index='Sport', columns='Year', values='Medal', aggfunc='count').fillna(0)
    return pt


def men_vs_women(df, selected_sport='Overall'):
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])

    # Applying sport filter
    if selected_sport != 'Overall':
        athlete_df = athlete_df[athlete_df['Sport'] == selected_sport]

    men = athlete_df[athlete_df['Sex'] == 'M'].groupby('Year').count()['Name'].reset_index()
    women = athlete_df[athlete_df['Sex'] == 'F'].groupby('Year').count()['Name'].reset_index()

    final = men.merge(women, on='Year', how='left')
    final.rename(columns={'Name_x': 'Male', 'Name_y': 'Female'}, inplace=True)
    final.fillna(0, inplace=True)

    return final
