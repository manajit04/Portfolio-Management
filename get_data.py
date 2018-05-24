#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  9 01:15:09 2018

@author: zhangtiangu
"""

from bs4 import BeautifulSoup
from selenium import webdriver 
import os

from time import sleep
def download_data(ticker,freq="1d"):    
    if isinstance(ticker,str):
        ticker = [ticker]
        
    option = webdriver.ChromeOptions()
    prefs = {"download.default_directory" : os.getcwd()}
    option.add_experimental_option("prefs",prefs)
    browser = webdriver.Chrome(chrome_options=option)
    
    for i in ticker:
        url = "https://finance.yahoo.com/quote/{}/history?period1=1167627600&period2=1476936000&interval=1d&filter=history&frequency={}".format(i,freq)
        browser.get(url)
        soup=BeautifulSoup(browser.page_source,"html.parser")
        a = soup.find_all("a",{"class":"Fl(end) Mt(3px) Cur(p)"})
        try:
            assert len(a)==1
            browser.get(a[0].get("href"))
        except AssertionError as e:
            print("can't find tag 'a'")
        sleep(1)
        
    browser.close() 

if __name__ == "__main__":
    ticker = ["FXE","EWJ","GLD","QQQQ","SPY","SHV","DBA","USO","XBI","ILF","GAF","EPP","FEZ"]
    download_data(ticker)
    path = os.getcwd()+"/data"
    
    # initilize dataframe by benchmark
    data = pd.read_csv(path+"/SPY.csv")
    data = data.loc[:,["Adj Close","Date"]]
    data.columns=["SPY","Date"]
    
    #get all adj_close and inner join
    ticker = ["FXE","EWJ","GLD","QQQ","SHV","DBA","USO","XBI","ILF","GAF","EPP","FEZ"]
    
    for i in ticker:
        adj_close = pd.read_csv(path+"/{}.csv".format(i))
        adj_close = adj_close.loc[:,["Adj Close","Date"]]
        adj_close.columns=[i,"Date"]
        data = pd.merge(data,adj_close,how="inner",on="Date")

    data.Date = pd.to_datetime(data.Date)
    #import factors's data
    factors = pd.read_csv(path+"/F-F_Research_Data_Factors_daily.CSV",
                          skiprows=5,
                          header=None,
                          names=["Date","Mkt-RF","SMB","HML","RF"])
    factors = factors.iloc[:-1,:]
    factors.Date = pd.to_datetime(factors["Date"],format="%Y%m%d")
    data = pd.merge(data,factors,how="inner",on="Date")

    data.set_index("Date",inplace=True)
    data = data.drop(data.index[data["GAF"]=="null"])
    data = data.applymap(float)
    data.to_csv(os.getcwd()+"/data/adj_close.csv")
