import numpy as np
import pandas as pd
import requests
from quickchart import QuickChart
from typing import Any, Dict, List


# class providing link to the chart describing data on temperature and pressure in the country


class LinkToChart:
    # formally, year is not a month, but with use these words ans indexes
    MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
              'August', 'September', 'October', 'November', 'December', 'Year']
    ALT_MESSAGE = "Unfortunately, there is no info on the weather"
    CHART_WIDTH = 1000
    CHART_HEIGHT = 600
    HIGH_AVG_T = 20
    LOW_AVG_T = 10
    HIGH_PRESSURE_DIFF = 100

    def __init__(self, data: Dict[str, Any]):
        self.chart_client = QuickChart()
        self.data_dict = data

    def __call__(self) -> Dict[str, str]:
        if 'weather' not in self.data_dict:
            return {
                "temp_chart_url": "",
                "press_char_url": "",
                "text": self.ALT_MESSAGE
            }
        data = pd.DataFrame.from_dict(self.data_dict['weather'], orient='index').astype(float)
        year_row = np.array([data.max().iloc[0], data.min().iloc[1], data.mean().iloc[2],
                             data.min().iloc[3], data.max().iloc[4], data.mean().iloc[5]])
        year_df = pd.DataFrame(year_row.reshape([1, 6]), columns=['tMin', 'tMax', 'tAvg', 'pMin', 'pMax', 'pAvg'],
                               index=['Year'])
        data = pd.concat([data, year_df])
        self.chart_client.width = self.CHART_WIDTH
        self.chart_client.height = self.CHART_HEIGHT
        self.chart_client.config = {
            "type": "bar",
            "data": {
                "labels": self.MONTHS,
                "datasets": [{
                    "label": "tMin",
                    "data": data['tMax'].to_list()
                }, {
                    "label": "tAvg",
                    "data": data['tAvg'].to_list()
                }, {
                        "label": "tMax",
                        "data": data['tMin'].to_list()
                }]
            }
        }
        temp_chart_url = self.chart_client.get_url()
        self.chart_client.config = {
            "type": "bar",
            "data": {
                "labels": self.MONTHS,
                "datasets": [{
                    "label": "pMin",
                    "data": data['pMin'].to_list()
                }, {
                    "label": "pAvg",
                    "data": data['pAvg'].to_list()
                }, {
                    "label": "pMax",
                    "data": data['pMax'].to_list()
                }]
            }
        }
        press_chart_url = self.chart_client.get_url()
        text = ""
        if data['tAvg'].iloc[12] > self.HIGH_AVG_T:
            text += "The climate is worm in the country."
        elif data['tAvg'].iloc[12] < self.LOW_AVG_T:
            text += "It is rather cold in this country."
        else:
            text += "Great climate! It's worm enough but not too hot."
        if data['pMax'].iloc[12] - data['pMin'].iloc[12] > self.HIGH_PRESSURE_DIFF:
            text += "Warning! High pressure drops."
        return {
            "temp_chart_url": temp_chart_url,
            "press_char_url": press_chart_url,
            "text": text
        }


# class collecting data for the specified country


class CountryInfo:
    ALT_MESSAGE = "Unfortunately, there is no info on the country. Probably, you have made a typo"
    POST_URL = "https://travelbriefing.org/{country}?format=json"

    def get_data(self, country: str) -> Dict[str, Any]:
        response = requests.get(self.POST_URL.format(country=country))
        if response.status_code != 200:
            return {
                "data": {},
                "text": self.ALT_MESSAGE
            }
        else:
            return {
                "data": response.json(),
                "text": ""
            }

    def __call__(self, country: str) -> Dict[str, Any]:
        result = self.get_data(country)
        if result['text'] != "":
            return {
                "full_name": "",
                "official_languages": [],
                "weather_chart_link": "",
                "text": result["text"]
            }
        else:
            return {
                "full_name": self.get_full_name(result['data']),
                "official_languages": self.get_languages(result['data']),
                "weather_chart_link": self.get_weather_chart(result['data']),
                "text": ""
            }

    @staticmethod
    def get_full_name(data: Dict[str, Any]) -> str:
        return data['names']['full']

    @staticmethod
    def get_languages(data: Dict[str, Any]) -> List[str]:
        result = []
        for lang_dict in data['language']:
            if lang_dict['official'] == 'Yes':
                result.append(lang_dict['language'])
        # if there is no official language, we print the corresponding message
        result.append("unknown")
        return result

    @staticmethod
    def get_weather_chart(data: Dict[str, Any]) -> Dict[str, Any]:
        link_to_chart = LinkToChart(data)
        return link_to_chart()
