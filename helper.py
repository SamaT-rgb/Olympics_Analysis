import numpy as np
import pandas as pd

def fetch_medal_tally(df, year, country):
    """
    Fetch medal tally for a given year and country.

    Args:
        df: DataFrame containing Olympic data
        year: Specific year or 'Overall'
        country: Specific country or 'Overall'

    Returns:
        DataFrame with medal tally
    """
    try:
        # Validate required columns
        required_cols = ['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal', 'region']
        if not all(col in df.columns for col in required_cols):
            raise ValueError("Missing required columns in DataFrame")

        medal_df = df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])

        flag = 0
        if year == 'Overall' and country == 'Overall':
            temp_df = medal_df
        elif year == 'Overall':
            flag = 1
            temp_df = medal_df[medal_df['region'] == country]
        elif country == 'Overall':
            temp_df = medal_df[medal_df['Year'] == int(year)]
        else:
            temp_df = medal_df[(medal_df['Year'] == int(year)) & (medal_df['region'] == country)]

        # Use one-hot encoded medal columns
        medal_columns = ['Medal_Gold', 'Medal_Silver', 'Medal_Bronze']
        if not all(col in df.columns for col in medal_columns):
            raise ValueError("Missing one-hot encoded medal columns (Medal_Gold, Medal_Silver, Medal_Bronze)")

        if flag == 1:
            x = temp_df.groupby('Year').sum()[medal_columns].sort_values('Year').reset_index()
        else:
            x = temp_df.groupby('region').sum()[medal_columns].sort_values('Medal_Gold', ascending=False).reset_index()

        # Rename columns to match expected output
        x = x.rename(columns={'Medal_Gold': 'Gold', 'Medal_Silver': 'Silver', 'Medal_Bronze': 'Bronze'})
        x['total'] = x['Gold'] + x['Silver'] + x['Bronze']
        x[['Gold', 'Silver', 'Bronze', 'total']] = x[['Gold', 'Silver', 'Bronze', 'total']].astype(int)

        return x if not x.empty else pd.DataFrame(columns=['Year', 'region', 'Gold', 'Silver', 'Bronze', 'total'])
    except Exception as e:
        print(f"Error in fetch_medal_tally: {str(e)}")
        return pd.DataFrame()

def country_year_list(df):
    """
    Get unique years and countries from the DataFrame.

    Returns:
        tuple: (sorted years list with 'Overall', sorted countries list with 'Overall')
    """
    try:
        years = df['Year'].unique().tolist()
        years.sort()
        years.insert(0, 'Overall')

        countries = np.unique(df['region'].dropna().values).tolist()
        countries.sort()
        countries.insert(0, 'Overall')

        return years, countries
    except Exception as e:
        print(f"Error in country_year_list: {str(e)}")
        return [], []

def data_over_time(df, col):
    """
    Calculate data distribution over time for a specific column.

    Args:
        df: Input DataFrame
        col: Column to analyze

    Returns:
        DataFrame with year-wise counts
    """
    try:
        if col not in df.columns:
            raise ValueError(f"Column {col} not found in DataFrame")
        nations_over_time = df.drop_duplicates(['Year', col])
        count_df = nations_over_time['Year'].value_counts().reset_index()
        count_df.columns = ['Year', 'count']
        return count_df.sort_values('Year')
    except Exception as e:
        print(f"Error in data_over_time: {str(e)}")
        return pd.DataFrame()

def yearwise_medal_tally(df, country):
    """
    Get year-wise medal tally for a specific country.

    Args:
        df: Input DataFrame
        country: Country name

    Returns:
        DataFrame with year-wise medal counts
    """
    try:
        temp_df = df[df['Medal'].notnull()].drop_duplicates(
            subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])
        new_df = temp_df[temp_df['region'] == country]
        final_df = new_df.groupby('Year').count()['Medal'].reset_index()
        return final_df
    except Exception as e:
        print(f"Error in yearwise_medal_tally: {str(e)}")
        return pd.DataFrame()

def most_successful_countrywise(df, country):
    """
    Get most successful athletes for a specific country.

    Args:
        df: Input DataFrame
        country: Country name

    Returns:
        DataFrame with top 10 athletes
    """
    try:
        temp_df = df[df['Medal'].notnull() & (df['region'] == country)]
        x = temp_df['Name'].value_counts().reset_index().head(10)
        x.columns = ['Name', 'Count']
        merged_df = x.merge(df[['Name', 'Sport', 'Medal']], on='Name', how='left').drop_duplicates('Name')
        return merged_df[['Name', 'Count', 'Sport', 'Medal']]
    except Exception as e:
        print(f"Error in most_successful_countrywise: {str(e)}")
        return pd.DataFrame()

def most_successful(df, sport):
    """
    Get most successful athletes for a specific sport or overall.

    Args:
        df: Input DataFrame
        sport: Sport name or 'Overall'

    Returns:
        DataFrame with top 10 athletes
    """
    try:
        temp_df = df[df['Sport'] == sport] if sport != 'Overall' else df
        most_successful_df = temp_df[temp_df['Medal'].notnull()].groupby('Name').count()['Medal'].reset_index()
        most_successful_df.columns = ['Name', 'Medal Count']
        most_successful_df = most_successful_df.sort_values(by='Medal Count', ascending=False).head(10)
        most_successful_df = most_successful_df.merge(df[['Name', 'Sport', 'Medal']], on='Name',
                                                      how='left').drop .duplicates('Name')
        return most_successful_df
    except Exception as e:
        print(f"Error in most_successful: {str(e)}")
        return pd.DataFrame()

def weight_v_height(df, sport):
    """
    Get height vs weight data for athletes.

    Args:
        df: Input DataFrame
        sport: Sport name or 'Overall'

    Returns:
        DataFrame with height and weight data
    """
    try:
        athlete_df = df.drop_duplicates(subset=['Name', 'region'])
        athlete_df['Medal'] = athlete_df['Medal'].fillna('No Medal')
        return athlete_df[athlete_df['Sport'] == sport] if sport != 'Overall' else athlete_df
    except Exception as e:
        print(f"Error in weight_v_height: {str(e)}")
        return pd.DataFrame()

def country_event_heatmap(df, selected_country):
    """
    Create a heatmap of events for a specific country.

    Args:
        df: Input DataFrame
        selected_country: Country name

    Returns:
        Pivot table with event counts
    """
    try:
        temp_df = df[df['Medal'].notnull() & (df['region'] == selected_country)]
        pt = temp_df.pivot_table(index='Sport', columns='Year', values='Medal', aggfunc='count').fillna(0).astype(int)
        return pt
    except Exception as e:
        print(f"Error in country_event_heatmap: {str(e)}")
        return pd.DataFrame()

def men_vs_women(df, selected_sport='Overall'):
    """
    Compare male vs female participation over time.

    Args:
        df: Input DataFrame
        selected_sport: Sport name or 'Overall'

    Returns:
        DataFrame with male and female participation counts
    """
    try:
        athlete_df = df.drop_duplicates(subset=['Name', 'region'])
        if selected_sport != 'Overall':
            athlete_df = athlete_df[athlete_df['Sport'] == selected_sport]

        men = athlete_df[athlete_df['Sex'] == 'M'].groupby('Year').count()['Name'].reset_index()
        women = athlete_df[athlete_df['Sex'] == 'F'].groupby('Year').count()['Name'].reset_index()

        final = men.merge(women, on='Year', how='left')
        final.rename(columns={'Name_x': 'Male', 'Name_y': 'Female'}, inplace=True)
        final.fillna(0, inplace=True)

        return final
    except Exception as e:
        print(f"Error in men_vs_women: {str(e)}")
        return pd.DataFrame()
