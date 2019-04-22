from selenium import webdriver
import bs4
import time
import config

class Driver():
    def __init__(self):
        self.driver = webdriver.Chrome('/Users/jordangeorge/Library/Mobile Documents/com~apple~CloudDocs/F4F_Checker/chromedriver')


class InstagramChecker():
    def __init__(self, driver):
        self.driver = driver
        self.url = 'https://www.instagram.com/'
        self.followers_usernames = list()
        self.following_usernames = list()

    def login(self, profile):
        self.driver.get(self.url)

        time.sleep(2)
        self.driver.find_elements_by_tag_name("button")[0].click()

        time.sleep(2)
        self.driver.find_element_by_name('email').send_keys(config.FACEBOOK_EMAIL)
        self.driver.find_element_by_name('pass').send_keys(config.FACEBOOK_PASSWORD)
        self.driver.find_element_by_id("loginbutton").click()

        time.sleep(2)
        self.driver.get(profile)

        # go to profile
        time.sleep(2)

    def getFollowing(self):
        print('Getting people following')

        # get number of following
        numberOfFollowingList = int(self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a/span').text)

        # time.sleep(1)
        d = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a')
        d.click()

        time.sleep(1)
        element = self.driver.find_element_by_xpath("/html/body/div[3]/div/div[2]/ul/div")
        num = 0
        while num != numberOfFollowingList:
            self.driver.execute_script("return arguments[0].scrollIntoView(0, document.documentElement.scrollHeight-10);", element)
            num = len(element.find_elements_by_tag_name("li"))

        time.sleep(2)
        page = self.driver.page_source
        soup = bs4.BeautifulSoup(page, "lxml")
        ul = soup.find_all("ul")[3]

        for list in ul:
            lis = list.find_all("li")
            for li in lis:
                username = li.find_all("div")[0].find_all("div")[2].find_all("div")[0].find("a").contents[0]
                self.following_usernames.append(username)

    def getFollowers(self):
        print('Getting followers')

        # get number of followers
        num_following = int(self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a/span').text)

        # click on followers dialog
        time.sleep(1)
        d = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a')
        d.click()

        # scrolling
        time.sleep(1)
        element = self.driver.find_element_by_xpath("/html/body/div[3]/div/div[2]/ul/div")
        num = 0
        while num != num_following:
            self.driver.execute_script("return arguments[0].scrollIntoView(0, document.documentElement.scrollHeight-10);", element)
            num = len(element.find_elements_by_tag_name("li"))

        time.sleep(2)
        page = self.driver.page_source
        soup = bs4.BeautifulSoup(page, "lxml")
        ul = soup.find_all("ul")[3]

        for list in ul:
            lis = list.find_all("li")
            for li in lis:
                username = li.find_all("div")[0].find_all("div")[2].find_all("div")[0].find("a").contents[0]
                self.followers_usernames.append(username)

    def makeComparisons(self):
        for u in range(len(self.following_usernames)):
            for j in range(len(self.followers_usernames)):
                if self.following_usernames[u] == self.followers_usernames[j]:
                    break
                elif self.following_usernames[u] != self.followers_usernames[j] and j == len(self.followers_usernames)-1:
                    print(self.following_usernames[u])

    def closeDialog(self, xpath):
        self.driver.find_element_by_xpath(xpath).click()


class TwitterChecker():

    def __init__(self):
        pass

    def getFollowing(self):
        pass

    def getFollowers(self):
        pass


if __name__ == "__main__":
    driver = Driver().driver

    print()
    ic = InstagramChecker(driver)
    ic.login("https://www.instagram.com/jordanngeorge")
    ic.getFollowing()
    ic.closeDialog('/html/body/div[3]/div/div[1]/div/div[2]/button')
    ic.getFollowers()
    print()
    ic.makeComparisons()

    driver.close()
