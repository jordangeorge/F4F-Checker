#!/usr/bin/env python3

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
        self.url = 'https://www.instagram.com/'

    def login(self, target_profile_username):
        # go to instagram
        self.driver.get(self.url)

        # login to instagram
        time.sleep(3)
        self.driver.find_element_by_name('username').send_keys(os.getenv('INSTAGRAM_USERNAME'))
        self.driver.find_element_by_name('password').send_keys(os.getenv('INSTAGRAM_PASSWORD'))
        self.driver.find_elements_by_xpath("/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div/div[3]/button/div[contains(text(), 'Iniciar sesión')]")[0].click()

        # go to profile
        time.sleep(3)
        self.driver.get(self.url + target_profile_username)

        time.sleep(2)

    def scroll_through_dialog(self, dialog_ul_div_xpath, num):
        time.sleep(7)
        dialog_ul_div = self.driver.find_element_by_xpath(dialog_ul_div_xpath)
        li_num = 0
        while li_num < num:
        # while li_num < 84: # FIXME: won't scroll beyond here for people i'm following list
            self.driver.execute_script('return arguments[0].scrollIntoView(0, document.documentElement.scrollHeight-10);', dialog_ul_div)
            li_num = len(dialog_ul_div.find_elements_by_tag_name('li'))
            print(li_num,'<',num)

    def getUlDiv(self):
        time.sleep(2)
        page = self.driver.page_source
        soup = bs4.BeautifulSoup(page, 'lxml')
        ul_div = soup.find_all('ul')
        if len(ul_div) == 3:
            ul_div = ul_div[2]
        elif len(ul_div) == 4:
            ul_div = ul_div[3]

        return ul_div

    def getFollowing(self):
        print('Getting people following you')

        # get number of following
        num_of_following = int(self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a/div/span').text)

        # click on following dialog
        time.sleep(3)
        self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a').click()

        self.scroll_through_dialog('/html/body/div[6]/div/div/div/div[3]/ul', num_of_following)

        following_usernames = list()
        ul_div = self.getUlDiv()
        lis = ul_div.find_all('li')
        for li in lis:
            username = li.find('div').find_all('div')[0].find_all('div')[2].find_all('div')[0].find('a').find('span').contents[0]

            profile_link = self.url + username

            try:
                display_name = li.find('div').find_all('div')[0].find_all('div')[2].find_all('div')[1].contents[0]
            except:
                display_name = '-'

            try:
                verify_status = li.find('div').find_all('div')[0].find_all('div')[2].find_all('div')[1].find('span').contents[0]
                display_name = li.find('div').find_all('div')[0].find_all('div')[2].find_all('div')[2].contents[0]
            except:
                verify_status = '-'

            following_usernames.append({
                'username': username,
                'profile_link': profile_link,
                'display_name': display_name,
                'verify_status': verify_status
            })

        return following_usernames

    def getFollowers(self):
        print('Getting your followers')

        # get number of followers
        num_of_followers = int(self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a/div/span').text)

        # click on followers dialog
        time.sleep(1)
        self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a').click()

        self.scroll_through_dialog('/html/body/div[6]/div/div/div/div[2]/ul', num_of_followers)

        followers_usernames = list()
        ul_div = self.getUlDiv()
        lis = ul_div.find_all('li')
        for li in lis:
            username = li.find('div').find_all('div')[0].find_all('div')[2].find_all('div')[0].find('a').find('span').contents[0]
            followers_usernames.append({'username': username})

        return followers_usernames

    def getComparisons(self):
        following_usernames = self.getFollowing()
        self.driver.find_element_by_xpath('/html/body/div[6]/div/div/div/div[1]/div/div[2]/button').click()  # close dialog window
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


if __name__ == '__main__':
    ic = InstagramChecker()
    ic.login('jordanngeorge')

    l = ic.getComparisons()
    print()
    fmt_amts = [25, 55, 35, len('Verify Status')]
    fmt_amts_str = ''
    for i in fmt_amts: fmt_amts_str += '{:' + str(i) + '}'
    print(fmt_amts_str.format('Username', 'Profile Link', 'Display Name', 'Verify Status'))
    print('-' * sum(fmt_amts))
    for item in l:
        print(fmt_amts_str.format(item['username'], item['profile_link'], item['display_name'], item['verify_status']))

    ic.closeDriver()
