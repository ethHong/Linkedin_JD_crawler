#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import urllib
from urllib import request
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains  
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
from fake_useragent import UserAgent
from tqdm.notebook import trange
import time


options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-automation']) 


def mock_user_agent():
    ua = UserAgent()
    
    working = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15"
    working_tail = "(" + working.split("(")[-1]
    random_head = ua.random.split("(")[0]+"("+ua.random.split("(")[1]
    return random_head + working_tail



ID = input("ID (Email)")
PASS = input("PASSWORD")


userAgent = mock_user_agent()
options.add_argument(f'user-agent={userAgent}')


driverpath = os.getcwd()+"/chromedriver"
driver =  webdriver.Chrome(driverpath,  chrome_options=options)

wait = WebDriverWait(driver, 10)

def Login_linkedin(driver, ID, PASS):

    url = "https://www.linkedin.com/"
   
    driver.get(url)
    #driver.find_element_by_xpath('/html/body/div/main/p/a').click()
    
    ID = ID
    PASS = PASS
    
    elem = driver.find_element_by_xpath('//*[@id="session_key"]')
    elem.send_keys(ID)
    elem = driver.find_element_by_xpath('//*[@id="session_password"]')
    elem.send_keys(PASS)
    
   
    driver.find_element_by_xpath('/html/body/main/section[1]/div[2]/form/button').click()
    


def refresh_link(continue_link):
    userAgent = mock_user_agent()
    options.add_argument(f'user-agent={userAgent}')
    driverpath = os.getcwd()+"/chromedriver"
    driver =  webdriver.Chrome(driverpath,  chrome_options=options)
    
    Login_linkedin(driver, ID, PASS)
    
    driver.get(continue_link)


Login_linkedin(driver, ID, PASS)

job = input("Put your job position: ")
region = "대한민국"

header = "https://www.linkedin.com/jobs/search/?geoId=105149562&keywords="

def refine(c):
    c_ref = "-".join(c.split(" ")).lower()
    return c_ref

link = header + refine(job)
driver.get(link)


print("wait 5 sec...")
time.sleep(5)


html = driver.page_source
soup = BeautifulSoup(html, "html.parser") 
driver.implicitly_wait(10)


pages = soup.find("ul", {"class": "artdeco-pagination__pages artdeco-pagination__pages--number"}).find_all("li")


total_page = int(pages[-1].text.strip()) # # of total page


def refresh_source_pages():
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser") 
    time.sleep(5)
    driver.implicitly_wait(10)
    try:
        p = soup.find("ul", {"class": "artdeco-pagination__pages artdeco-pagination__pages--number"}).find_all("li")
    except:
        driver.get(driver.current_url)
        time.sleep(5)
        p = soup.find("ul", {"class": "artdeco-pagination__pages artdeco-pagination__pages--number"}).find_all("li")
    return [p, soup]

def crawl_jd():
    soup = refresh_source_pages()[1]

    potision = []
    job_details = []

    jobs = soup.find_all("li", {"class": "jobs-search-results__list-item occludable-update p0 relative ember-view"})
    jobs_id = [i["id"] for i in jobs]
    
    for i in jobs_id:
        driver.find_element_by_xpath('//*[@id="{}"]'.format(i)).click()

        driver.implicitly_wait(10)
        #refresh page source
        soup = refresh_source_pages()[1]
        
        driver.implicitly_wait(10)
        
        Position =soup.find("h2", {"class": "jobs-details-top-card__job-title t-20 t-black t-normal"}).text.rstrip()

        Job_Details = soup.find("div", {"id":"job-details"}).text.strip()
        potision.append(Position)
        job_details.append(Job_Details)

    
    return pd.DataFrame({"Position" : potision, "Job_Details": job_details})


how_many = 3 #안전하게 3번마다 Refresh


pages = refresh_source_pages()[0]
soup = refresh_source_pages()[1]


#Start Page 넣으면 알아서 크롤링하게 만들기
def crawl_job_description(starting_page, how_many, start_url):
    if how_many>total_page:
        how_many= total_page
        
    driver.get(start_url)
    driver.implicitly_wait(10)
    
    pages = refresh_source_pages()[0]
    soup = refresh_source_pages()[1]
    
    current = starting_page
    df = pd.DataFrame()

    for i in trange(starting_page-1, how_many+starting_page-1):
    
        print ("Crawling {} out of {} pages...".format(current, total_page))

        pages_meta = [j.text.strip().split()[0] for j in pages]    

        #Do Crawling#
        crawed_page = crawl_jd()
        df = pd.concat([df, crawed_page])
        current = current+1
        #Move page 
        try:
            index_of_next_page = pages_meta.index(str(i+2))
        except ValueError:
            index_of_next_page = len(pages_meta) -1 - pages_meta[::-1].index('…')

        button_aria_label = pages[index_of_next_page].find("button")["aria-label"]

        #해당 버튼이 나올때까지 기다려주기

        driver.implicitly_wait(10)

        try:
            driver.find_element_by_xpath('//*[@aria-label="{}"]'.format(button_aria_label)).click()

        except:
            driver.get(driver.current_url)
            driver.implicitly_wait(10)
            button_aria_label = str(int(button_aria_label.split()[0])+1) + " " + button_aria_label.split()[1]
            driver.find_element_by_xpath('//*[@aria-label="{}"]'.format(button_aria_label)).click()

        
        driver.implicitly_wait(10)
        print ("Upcoming page is {}".format(starting_page+i+1))
        upcoming = driver.current_url
        #Refresh List
        try:
            pages = refresh_source_pages()[0]
        except:
            driver.get(driver.current_url)
            driver.implicitly_wait(10)
        
    return (df, upcoming)


def check_http_error():
    return "HTTP ERROR 429" in driver.page_source

df = pd.DataFrame()
start_url = driver.current_url

go = "y"

while go=="y":
    for i in trange(total_page//how_many):
        starting_page_num = 1+(3*i)

        try:
            out = crawl_job_description(starting_page_num, 3, start_url)
        except:
            if check_http_error() == True:
                backup_df = df
                
                if starting_page_num !=1:
                    
                    start_url = out[1]
                print ("Take a break...for 1.5 minuits...")
                time.sleep(90)
                #go = input("Keep going? (y/n)")
                refresh_link(start_url)
                out = crawl_job_description(starting_page_num, 3, start_url)
            else: #For simple errors
                refresh_link(start_url)
                driver.implicitly_wait(10)
                out = crawl_job_description(starting_page_num, 3, start_url)
        
        start_url = out[1]
        df =  pd.concat([df, out[0]])
        print ("Refreshing for {} times".format(i+1))
        refresh_link(start_url)

       
     

df.to_csv("JD_{}.csv".format(job), index = False, encoding = 'utf-8')
df.to_excel("JD_{}.xlsx".format(job), index = False, encoding = 'utf-8')

df.head()



