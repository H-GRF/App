
import pandas as pd
#import matplotlib.pyplot as plt
import sys
sys.path.append('..')
import config as c

## Loading the data
def load_weather_data(dept: str) -> pd.DataFrame:
    """Load weather data from a CSV file.

    Args:
        file_path (str): Path to the CSV file.
    """

    path = f"https://object.files.data.gouv.fr/meteofrance/data/synchro_ftp/BASE/QUOT/Q_{dept}_previous-1950-2023_RR-T-Vent.csv.gz"
    
    d = {
    'NUM_POSTE': 'string',
    'NOM_USUEL': 'string',
    'LAT': 'string',
    'LON': 'string',
    'ALTI': 'string',
    'AAAAMMJJ': 'string',
    'TN': 'string',
    'TNSOL': 'string',
    'TN50': 'string',
    }

    df = pd.read_csv(path,
                    compression='gzip',
                    sep=';',
                    dtype=d,
                    usecols=d.keys(),)

    df['AAAAMMJJ'] = pd.to_datetime(df['AAAAMMJJ'], format='%Y%m%d')
    df = df.loc[df['AAAAMMJJ'].dt.year.between(c.START_YEAR, c.END_YEAR)]
    return df