from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from functools import reduce
import pandas as pd
import time

def render_page(url):
    # Change path on line 11 with location of your google chrome driver 
    # (download correct version for your version of google chrome here: https://chromedriver.chromium.org/downloads)
    driver_file_loc = "C:\\Users\Erin Dowdy\Downloads\chromedriver_win32\chromedriver"
    driver = webdriver.Chrome(driver_file_loc)
    driver.get(url)
    time.sleep(3)
    r = driver.page_source
    driver.quit()
    return r


def get_lat_long(soup) :
    a = soup.find('div', class_ = 'dashboard__header small-12 ng-star-inserted')
    if a is not None:
        b = a.find('div', class_ = 'columns small-12 station-header')
        if b is not None:
            c = b.find('div', class_ = 'sub-heading')
            if c is not None:
                d = c.find('span')
                txt = d.text
                vals = txt.split(',')
                result = []
                south = False
                west = False
                for v in vals:
                    x = v.strip()
                    for char in x:
                        if (char.isnumeric() == False and char != '.'):
                            if char == 'S':
                                south = True
                            if char == 'W':
                                west = False
                            x = x.replace(char,'')
                    result.append(x)
                if west:
                    result[2] = '-' + result[2]
                if south:
                    result[1] = '-' + result[1]
                return result
    return ['---', '---','---']


def scraper(dates, station_path, outpath):
    stations = []
    with open(station_path) as f:
        stations = f.readlines()

    dict = {'station':[],'elev (ft)':[],'lat':[],'lon':[], 'high_temp':[], 'low_temp':[], 'avg_temp':[],'high_dewpt':[],'avg_dewpt':[],'low_dewpt':[],'high_hum':[],'avg_hum':[],'low_hum':[],'precip':[]}
    output = pd.DataFrame(dict)
    for date in dates:
        for station in stations:
            url  = "https://www.wunderground.com/dashboard/pws/station/table/date/date/daily"
            url = url.replace("station", station)
            url = url.replace("date", date)

            r = render_page(url)
            soup = BS(r, "html.parser")
            loc = get_lat_long(soup)


            a = soup.find('lib-history-summary')
            if a is not None:
                check = a.find('tbody')

                data = [station, loc[0], loc[1], loc[2]]
                for c in check.find_all('tr'):
                    for i in c.find_all('td'):
                        d = i.find('lib-display-unit')
                        if d is not None:
                            s = d.find('span')
                            if s is not None :
                                t = s.find('span')
                                print(station, t.text)
                                data.append(t.text)
                output.loc[len(output.index)] = data
    output.to_csv(outpath)


stations = r'C:\\Users\\Erin Dowdy\\Documents\\hackathon\\stations.txt' # replace with location of your station file
dates = ['2022-6-14'] # add/change dates based on your study range
outpath = r'C:\\Users\\Erin Dowdy\\Documents\\hackathon\\results.csv' # change with your outpath
df_output = scraper(dates, stations, outpath)
