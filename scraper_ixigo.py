# -*- coding: utf-8 -*-
"""
Created on Sat Jan  4 12:06:04 2020

@author: debayan.bose
"""
import csv
import selenium.webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

from selenium import webdriver
#from multiprocessing import Process
#import multiprocessing
import warnings
import datetime
from dateutil.rrule import rrule, DAILY
import numpy as np
#import config
from pymongo import MongoClient 
from selenium.webdriver.firefox.options import Options



warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

def get_driver():
#    options = webdriver.ChromeOptions()    
#    options.add_argument("--headless")
#    options.add_argument("window-size=1920,1080")
#    options.add_argument("start-maximised")
#    options.add_argument("--use-fake-ui-for-media-stream")
#    options.add_argument("--disable-user-media-security=true")
#    options.add_argument('--no-proxy-server') 
#    capabilities = DesiredCapabilities.CHROME.copy()
#    capabilities['acceptSslCerts'] = True 
#    capabilities['acceptInsecureCerts'] = True
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options, executable_path=r'C:/D Backup/geckodriver.exe')

    return driver


def parser(soup):
    flight_detail = soup.find_all('div', attrs={'class': 'airline-info'})
    flight_num = []
    for j in range(len(flight_detail)):
        temp1 = flight_detail [j].find_all('div',attrs={'class': 'u-text-ellipsis'})[2].text
        flight_num.append(temp1)
    
    flight_name = []
    for j in range(len(flight_detail)):
        temp1 = flight_detail [j].find_all('div',attrs={'class': 'u-text-ellipsis'})[1].text
        flight_name.append(temp1)
    
    flight_summary = soup.find_all('div', attrs={'class': 'flight-summary'})
    flight_depDate = []
    for j in range(len(flight_summary)):
        temp2 = flight_summary [j].find_all('div',attrs={'class': 'date'})[0].text
        flight_depDate.append(temp2)
    flight_arrDate = []
    for j in range(len(flight_summary)):
        temp3 = flight_summary [j].find_all('div',attrs={'class': 'date'})[1].text
        flight_arrDate.append(temp3)
    flight_Origin = []
    for j in range(len(flight_summary)):
        temp4 = flight_summary [j].find_all('div',attrs={'class': 'city u-text-ellipsis'})[0].text
        flight_Origin.append(temp4)
    
    flight_Destin = []
    for j in range(len(flight_summary)):
        temp5 = flight_summary [j].find_all('div',attrs={'class': 'city u-text-ellipsis'})[1].text
        flight_Destin.append(temp5)
    flight_DepTime = []
    for j in range(len(flight_summary)):
        temp6 = flight_summary [j].find_all('div',attrs={'class': 'time'})[0].text
        flight_DepTime.append(temp6)
    flight_ArrTime = []
    for j in range(len(flight_summary)):
        temp7 = flight_summary [j].find_all('div',attrs={'class': 'time'})[1].text
        flight_ArrTime.append(temp7)
    
    flight_duration = []
    for j in range(len(flight_summary)):
        temp9 = flight_summary [j].find_all('div',attrs={'class': 'label tl'})[0].text
        flight_duration.append(temp9)
    
    flight_stop = []
    for j in range(len(flight_summary)):
        temp10 = flight_summary [j].find_all('div',attrs={'class': 'label br'})[0].text
        flight_stop.append(temp10)
    
    fare_details = soup.find_all('div', attrs={'class': 'price-section'})
    flight_fare=[]
    for j in range(len(fare_details)):
        temp11 = fare_details [j].text
        flight_fare.append(temp11)
    
    flightsData = []
    for j in range(len(fare_details)):
        flightsData.append([flight_name[j], flight_num[j], flight_Origin[j], flight_Destin[j], flight_DepTime[j], flight_ArrTime[j], flight_duration[j], flight_stop[j], flight_fare[j]])
    flightsData = pd.DataFrame(flightsData)
    return flightsData

    
def scrape_ixigo(url,depdate):
    
    driver=get_driver()
    driver.get(url)  			 # URL requested in browser.
    #myElem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body')))  	
    time.sleep(20)
    for j in range(1,50):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    body = driver.page_source
    soup_page1 = BeautifulSoup(body, "lxml")
    flightsData_1 = parser(soup_page1)
    if len(flightsData_1)==0:
        print('no records found for '+ url)
        driver.close()
        driver.quit()
        return None
    else:
        test = []
        for page_link in driver.find_elements_by_xpath('//span[@class="page-num"]'):
            #print("page number: %s" % page_link.text)
            page_link.click()
            body = driver.page_source
            soup = BeautifulSoup(body, "lxml")
            #flight_num = soup.find_all('a', attrs={'class': 'flight-name'})
            flightsData = parser(soup)
            test.append(flightsData)
        if len(test)>0:
            test = pd.concat(test)
            test = test.append(flightsData_1)
        else:
            test = flightsData_1
        
        test['DepartureDate'] = depdate
        driver.close()
        driver.quit()
    return test

def scrapenew_ixigo(origin,destin,fromdate,todate,job_time, passengers, stops):
    a = datetime.datetime.strptime(fromdate, "%d/%m/%Y").date()
    b = datetime.datetime.strptime(todate, "%d/%m/%Y").date()
    trDate = list()
    for dt in rrule(DAILY, dtstart=a, until=b):
        dept_date = str(dt.strftime("%m/%d/%Y"))
        trDate.append(dept_date)
    all_urls = list()  
    for j in range(len(trDate)):
        url = 'https://www.ixigo.com/search/result/flight/'
        url = url + origin +'/'+destin +'/'
        dt_format = datetime.datetime.strptime(trDate[j], "%m/%d/%Y").date().strftime('%d%m%Y')
        url = url + dt_format + '//'
        
        #passengers = 'A-1_C-0_I-0'
        adults = passengers[2]
        children = passengers[6]
        infants = passengers[10]
        pax = adults+'/'+children+'/'+infants+'/'
        url = url + pax + 'e?source=Search%20Form'
        #url = url + '&validation_result=&domesinter=international&livequote=-1&flightClass=ALL&travType=DOM&routingType=ALL&preferredCarrier=ALL&prefCarrier=0&isAjax=false'
        all_urls.append(url)
    data=list()
    for urls in range(len(all_urls)):
        temp1 = scrape_ixigo(all_urls[urls],trDate[urls])
        if not (temp1 is None):
            data.append(temp1)
    if len(data) == 0:
        return 0
    df = pd.concat(data)
    df.columns = ['FlightName', 'FlightCode', 'DepCity','ArrivalCity','DepTime','ArrivalTime','FlightDuration','stops','fare','DepartureDate']
    cols = ['DepartureDate','FlightName', 'FlightCode', 'DepTime','DepCity','FlightDuration','ArrivalTime','ArrivalCity','fare','stops']
    df = df[cols]
#    df['fare'] = [w.replace('₹ ', '') for w in df['fare']]
#    df['fare'] = [w.replace(',', '') for w in df['fare']]
    df['fare']= np.array(df['fare'],float)
    df['sector']= origin +'_'+destin
    df['job_time'] = job_time
    df['NSTOP'] = df['stops']
    for j in range(len(df)):
        if df['stops'].iloc[j] == 'non-stop':
            df['NSTOP'].iloc[j] = '0'
    df['NSTOP'] = [w.replace('stop','') for w in df['NSTOP']]
    df['NSTOP'] = [w.replace('s','') for w in df['NSTOP']]
    
    df['NSTOP'] = [w.replace(' ','') for w in df['NSTOP']]
    df['NSTOP'] = np.array(df['NSTOP'],int)
#    df_del = df[df['NSTOP']==0] 
#    df_del = df_del[df_del['FlightName'].str.contains('MultipleAirlines')]
#    df = df.drop(df_del.index, axis=0) 
    df['stops'] = df['NSTOP']
    del df['NSTOP']
    if (stops >= 0):
        df = df.query("stops == "+str(stops))

    if len(df.index) == 0:
        return 0
    df['source'] = 'IXIGO'

#    conn = MongoClient(config.DB_SERVER)
#    db = conn.database 
#    new_database = db.scrapedb  
#    data = df.to_dict(orient='records') 
#    result = new_database.insert_many(data)
#    
    return df


if __name__ == '__main__':
    mydata = scrapenew_ixigo('BOM','GAU','14/1/2020','14/1/2020','12/12/2019 16:48',
                       passengers='A-1_C-0_I-0', stops = 0 )	
        