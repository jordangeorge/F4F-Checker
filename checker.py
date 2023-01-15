#!/usr/bin/python3

import bs4
from datetime import datetime
import json
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time

load_dotenv()

class InstagramChecker():
    def __init__(self):
        self.driver = webdriver.Chrome('./chromedriver')
        self.url = 'https://www.instagram.com'
        self.wait = WebDriverWait(self.driver, 15)
        self.target_profile_username = os.getenv('INSTAGRAM_USERNAME')

    def login(self):
        # go to instagram
        self.driver.get(self.url)

        # input username and password
        time.sleep(3)
        self.driver.find_element_by_name('username').send_keys(self.target_profile_username)
        self.driver.find_element_by_name('password').send_keys(os.getenv('INSTAGRAM_PASSWORD'))
        
        # click login button
        time.sleep(1)
        login_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[class='_ab8w  _ab94 _ab99 _ab9f _ab9m _ab9p _abcm']")))
        login_button.click() 

        # go to profile
        time.sleep(3)
        self.driver.get(self.url + "/" + self.target_profile_username)

        time.sleep(5)

        # print("on profile")

    def scroll_through_dialog(self, dialog_ul_div_xpath, num):
        time.sleep(7)
        dialog_ul_div = self.driver.find_element_by_xpath(dialog_ul_div_xpath)
        li_num = 0
        while li_num < num:
            self.driver.execute_script('return arguments[0].scrollIntoView(0, document.documentElement.scrollHeight-10);', dialog_ul_div)
            li_num = len(dialog_ul_div.find_elements_by_tag_name('button'))
            # print(li_num,'<',num)

    def getFollowing(self):
        print('Getting people ' + self.target_profile_username + ' is following')

        # get number of following
        time.sleep(4)
        num_of_following = int(self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span[class='_ac2a']")))[2].text)
        # print("num_of_following:",num_of_following)

        # click on following dialog
        time.sleep(4)
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'/following')]"))).click()
        # print("clicked followingdialog")
        
        # print("scrolling")
        self.scroll_through_dialog('/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/div[1]', num_of_following)
        # print("done scrolling")

        following_usernames = list()

        for i in range(0, num_of_following):
            username_and_verify_status = self.driver.find_element_by_xpath('/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/div/div/div['+str(i+1)+']/div[2]/div[1]/div/div/div/a/span/div').text.split('\n')

            username = username_and_verify_status[0]
            
            try:
                verify_status = username_and_verify_status[1]
            except:
                verify_status = '-'

            try:
                display_name = self.driver.find_element_by_xpath('/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/div/div/div['+str(i+1)+']/div[2]/div[2]/div').text
            except:
                display_name = "-"

            following_usernames.append({
                'username': username,
                'profile_link': self.url + "/" + username,
                'display_name': display_name,
                'verify_status': verify_status
            })
        
        # print()
        # print()

        return following_usernames

    def getFollowers(self):
        print('Getting people that are following ' + self.target_profile_username)

        # get number of followers
        num_of_followers = int(self.driver.find_elements_by_css_selector("span[class='_ac2a']")[1].text)
        # print("num_of_followers:",num_of_followers)

        # click on followers dialog
        time.sleep(1)
        self.driver.find_element_by_xpath('/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/div[1]/div[2]/section/main/div/header/section/ul/li[2]/a').click()

        # print("scrolling")
        self.scroll_through_dialog('/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div[1]', num_of_followers)
        # print("done scrolling")

        followers_usernames = list()

        for i in range(0, num_of_followers):
            username_and_verify_status = self.driver.find_element_by_xpath('/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div[1]/div/div['+str(i+1)+']/div[2]/div[1]/div/div/div/a/span/div').text.split("\n")

            username = username_and_verify_status[0]

            try:
                verify_status = username_and_verify_status[1]
            except:
                verify_status = '-'

            try:
                display_name = self.driver.find_element_by_xpath('/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div[1]/div/div['+str(i+1)+']/div[2]/div[2]/div').text
            except:
                display_name = "-"

            followers_usernames.append({
                'username': username,
                'profile_link': self.url + "/" + username,
                'display_name': display_name,
                'verify_status': verify_status
            })


        return followers_usernames

    def getComparisons(self):
        following_usernames = self.getFollowing()
        self.driver.find_element_by_xpath('/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[1]/div/div[3]/div/button').click() # close dialog window
        followers_usernames = self.getFollowers()

        l = list()

        for i in range(len(following_usernames)):
            for j in range(len(followers_usernames)):
                if following_usernames[i]['username'] == followers_usernames[j]['username']:
                    break
                elif following_usernames[i]['username'] != followers_usernames[j]['username'] and j == len(followers_usernames)-1:
                    l.append(following_usernames[i])

        return l

    def closeDriver(self):
        self.driver.close()

    def __exit__(self, exc_type, exc_value, traceback):
        self.closeDriver()

def put_results_in_file(l, fmt_amts_str):
    current_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    filename = "results_"+current_time+".txt"

    if os.path.isfile(filename):
        os.remove(filename)

    results_file = open(filename, "a")

    results_file.write(str(fmt_amts_str.format('Username', 'Profile Link', 'Display Name', 'Verify Status')))
    results_file.write(str('\n'))
    results_file.write(str('-' * sum(fmt_amts)))
    results_file.write(str('\n'))

    for item in l:
        results_file.write(str(fmt_amts_str.format(item['username'], item['profile_link'], item['display_name'], item['verify_status'])))
        results_file.write(str('\n'))

    results_file.close()

def print_results_to_console(l, fmt_amts_str):
    print(fmt_amts_str.format('Username', 'Profile Link', 'Display Name', 'Verify Status'))
    print('-' * sum(fmt_amts))
    for item in l:
        print(fmt_amts_str.format(item['username'], item['profile_link'], item['display_name'], item['verify_status']))
    print()

if __name__ == '__main__':
    ic = InstagramChecker()
    ic.login()

    l = ic.getComparisons()
    print()

    fmt_amts = [25, 55, 35, len('Verify Status')]
    fmt_amts_str = ''
    for i in fmt_amts: fmt_amts_str += '{:' + str(i) + '}'

    put_results_in_file(l, fmt_amts_str)
    # print_results_to_console(l, fmt_amts_str)

    ic.closeDriver()

    print("Done.")
