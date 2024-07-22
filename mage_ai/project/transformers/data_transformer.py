import pandas as pd
if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def transform(data, *args, **kwargs):
    """
    Template code for a transformer block.

    Add more parameters to this function if this block has multiple parent blocks.
    There should be one parameter for each output variable from each parent block.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    df = data

    # Filter data
    tr = 'time_referred'
    tp = 'time_procured'
    format = '%Y-%m-%d %H:%M:%S.%f'
    df_sub = df.loc[df[tp].notnull() & df[tr].notnull()].copy()

    # Convert time columns to datetime
    df_sub['tr_time_format'] = pd.to_datetime(df_sub[tr], format=format)
    df_sub['tp_time_format'] = pd.to_datetime(df_sub[tp], format=format)

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


    return df_model


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
