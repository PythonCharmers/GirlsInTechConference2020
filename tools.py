"""
Supporting module for the presentation:

    Joy of Tech - Python Coding

by Ed Schofield on September 9th, 2020

Copyright (c) 2020 Python Charmers

License: Creative Commons BY-NC-SA 3.0: https://creativecommons.org/licenses/by-nc-sa/3.0/

Usage instructions:
    1. Install Python via Anaconda
    2. Install the dependencies:

    From the Terminal (macOS) or Anaconda Prompt (Windows), run:

    pip install -r requirements.txt

    3. To follow along with the weather API example, sign up for a (free) API
       key from OpenWeatherMap.org and enter it below.

    4. To following along with the SMS / MMS API example, sign up for a (free
       trial) API key from dev.telstra.com and enter it at the top of
       messaging.py.
"""
# Example:
# weather_api_key = '93d1ca18ad905ac3e5c2044147c97d25'
weather_api_key = '...'

class UsageError(Exception):
    """
    Usage help
    """

usage_help = """The OpenWeatherMap API did not return a result.

To following along with the real-time weather example, sign up for an API key first at https://openweathermap.org and enter your weather_api_key at the top of tools.py."""

# For Ed's live talk: look up Ed's saved credentials:
if weather_api_key == '...':
    try:
        import keyring
        from getpass import getuser
        weather_api_key = keyring.get_password('openweathermap_api_key', getuser())
    except:
        raise UsageError(usage_help)


import matplotlib.pyplot as plt
import toolz as tz
import pandas as pd
import altair
import numpy as np
import requests
from IPython.display import Image


altair.data_transformers.disable_max_rows()


# URL for the OpenWeatherMap API. See here: https://openweathermap.org/current
weather_url = 'https://api.openweathermap.org/data/2.5/weather'


def cleanup_countries(all_countries):
    countries_df = pd.DataFrame(all_countries)
    new = countries_df.copy()
    def get_income(cell):
        return cell['value']
    new['incomelevel'] = new['incomeLevel'].apply(get_income)
    newer = (new
             .rename(columns={'capitalCity': 'capital'})
             .drop(columns=['region', 'adminregion', 'incomeLevel', 'lendingType'])
            )

    # Delete any rows without a capital, longitude, or latitude
    criterion1 = (newer['capital'] != '')
    criterion2 = (newer['longitude'] != '')
    criterion3 = (newer['latitude'] != '')

    newest = newer[criterion1 & criterion2 & criterion3].copy()
    newest['longitude'] = newest['longitude'].astype(float)
    newest['latitude'] = newest['latitude'].astype(float)

    # Create a column that colors by income level
    colors = ['green', 'darkred', 'red', 'orange']
    levels = list(newest['incomelevel'].unique())
    def level_to_color(incomelevel):
        return colors[levels.index(incomelevel)]
    newest['color'] = newest['incomelevel'].map(level_to_color)
    return newest


@tz.memoize
def countries_as_dataframe(cities_string: str):
    """
    Convert a multi-line string of cities like this:

    Melbourne, Australia
    Singapore,Singapore
    San Francisco, USA

    into a DataFrame with these columns:

    City,Country,Country Code

    by looking up the 2-letter country code in ~/Data/countries.csv
    """
    countries_list = cities.replace(', ', ',').strip().splitlines()


def prep_countries_data():
    all_countries = pd.read_csv('~/Data/countries.csv')

    cols = ['name', '2 letter ISO abbreviation', 'capital']

    all_countries_clean = all_countries[cols].rename(
        columns={'2 letter ISO abbreviation': 'Country Code',
                 'capital': 'Capital',
                 'name': 'Country'}
    ).set_index(
        'Country'
    )
    all_countries_clean.to_hdf('countries.h5', index=False, key='countries')


def show_together(*images, labels=['Source', 'Reference', 'Matched']):
    fig, axes = plt.subplots(nrows=1, ncols=len(images), figsize=(12, 6),
                             sharex=True, sharey=True)
    for aa in axes:
        aa.set_axis_off()

    for (ax, image, label) in zip(axes, images, labels):
        ax.imshow(image)
        ax.set_title(label)

    plt.tight_layout()
    plt.show()


def savings(year, returns, annual_deposit=25000):
    "Calculate the savings at the end of the given year"
    if year == 0:
        return annual_deposit * returns[year]
    else:
        return (savings(year - 1, returns, annual_deposit)
                + annual_deposit) * returns[year]


def savings_hist(mean_return = 0.06, std_return = 0.1, num_trials = 10**5, years = 21, annual_deposit = 25_000):
    returns = np.random.normal(mean_return, std_return,
                           size=(years+1, num_trials)) + 1
    sav = pd.DataFrame({'Trial': range(num_trials), 'Savings': savings(years, returns, annual_deposit=annual_deposit)}).sample(10_000)
    chart = altair.Chart(sav).mark_bar().encode(
        altair.X('Savings:Q', bin=altair.Bin(maxbins=100)),
        altair.Y('count()'),
    ).properties(
        title=f'Savings after {years} years'
    ).interactive()
    return chart


def get_weather(city):
    params = {'q': city, 'appid': weather_api_key, 'units': 'metric'}
    response = requests.get(weather_url, params)
    if response.status_code != 200:
        return None
    weather = response.json()
    return weather


@tz.memoize
def get_temperature(city):
    weather = get_weather(city)
    try:
        return weather['main']['temp']
    except KeyError:
        return float('nan')


@tz.memoize
def get_icon_url(icon_code, size=2):
    return f'http://openweathermap.org/img/wn/{icon_code}@{size}x.png'

@tz.memoize
def get_icon(icon_code, size=2):
    return Image(get_icon_url(icon_code, size))

# This code pre-downloads all the icon codes for the live presentation:
icon_codes = ['01d', '02d', '03d', '04d', '09d', '10d', '11d', '13d', '50d',
              '01n', '02n', '03n', '04n', '09n', '10n', '11n', '13n', '50n', ]
for code in icon_codes:
    _ = get_icon(code, size=2)
    _ = get_icon(code, size=4)
