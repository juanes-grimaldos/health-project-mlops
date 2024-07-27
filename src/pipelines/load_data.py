import io
import pandas as pd
import requests
import logging
import os
import subprocess

def load_and_preprocess_data() -> pd.DataFrame:
    """
    Load and preprocess data from a CSV file.

    Returns:
        pandas.DataFrame: The preprocessed DataFrame containing filtered and 
        transformed data.
    """
    url = "https://physionet.org/files/orchid/2.0.0/referrals.csv?download"
    cookies = os.getenv("COOKIE_API_REQUEST")
    headers = {
        'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
        'Referer': 'https://physionet.org/content/orchid/2.0.0/',
        'Cookie': cookies,
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Priority': 'u=0, i',
        'TE': 'trailers'
    }

    response = requests.request("GET", url, headers=headers)
    if response.status_code == 200:
        logging.info("File downloaded successfully.")
        df = pd.read_csv(io.StringIO(response.text), sep=',')
        df_pre = preprocess_data(df)
        return df_pre
    elif response.status_code == 403:
        logging.error("403 Forbidden error. Trying with a different method.")
        if cookies is None:
            logging.error("Environment variable"
                          "COOKIE_API_REQUEST must be set.")
        return fallback_download()
    else:
        response.raise_for_status()


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess the data by filtering and transforming it.
    
    Args:
        df (pd.DataFrame): The input DataFrame.
        
    Returns:
        pd.DataFrame: The preprocessed DataFrame.
    """

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

def fallback_download() -> pd.DataFrame:
    """
    Fallback function to download the CSV file using wget and 
    load it into a pandas DataFrame.

    Returns:
        pandas.DataFrame: The DataFrame containing the data from the 
        downloaded CSV file.
    """
    url = "https://physionet.org/files/orchid/2.0.0/referrals.csv"
    output_file = "referrals.csv"

    # Retrieve the username and password from environment variables
    username = os.getenv("PHYSIONET_USERNAME")
    password = os.getenv("PHYSIONET_PASSWORD")

    if username is None or password is None:
        logging.error("Environment variables "
                      "PHYSIONET_USERNAME and PHYSIONET_PASSWORD must be set.")
        raise ValueError(
            "Environment variables PHYSIONET_USERNAME "
            " and PHYSIONET_PASSWORD must be set")

    # Run the wget command to download the file
    command = f'wget --user="{username}" --password="{password}" "{url}" -O {output_file}'
    subprocess.run(command, shell=True, check=True)
    
    # Load the CSV file into a Pandas DataFrame
    df = pd.read_csv(output_file)
    df_pre = preprocess_data(df)
    return df_pre

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
    )
    load_and_preprocess_data()