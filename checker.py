from selenium import webdriver
import bs4
import time
import config
import json

class InstagramChecker():
    def __init__(self):
        self.driver = webdriver.Chrome('./chromedriver')
        self.url = 'https://www.instagram.com/'

    def login(self, target_profile_username):
        # go to instagram
        self.driver.get(self.url)

        # click 'login with facebook' button
        time.sleep(2)
        self.driver.find_elements_by_tag_name('button')[1].click()

        # login with facebook
        time.sleep(2)
        self.driver.find_element_by_name('email').send_keys(config.FACEBOOK_EMAIL)
        self.driver.find_element_by_name('pass').send_keys(config.FACEBOOK_PASSWORD)
        self.driver.find_element_by_id('loginbutton').click()

        # reload home page
        time.sleep(2)
        self.driver.get(self.url)

        # click on "Continue as 'username'"
        time.sleep(4)
        self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/article/div[2]/div[1]/div/div[2]/button').click()

        # go to profile
        time.sleep(2)
        self.driver.get(self.url + target_profile_username)

        time.sleep(2)

    def getFollowing(self):
        print('Getting people following')

        # get number of following
        number_of_following = int(self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a/span').text)

        # click on following dialog
        time.sleep(3)
        self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a').click()

        # scrolling
        time.sleep(3)
        dialog_ul_div = self.driver.find_element_by_xpath('/html/body/div[4]/div/div[2]/ul')
        li_num = 0
        while li_num != number_of_following:
            self.driver.execute_script('return arguments[0].scrollIntoView(0, document.documentElement.scrollHeight-10);', dialog_ul_div)
            li_num = len(dialog_ul_div.find_elements_by_tag_name('li'))

        time.sleep(2)
        page = self.driver.page_source
        soup = bs4.BeautifulSoup(page, 'lxml')
        ul_div = soup.find_all('ul')
        if len(ul_div) == 3:
            ul_div = ul_div[2]
        elif len(ul_div) == 4:
            ul_div = ul_div[3]

        following_usernames = list()

        lis = ul_div.find_all('li')
        for li in lis:
            try: status = li.find_all('div')[0].find_all('div')[0].find_all('div')[1].find('span').contents[0]
            except: status = '-'

            username = li.find_all('div')[0].find_all('div')[0].find_all('div')[1].find('a').contents[0]
            profile_link = self.url + username

            temp_dict = {}
            temp_dict['username'] = username
            temp_dict['profile_link'] = profile_link
            temp_dict['verify_status'] = status

            following_usernames.append(temp_dict)

        return following_usernames

    def getFollowers(self):
        print('Getting followers')

        # get number of followers
        num_of_followers = int(self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a/span').text)

        # click on followers dialog
        time.sleep(1)
        self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a').click()

        # scrolling
        time.sleep(3)
        dialog_ul_div = self.driver.find_element_by_xpath('/html/body/div[4]/div/div[2]/ul/div')
        li_num = 0
        while li_num != num_of_followers:
            self.driver.execute_script('return arguments[0].scrollIntoView(0, document.documentElement.scrollHeight-10);', dialog_ul_div)
            li_num = len(dialog_ul_div.find_elements_by_tag_name('li'))

        time.sleep(2)
        page = self.driver.page_source
        soup = bs4.BeautifulSoup(page, 'lxml')
        ul_div = soup.find_all('ul')
        if len(ul_div) == 3:
            ul_div = ul_div[2]
        elif len(ul_div) == 4:
            ul_div = ul_div[3]

        followers_usernames = list()

        lis = ul_div.find_all('li')
        for li in lis:
            username = li.find_all('div')[0].find_all('div')[0].find_all('div')[1].find('a').contents[0]
            profile_link = self.url + username

            temp_dict = {}
            temp_dict['username'] = username
            temp_dict['profile_link'] = profile_link

            followers_usernames.append(temp_dict)

        return followers_usernames

    def getComparisons(self):
        following_usernames = self.getFollowing()
        self.driver.find_element_by_xpath('/html/body/div[4]/div/div[1]/div/div[2]/button').click() # close dialog window
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
    print()
    ic = InstagramChecker()
    ic.login('jordanngeorge')

    l = ic.getComparisons()
    print()
    print('{:30}{:60}{}'.format('Username', 'Profile Link', 'Verify Status'))
    print('-' * (30+60+len('Verify Status')))
    for item in l:
        print('{:30}{:60}{}'.format(item['username'], item['profile_link'], item['verify_status']))

    ic.closeDriver()
