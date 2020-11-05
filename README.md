# Linkedin_JD_crawler
Selenium based Linkedin Job Description crawler

# Description
This projet is closely related to following project: https://github.com/ethHong/Selenium_Linkedin_Crawler

## Introduction

Linkedin is open platform in career market. It enables many people to get access to career and reqruitment related information of various companies. Many jobseekers and recruiters use them.

We can search Job Descriptions for open jobs, but it is difficult to manually scrape them. Therefore I'd been working on a useful tool to automate process of:

- Sign in, and put a job role you want to search (ex. Operation, Marketing, etc...)
- Scrape currently uplpoaded job description of your region. 

Of course it collects the information of people who agreed to display their data on Linkedin platform, and since there could be privacy issues the coide definitely collect data anonymously. As I know, there exists some 3rd party APIs, and ugins Request is more efficient way for crawling programs in general, but for two reasons I use selenium:

Since Linkedin is reactive webpage, and requires log-in, it is more easier and intuitive to use Seleinium, and
Using urllib request to scrape from services like Linkedin could be problematic, if they prohibit such activity. However, manually searching for information through the platform is allowed, so I used Selenium which merely automates process we manually do.

## How to Use

- If you don't have chromedriver, you need to install the right version of Chromedriver, which matches your browser.
- When running this file, the default region is set as South KR, so you may have to change from the code
- I HIGHLY RECOMMEND using ipynb rather than py, because for somewhat reason py seems to have more superior processing speed, causing http 429 error (sending too frequent request to website), which could give negative impact to the website
- This program uses fake-UA to avoid bot-detection, so highly recommend only using this for personal / academic purpose


## Current Issues
This program has an issue of failing to scrape more than 6 JDs per page, and move to next page. Work on progress to solve this issue. 
