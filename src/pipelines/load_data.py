import pandas as pd



def load_and_preprocess_data() -> pd.DataFrame:
    """
    Load and preprocess data from a CSV file.

    Returns:
        pandas.DataFrame: The preprocessed DataFrame containing filtered and transformed data.
    """
    # Load data from CSV file
    df = pd.read_csv('data/referrals.csv')

    # Filter data
    tr = 'time_referred'
    tp = 'time_procured'
    df_sub = df.loc[df[tp].notnull() & df[tr].notnull()].copy()

    # Convert time columns to datetime
    df_sub['tr_time_format'] = pd.to_datetime(df_sub[tr], format='ISO8601')
    df_sub['tp_time_format'] = pd.to_datetime(df_sub[tp], format='ISO8601')

    # Calculate time to procurement
    tr_t ='tr_time_format'
    tp_t = 'tp_time_format'
    df_sub['time_to_procurement'] = (df_sub[tp_t] - df_sub[tr_t]).dt.days

    # Filter data for modeling
    df_model = df_sub.loc[
        (df_sub['time_to_procurement'] <= 20) & 
        (df_sub['time_to_procurement'] > 0) # one negative value
    ].copy()

    # Create blood type column
    new_column = 'blood_type'
    df_model[new_column] = df_model['ABO_BloodType'] + '-' + df_model['ABO_Rh']

    # Return the preprocessed DataFrame
    return df_model