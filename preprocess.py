import pandas as pd

def preprocess(df, region_df):
    """
    Preprocess Olympic data by filtering and merging with region data.

    Args:
        df: Athlete events DataFrame
        region_df: NOC regions DataFrame

    Returns:
        Processed DataFrame
    """
    try:
        # Input validation
        if df.empty or region_df.empty:
            raise ValueError("Input DataFrames cannot be empty")

        required_cols = ['Season', 'NOC', 'Medal']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"Missing required columns: {', '.join(set(required_cols) - set(df.columns))}")

        # Filter for Summer Olympics
        processed_df = df[df['Season'] == 'Summer'].copy()

        # Merge with region_df
        processed_df = processed_df.merge(region_df, on='NOC', how='left')

        # Drop duplicates
        processed_df = processed_df.drop_duplicates()

        # One-hot encoding medals with explicit column names
        medal_dummies = pd.get_dummies(processed_df['Medal'], prefix='Medal')
        processed_df = pd.concat([processed_df, medal_dummies], axis=1)

        # Ensure numeric columns
        numeric_cols = ['Age', 'Height', 'Weight', 'Year']
        for col in numeric_cols:
            if col in processed_df.columns:
                processed_df[col] = pd.to_numeric(processed_df[col], errors='coerce')

        return processed_df

    except Exception as e:
        print(f"Error in preprocessing: {str(e)}")
        return pd.DataFrame()
