# -*- coding: utf-8 -*-
"""
Created on Thu Jan  6 12:46:06 2022

A script to scrape the log files from virtualsilcton.com

@author: smwei
"""
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import getpass
import os

# Where to save the data? 
output_dir = 'c:/users/smwei/Desktop/Splash/sketchLogs'


# Get login email and study ID from user
# Study ID should be the URL # visible after you login to virtualsilcton.com and navigate to your study.
email = 'smweis@gmail.com'
study_id = '753798709' 


# You'll be prompted for your password
password = getpass.getpass()

# Check whether the specified path exists or not
isExist = os.path.exists(output_dir)
if not isExist:
  # Create a new directory because it does not exist 
  os.makedirs(output_dir)
  print(f"Output directory is: {output_dir}")

url = 'http://www.virtualsilcton.com/experimenters/sign_in'

# Use 'with' to ensure the session context is closed after use.
with requests.Session() as s:
    site = s.get(url)
    bs_content = bs(site.content, "html.parser")
    token = bs_content.find("meta", {"name":"csrf-token"})['content']
    login_data = {"experimenter[email]":email,"experimenter[password]":password, "authenticity_token":token}
    s.post(url,login_data)
    
    
    navlog_page = s.get("http://www.virtualsilcton.com/experimenter/studies/" + study_id + "/data?table=navigation-log")
    navlog_soup = bs(navlog_page.text,features='lxml')
    
    navlog_table = navlog_soup.find('table')
    
    # Initialize a dataFrame
    data = pd.DataFrame(columns=['participant','datetime','route','number_log_lines','text','link'])
    
    # Loop through each row of the table and get all the data we need to extract logs
    rows = navlog_table.find_all('tr')
    for row in rows[1:]:
        cols = row.findAll('td')
        text_cols = [ele.text.strip() for ele in cols]
        # Some special code to grab the link
        for link in row.findAll('a'):
            link_text = 'http://www.virtualsilcton.com' + link.get('href') + '.txt'
            text_cols.append(link_text)

        data = data.append(pd.Series(text_cols,index=data.columns),ignore_index=True)
     
        # Now extract logs! 
        file = s.get(link_text)
        
        # filename is participant id, route name
        filename = 'participant-' + text_cols[0] + '_route-' + text_cols[2] + '.txt'

        open(os.path.join(output_dir, filename),'wb').write(file.content)
    
    