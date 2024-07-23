import io
import pandas as pd
import requests

def load_and_preprocess_data() -> pd.DataFrame:
    """
    Load and preprocess data from a CSV file.

    Returns:
        pandas.DataFrame: The preprocessed DataFrame containing filtered and transformed data.
    """
    url = "https://physionet.org/files/orchid/2.0.0/referrals.csv?download"
    payload = {}
    headers = {
    'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
    'Referer': 'https://physionet.org/content/orchid/2.0.0/',
    'Cookie': '_ga=GA1.2.263637740.1720827977; _gid=GA1.2.568479628.1720827977; _ga_YKC8ZQQ4FF=GS1.1.1720884389.2.0.1720884389.0.0.0; sessionid=mhqb7hzqqd5wr3czmywgzkgmd6ofynfq; csrftoken=WMtkvE71RGbcaSwET3WXCsuq5lAJdXMM',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Priority': 'u=0, i'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    df = pd.read_csv(io.StringIO(response.text), sep=',')

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
