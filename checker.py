#!/usr/bin/python3

import bs4
import json
import os
from dotenv import load_dotenv
from selenium import webdriver
import time

load_dotenv()

class InstagramChecker():
    def __init__(self):
        self.driver = webdriver.Chrome('./chromedriver')
        self.url = 'https://www.instagram.com'

    def login(self, target_profile_username):
        # go to instagram
        self.driver.get(self.url)

        # login to instagram
        time.sleep(3)
        self.driver.find_element_by_name('username').send_keys(target_profile_username)
        self.driver.find_element_by_name('password').send_keys(os.getenv('INSTAGRAM_PASSWORD'))
        time.sleep(1)
        self.driver.find_elements_by_xpath("/html/body/div[1]/section/main/article/div[2]/div[1]/div[2]/form/div/div[3]/button/div[contains(text(), 'Iniciar sesión')]")[0].click()

        # go to profile
        time.sleep(3)
        self.driver.get(self.url + "/" + target_profile_username)

        time.sleep(2)

    def scroll_through_dialog(self, dialog_ul_div_xpath, num):
        time.sleep(7)
        dialog_ul_div = self.driver.find_element_by_xpath(dialog_ul_div_xpath)
        li_num = 0
        while li_num < num:
            self.driver.execute_script('return arguments[0].scrollIntoView(0, document.documentElement.scrollHeight-10);', dialog_ul_div)
            li_num = len(dialog_ul_div.find_elements_by_tag_name('button'))
            # print(li_num,'<',num)

    def getFollowing(self):
        print('Getting people you\'re following')

        # get number of following
        time.sleep(4)
        num_of_following = int(self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/div[1]/div/div/div/div[1]/div[1]/section/main/div/header/section/ul/li[3]/a/div/span').text)

        # click on following dialog
        time.sleep(4)
        self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/div[1]/div/div/div/div[1]/div[1]/section/main/div/header/section/ul/li[3]/a').click()

        self.scroll_through_dialog('/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/div[1]/div', num_of_following)

        following_usernames = list()

        for i in range(0, num_of_following):
            username_and_verify_status = self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/div/div/div['+str(i+1)+']/div[2]/div[1]/div/div/span/a/span/div').text.split("\n")

            username = username_and_verify_status[0]
            
            try:
                verify_status = username_and_verify_status[1]
            except:
                verify_status = '-'

            try:
                display_name = self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/div/div/div['+str(i+1)+']/div[2]/div[2]/div').text
            except:
                display_name = "-"

            profile_link = self.url + "/" + username

            following_usernames.append({
                'username': username,
                'profile_link': profile_link,
                'display_name': display_name,
                'verify_status': verify_status
            })

        return following_usernames

    def getFollowers(self):
        print('Getting people following you')

        # get number of followers
        num_of_followers = int(self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/div[1]/div/div/div/div[1]/div[1]/section/main/div/header/section/ul/li[2]/a/div/span').text)
        # print("num_of_followers=",num_of_followers)

        # click on followers dialog
        time.sleep(1)
        self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/div[1]/div/div/div/div[1]/div[1]/section/main/div/header/section/ul/li[2]/a').click()

        self.scroll_through_dialog('/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div[1]/div', num_of_followers)

        followers_usernames = list()

        for i in range(0, num_of_followers):
            username_and_verify_status = self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div/div/div['+str(i+1)+']/div[2]/div[1]/div/div/span/a/span/div').text.split("\n")

            username = username_and_verify_status[0]

            try:
                verify_status = username_and_verify_status[1]
            except:
                verify_status = '-'

            try:
                display_name = self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div/div/div['+str(i+1)+']/div[2]/div[2]/div').text
            except:
                display_name = "-"

            profile_link = self.url + "/" + username

            followers_usernames.append({
                'username': username,
                'profile_link': profile_link,
                'display_name': display_name,
                'verify_status': verify_status
            })


        return followers_usernames

    def getComparisons(self):
        following_usernames = self.getFollowing()
        self.driver.find_element_by_xpath('/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[1]/div/div[3]/div/button').click() # close dialog window
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
    filename = "results.txt"

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
    ic.login(os.getenv('INSTAGRAM_USERNAME'))

    l = ic.getComparisons()
    print()

    fmt_amts = [25, 55, 35, len('Verify Status')]
    fmt_amts_str = ''
    for i in fmt_amts: fmt_amts_str += '{:' + str(i) + '}'

    put_results_in_file(l, fmt_amts_str)
    # print_results_to_console(l, fmt_amts_str)

    ic.closeDriver()

    print("Done.")
