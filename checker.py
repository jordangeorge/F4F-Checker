#!/usr/bin/python3

import bs4
from datetime import datetime
import json
import os
from dotenv import load_dotenv
import logging
from operator import itemgetter
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time

logging.basicConfig(
    filename="status.log",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

load_dotenv()

class InstagramChecker():
    def __init__(self):
        self.driver = webdriver.Chrome("./chromedriver")
        self.url = "https://www.instagram.com"
        self.wait = WebDriverWait(self.driver, 15)
        self.target_profile_username = os.getenv("INSTAGRAM_USERNAME")

    def login(self):
        # go to instagram
        self.driver.get(self.url)

        # input username and password
        time.sleep(3)
        self.driver.find_element_by_name("username").send_keys(self.target_profile_username)
        self.driver.find_element_by_name("password").send_keys(os.getenv("INSTAGRAM_PASSWORD"))
        
        # click login button
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[class='_ab8w  _ab94 _ab99 _ab9f _ab9m _ab9p _abcm']"))).click()
        
        time.sleep(5)
        # Looking for alerts such as "Espera unos minutos antes de volver a intentarlo."
        try:
            alert = self.driver.find_element_by_css_selector("div[class='_ab2z']")
            print(f"Alert found: {alert.text}\nExiting program.\n")
            logging.error(f"Need to wait before executing again. Alert found: {alert.text}")
            return False
        except:
            print("No alert found.")
            pass

        # go to profile
        try:
            self.wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/div[1]/div[1]/div/div/div/div/div[2]/div[7]/div/div/a"))).click() 
        except:
            # "Activar notificaciones" modal shows
            self.driver.get(self.url + "/" + self.target_profile_username)

        time.sleep(5)

        return True

    def scroll_through_dialog(self, dialog_ul_div_xpath, num):
        time.sleep(7)
        dialog_ul_div = self.driver.find_element_by_xpath(dialog_ul_div_xpath)
        # dialog_ul_div = self.wait.until(EC.presence_of_element_located((By.XPATH, dialog_ul_div_xpath)))

        li_num = 0
        while li_num < num:
            self.driver.execute_script("return arguments[0].scrollIntoView(0, document.documentElement.scrollHeight-10);", dialog_ul_div)
            li_num = len(dialog_ul_div.find_elements_by_tag_name("button"))
            # print(li_num,"<",num)

    def get_following(self):
        print("Getting people " + self.target_profile_username + " is following")

        # get number of following
        time.sleep(4)
        num_of_following = int(self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span[class='_ac2a']")))[2].text)

        # todo
        # click on following dialog
        time.sleep(4)
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'/following')]"))).click()
        
        self.scroll_through_dialog("/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/div[1]", num_of_following)

        following_usernames = list()

        for i in range(0, num_of_following):
            username_and_verify_status = self.driver.find_element_by_xpath("/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/div/div/div["+str(i+1)+"]/div[2]/div[1]/div/div/div/a/span/div").text.split("\n")

            username = username_and_verify_status[0]
            
            try:
                verify_status = username_and_verify_status[1]
            except:
                verify_status = "-"

            try:
                display_name = self.driver.find_element_by_xpath("/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/div/div/div["+str(i+1)+"]/div[2]/div[2]/div").text
            except:
                display_name = "-"

            following_usernames.append({
                "username": username,
                "profile_link": self.url + "/" + username,
                "display_name": display_name,
                "verify_status": verify_status
            })

        return following_usernames

    def get_followers(self):
        print("Getting people that are following " + self.target_profile_username)

        # get number of followers
        num_of_followers = int(self.driver.find_elements_by_css_selector("span[class='_ac2a']")[1].text)

        # click on followers dialog
        time.sleep(1)
        self.driver.find_element_by_xpath("/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/div[1]/div[2]/section/main/div/header/section/ul/li[2]/a").click()

        self.scroll_through_dialog("/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div[1]", num_of_followers)

        followers_usernames = list()

        for i in range(0, num_of_followers):
            username_and_verify_status = self.driver.find_element_by_xpath("/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div[1]/div/div["+str(i+1)+"]/div[2]/div[1]/div/div/div/a/span/div").text.split("\n")

            username = username_and_verify_status[0]

            try:
                verify_status = username_and_verify_status[1]
            except:
                verify_status = "-"

            try:
                display_name = self.driver.find_element_by_xpath("/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div[1]/div/div["+str(i+1)+"]/div[2]/div[2]/div").text
            except:
                display_name = "-"

            followers_usernames.append({
                "username": username,
                "profile_link": self.url + "/" + username,
                "display_name": display_name,
                "verify_status": verify_status
            })


        return followers_usernames

    def get_comparisons(self):
        following_usernames = self.get_following()
        self.driver.find_element_by_xpath("/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[1]/div/div[3]/div/button").click() # close dialog window
        followers_usernames = self.get_followers()

        result_list = list()

        for i in range(len(following_usernames)):
            for j in range(len(followers_usernames)):
                if following_usernames[i]["username"] == followers_usernames[j]["username"]:
                    break
                elif following_usernames[i]["username"] != followers_usernames[j]["username"] and j == len(followers_usernames)-1:
                    result_list.append(following_usernames[i])

        return result_list

    # TODO: refactor
    def create_ratio_sorted_csv(self, result_list, use_pickle):
        print("Creating ratio sorted csv file...")

        for user in result_list:
            print(user["username"])

            # go to profile
            self.driver.get(self.url + "/" + user["username"])
            
            print("Getting followers")

            # get number of followers
            followers_string = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span[class='_ac2a']")))[1].text
            
            # print(followers_string)

            followers_int = 0
            if "mil" in followers_string:
                # is , being registered as . at all?
                just_numbers = followers_string.split(" ")[0]
                replace_comma = just_numbers.replace(",", ".")
                convert_to_float = float(replace_comma)
                multiply = convert_to_float * 1000
                followers_int = int(multiply)
            elif "M" in followers_string:
                just_numbers = followers_string.strip("M")
                replace_comma = just_numbers.replace(",", ".")
                convert_to_float = float(replace_comma)
                multiply = convert_to_float * 1000000
                followers_int = int(multiply)
            else:
                convert_to_float = float(followers_string)
                multiply = convert_to_float
                followers_int = int(multiply)

            # print(followers_int)

            # add to dict
            user["followers"] = followers_int

            print("Getting following")

            # get number of following
            following_string = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span[class='_ac2a']")))[2].text
            
            # print(following_string)

            following_int = 0
            if "mil" in following_string:
                # is , being registered as . at all?
                just_numbers = following_string.split(" ")[0]
                replace_comma = just_numbers.replace(",", ".")
                convert_to_float = float(replace_comma)
                multiply = convert_to_float * 1000
                following_int = int(multiply)
            elif "M" in following_string:
                just_numbers = following_string.strip("M")
                replace_comma = just_numbers.replace(",", ".")
                convert_to_float = float(replace_comma)
                multiply = convert_to_float * 1000000
                following_int = int(multiply)
            else:
                convert_to_float = float(following_string)
                multiply = convert_to_float 
                following_int = int(multiply)

            # print(following_int)

            # add to dict
            user["following"] = following_int

            user["ratio"] = round(followers_int / following_int, 1)

            print(f"follower:following ratio for \"{user['username']}\": {user['ratio']}")
            print("------------------------------")

        # sort by ratio
        sorted_data = sorted(result_list, key=itemgetter("ratio"), reverse=True)
        # print(sorted_data)

        # create csv file
        dir_name = "csv"
        if not os.path.isdir(dir_name):
            os.mkdir("./results/" + dir_name)

        current_time = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        file_path = "./results/" + dir_name + "/results_" + current_time + ".csv"
        
        df = pd.DataFrame(sorted_data)
        print()
        print(df["ratio"].head())
        print()
        df.to_csv(file_path, sep=",", index=False)

        # create pickle for df
        if not os.path.isdir(dir_name):
            os.mkdir(dir_name)
        df.to_pickle(f"data_{current_time}.pkl")

    def close_driver(self):
        self.driver.close()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_driver()

def put_results_in_file(result_list, fmt_amts_str):
    dir_name = "text"
    if not os.path.isdir(dir_name):
        os.mkdir("./results/" + dir_name)

    current_time = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    file_path = "./results/" + dir_name + "/results_" + current_time + ".txt"

    results_file = open(file_path, "a")

    results_file.write(str(fmt_amts_str.format("Username", "Profile Link", "Display Name", "Verify Status")))
    results_file.write(str("\n"))
    results_file.write(str("-" * sum(fmt_amts)))
    results_file.write(str("\n"))

    for item in result_list:
        results_file.write(str(fmt_amts_str.format(item["username"], item["profile_link"], item["display_name"], item["verify_status"])))
        results_file.write(str("\n"))

    results_file.close()

    print(f"Results are located here: {file_path}")
    print()

def print_results_to_console(l, fmt_amts_str):
    print(fmt_amts_str.format("Username", "Profile Link", "Display Name", "Verify Status"))
    print("-" * sum(fmt_amts))
    for item in l:
        print(fmt_amts_str.format(item["username"], item["profile_link"], item["display_name"], item["verify_status"]))
    print()

# for sorting by another column besides "ratio"
def usePickle(sort_by_column):
    print(f"Creating {sort_by_column} sorted csv file...")

    dir_name = "pickles"
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)

    # get latest pickle file
    files = os.listdir(dir_name)
    paths = [os.path.join(dir_name, basename) for basename in files]
    print(max(paths, key=os.path.getctime))
    pickle_file_path = max(paths, key=os.path.getctime)

    # get data from pickle file
    df = pd.read_pickle(pickle_file_path)

    # sort df
    df.sort_values(sort_by_column)

    # show a few rows
    print()
    print(df[sort_by_column].head())
    print()

    # create csv file
    dir_name = "csv"
    if not os.path.isdir(dir_name):
        os.mkdir("./results/" + dir_name)

    current_time = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    csv_file_path = "./results/" + dir_name + "/results_" + current_time + ".csv"

    df.to_csv(csv_file_path, sep=",", index=False)

if __name__ == "__main__":
    logging.info("Started")

    dir_name = "results"
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)

    print()

    # Set to True and change column_to_sort_by if you want to sort by a column other than "ratio" in the csv result file. Also can be used to use old data and not have to go through the whole process below again if it's already been done once.
    use_pickle = False
    column_to_sort_by = "followers"
    if use_pickle:
        usePickle(column_to_sort_by)
        exit()
    
    ic = InstagramChecker()
    no_alert_found = ic.login()

    if no_alert_found:
        result_list = ic.get_comparisons()
        print()

        ic.create_ratio_sorted_csv(result_list)

        fmt_amts = [25, 55, 35, len("Verify Status")]
        fmt_amts_str = ""
        for i in fmt_amts: fmt_amts_str += "{:" + str(i) + "}"

        put_results_in_file(result_list, fmt_amts_str)
        # print_results_to_console(result_list, fmt_amts_str)

        print("Done.\n")

    ic.closeDriver()

    