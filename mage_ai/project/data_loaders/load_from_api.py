import io
import pandas as pd
import requests
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_loader
def load_data_from_api(*args, **kwargs):
    """
    Template for loading data from API
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

    return pd.read_csv(io.StringIO(response.text), sep=',')


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
