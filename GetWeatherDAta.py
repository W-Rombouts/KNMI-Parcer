import knmi
import json
import pandas as pd
import requests
from knmi.parsers import parse_day_data, parse_dataframe, parse_forecast_data

file = open("datetime.json", "r")
test = file.read()
file.close()

requiredTimes = json.loads(test)


def getHourlyTempAndDownfallForStation(stations: list, start="2019063000", end="2019123123", inseason=False):
    variables = ["ALL"]
    url = "http://projects.knmi.nl/klimatologie/uurgegevens/getdata_uur.cgi"
    params = {
        "stns": ":".join(str(station) for station in stations),
    }

    if start is not None:
        if not isinstance(start, str):
            start = start.strftime("%Y%m%d%HH")
        params.update({"start": start})
    if end is not None:
        if not isinstance(end, str):
            end = end.strftime("%Y%m%d%HH")
        params.update({"end": end})
        if inseason is True:
            params.update({"inseason": "Y"})
    params.update({"vars": ":".join(variables)})
    r = requests.post(url=url, data=params)
    r.raise_for_status()

    disclaimer, stations, legend, data = parse_day_data(raw=r.text)

    df = parse_dataframe(data, setIndex=False)
    df['YYYYMMDD'] = pd.to_datetime(df.YYYYMMDD,format="%Y%m%d")
    df['YYYYMMDD'] += pd.to_timedelta(df.HH, unit='h')
    df.index = pd.DatetimeIndex(df.YYYYMMDD)
    df = df.drop(columns=['YYYYMMDD', 'HH'])
    #df['T'] = df['T'].apply(lambda x: x * 0.1)
    #df['T'] = df['T'].map('{:,.1f}'.format)
    #df['DR'] = df['DR'].apply(lambda x: x * 6)

    return disclaimer, stations, legend, df

#Station 375 is Volkel Voor Gennep
disclaimer, stations, legend, df = getHourlyTempAndDownfallForStation(stations=[375])
# print(df.disclaimer)
# print(df.stations)
print(legend)
print(df)

file = open("legend.txt", "w")
file.write(str(legend))
file.close()
file = open("Disclaimer.txt", "w")
file.write(str(disclaimer))
file.close()


df.to_csv(r'Export_DataFrame.csv')
df.to_json("WeatherData.json")

