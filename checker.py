#!/usr/bin/python3

import bs4
from datetime import datetime
import json
import os
from dotenv import load_dotenv
import logging
from operator import itemgetter
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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
        # Configure Chrome options to use Chrome for Testing
        chrome_options = Options()
        chrome_options.binary_location = "./chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
        
        # Add arguments to help Chrome start properly
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        # Create Chrome service with the chromedriver
        service = Service(executable_path="./chromedriver")
        
        # Create the webdriver instance
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.url = "https://www.instagram.com"
        self.wait = WebDriverWait(self.driver, 15)
        self.target_profile_username = os.getenv("INSTAGRAM_USERNAME")

    def login(self):
        print("Logging in")

        # TODO: test and handle appropriately
            # occurs when i turn vpn off
        # go to instagram
        try:
            self.driver.get(self.url)
        except Exception as e:
            print(e)

            print(f"Unable to open {self.url}\nExiting program.\n")
            logging.error(f"Unable to open {self.url}. Error: {e}")

            return False
        
        # input username and password
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[class='_aa4b _add6 _ac4d _ap35']")))

        self.driver.find_element(By.NAME, "username").send_keys(self.target_profile_username)
        self.driver.find_element(By.NAME, "password").send_keys(os.getenv("INSTAGRAM_PASSWORD"))
        
        # click login button - use a more reliable selector
        # Try to find the button by type and text content
        try:
            # First, try to find by button type
            login_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
            login_button.click()
        except:
            try:
                # If that fails, try by text content
                login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Log in') or contains(text(), 'Log In')]")))
                login_button.click()
            except:
                # Last resort: use Enter key
                print("Using Enter key to submit form...")
                self.driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
        
        # looking for alerts (red text) on the login page that will not allow user to login
        time.sleep(2)  # Wait for potential alert to appear
        try:
            alert = self.driver.find_element(By.CSS_SELECTOR, "div[class='_ab2z']")
            print(f"Alert found: {alert.text}\nExiting program.\n")
            logging.error(f"Need to wait before executing again. Alert found: {alert.text}")
            return False
        except:
            print("No alert found")
            pass

        # if next page is asking for 2FA code
        try:
            self.wait = WebDriverWait(self.driver, 15)
            mfa_text = self.wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/section/main/div/div/div[1]/div[2]/div"))).text
            if "Ingresa el código que enviamos al número que termina en" in mfa_text or "Enter the code we sent to your number ending in" in mfa_text:
                print(f"\nThe page is displaying \"{mfa_text}\" This means that two-factor authentication is not disabled. Please disable two-factor authentication at https://www.instagram.com/accounts/two_factor_authentication/.\n\nExiting program.\n")
                logging.error(f"Need to disable 2FA.")
                return False
        except:
            print("2FA disabled")
            pass

        # # go to profile
        # self.wait = WebDriverWait(self.driver, 10)
        # try:
        #     self.wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/div[1]/div[1]/div/div/div/div/div[2]/div[7]/div/div/a"))).click() 
        # except:
        #     # "Activar notificaciones" modal shows
        #     # or
        #     # "¿Guardar tu información de inicio de sesión?" modal shows
        #     self.driver.get(self.url + "/" + self.target_profile_username)

        # go to profile
        self.driver.get(self.url + "/" + self.target_profile_username)

        print("Login successful\n")

        return True

    def scroll_through_dialog(self, dialog_ul_div_xpath, num, class_name):
        print("Scrolling")

        time.sleep(3)
        
        # Try to find the scrollable dialog div with multiple approaches
        dialog_ul_div = None
        
        # Method 1: Try original XPath
        try:
            dialog_ul_div = self.driver.find_element(By.XPATH, dialog_ul_div_xpath)
            print("Found dialog using original XPath")
        except:
            pass
        
        # Method 2: Find div with role="dialog" and its scrollable container
        if not dialog_ul_div:
            try:
                # Find the dialog first
                dialog = self.driver.find_element(By.CSS_SELECTOR, "div[role='dialog']")
                # Find the scrollable div inside the dialog
                dialog_ul_div = dialog.find_element(By.CSS_SELECTOR, "div[style*='overflow']")
                print("Found dialog using role='dialog'")
            except:
                pass
        
        # Method 3: Find any div with overflow-y: auto or scroll
        if not dialog_ul_div:
            try:
                dialog_ul_div = self.driver.find_element(By.XPATH, "//div[contains(@style, 'overflow-y')]")
                print("Found dialog using overflow-y")
            except:
                pass
        
        # Method 4: Try to find a div that can scroll
        if not dialog_ul_div:
            try:
                # Execute JavaScript to find scrollable divs
                scrollable_div = self.driver.execute_script("""
                    var divs = document.querySelectorAll('div[role="dialog"] div');
                    for (var i = 0; i < divs.length; i++) {
                        if (divs[i].scrollHeight > divs[i].clientHeight) {
                            return divs[i];
                        }
                    }
                    return null;
                """)
                if scrollable_div:
                    dialog_ul_div = scrollable_div
                    print("Found dialog using JavaScript")
            except:
                pass
        
        if not dialog_ul_div:
            print("ERROR: Could not find scrollable dialog")
            return 0

        print(f"Found scrollable dialog. Starting to scroll for {num} items...")
        
        li_num = 0
        scroll_attempts = 0
        max_scrolls = num // 5 + 30  # More scrolls for larger lists
        last_count = 0
        stable_count = 0
        
        # Initial count
        try:
            li_num = len(self.driver.find_elements(By.CSS_SELECTOR, "div[role='dialog'] a[href*='/']"))
            print(f"Initial item count: {li_num}")
        except:
            pass
        
        while li_num < num and scroll_attempts < max_scrolls:
            # Scroll using JavaScript - more reliable
            try:
                # Method 1: Scroll the element itself
                scroll_height = self.driver.execute_script("return arguments[0].scrollHeight", dialog_ul_div)
                client_height = self.driver.execute_script("return arguments[0].clientHeight", dialog_ul_div)
                scroll_top = self.driver.execute_script("return arguments[0].scrollTop", dialog_ul_div)
                
                # Scroll down by client height
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].clientHeight", dialog_ul_div)
                
                # Also try scrolling to bottom
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", dialog_ul_div)
            except Exception as e:
                print(f"Scroll error: {e}")
            
            time.sleep(2)  # Give it more time to load
            
            # Count items using multiple methods
            try:
                # Count all links in the dialog that look like profile links
                items = self.driver.find_elements(By.CSS_SELECTOR, "div[role='dialog'] a[href*='/']")
                # Filter to only count unique profile links (not buttons, etc)
                filtered_items = []
                for item in items:
                    href = item.get_attribute('href')
                    if href and '/p/' not in href and '/reel/' not in href:
                        # Skip if it's a real profile link
                        filtered_items.append(item)
                li_num = len(filtered_items)
            except:
                try:
                    # Fallback: just count all links
                    li_num = len(self.driver.find_elements(By.CSS_SELECTOR, "div[role='dialog'] a"))
                except:
                    pass
            
            scroll_attempts += 1
            
            # Print progress every scroll for debugging
            print(f"Scroll {scroll_attempts}: Found {li_num} items (target: {num})")
            
            # Check if we're making progress
            if li_num > last_count:
                print(f"  Progress! Found {li_num - last_count} new items")
                stable_count = 0
                last_count = li_num
            else:
                stable_count += 1
                if stable_count >= 3:  # No progress for 3 scrolls
                    print(f"No new items loaded after {stable_count} scrolls. Stopping.")
                    break
            
            # If we've found enough items, break
            if li_num >= num:
                print(f"Found all {num} items!")
                break
            
            # If we hit max scrolls, break
            if scroll_attempts >= max_scrolls:
                print(f"Reached max scrolls ({max_scrolls}), stopping with {li_num} items found")
                break

        print(f"Done scrolling. Found {li_num} items out of {num} target")
        return li_num

    def get_following(self):
        print("Getting people \"" + self.target_profile_username + "\" is following...")

        # Wait for page to be fully loaded
        time.sleep(2)

        # get number of following - try multiple approaches
        try:
            # Try the old selector first
            num_of_following = int(self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span[class='html-span xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1hl2dhg x16tdsg8 x1vvkbs']")))[2].text)
        except:
            try:
                # Try finding all links that contain '/following'
                following_link = self.wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href,'/following')]")))
                following_text = following_link.text
                # Extract number from text like "123 following"
                num_of_following = int(re.search(r'[\d,]+', following_text.replace(',', '')).group())
            except Exception as e:
                print(f"Error getting following count: {e}")
                raise

        # click on following dialog
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'/following')]"))).click()
        
        # Wait for dialog to open
        time.sleep(2)
        
        actual_count = self.scroll_through_dialog(
            "/html/body/div[4]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]",
            num_of_following,
            "x1dm5mii x16mil14 xiojian x1yutycm x1lliihq x193iq5w xh8yej3"
        )
        
        # Use the actual count found instead of the expected count
        items_to_process = min(actual_count, num_of_following)
        print(f"Processing {items_to_process} items...")

        following_usernames = list()

        # pause_for_inspection()

        for i in range(0, items_to_process):
            position = str(i+1)

            username_and_display_name = self.driver.find_element(By.XPATH,
                "/html/body/div[4]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/div[1]/div/div["
                +position+
                "]/div/div/div/div[2]/div/div"
                ).text.split("\n")

            print(f"{username_and_display_name=}")

            username = username_and_display_name[0]
            
            try:
                display_name = username_and_display_name[1]
            except:
                display_name = "-"

            try:
                verify_status = self.driver.find_element(By.XPATH,
                "/html/body/div[4]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/div[1]/div/div["
                +position+
                "]/div/div/div/div[2]/div/div/div/div/span/div/a/div/div/div/svg/title"
                ).text
            except:
                verify_status = "-"

            following_usernames.append({
                "username": username,
                "profile_link": self.url + "/" + username,
                "display_name": display_name,
                "verify_status": verify_status
            })

        print()

        return following_usernames

    def get_followers(self):
        print("Getting people that are following \"" + self.target_profile_username + "\"...")

        # get number of followers - try multiple approaches
        try:
            # Try the old selector first
            num_of_followers = int(self.driver.find_elements(By.CSS_SELECTOR, "span[class='_ac2a']")[1].text)
        except:
            try:
                # Try finding the followers link
                followers_link = self.wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href,'/followers')]")))
                followers_text = followers_link.text
                # Extract number from text like "123 followers"
                num_of_followers = int(re.search(r'[\d,]+', followers_text.replace(',', '')).group())
            except Exception as e:
                print(f"Error getting followers count: {e}")
                raise

        # click on followers dialog
        self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/ul/li[2]/a").click()

        self.scroll_through_dialog(
            "/html/body/div[2]/div/div/div[3]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div[1]",
            num_of_followers,
            "x1i10hfl x1qjc9v5 xjbqb8w xjqpnuy xa49m3k xqeqjp1 x2hbi6w x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xdl72j9 x2lah0s xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r x2lwn1j xeuugli xexx8yu x4uap5 x18d9i69 xkhd6sd x1n2onr6 x16tdsg8 x1hl2dhg xggy1nq x1ja2u2z x1t137rt x1q0g3np x87ps6o x1lku1pv x1a2a7pz xh8yej3 x193iq5w x1lliihq x1dm5mii x16mil14 xiojian x1yutycm")

        followers_usernames = list()

        for i in range(0, num_of_followers):
            position = str(i+1)

            username_and_verify_status = self.driver.find_element(By.XPATH,
                "/html/body/div[2]/div/div/div[3]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div/div/div["
                +position+
                "]/div/div/div/div[2]/div/div/span[1]/span/div/div/div/a/span/div"
                ).text.split("\n")

            username = username_and_verify_status[0]

            try:
                verify_status = username_and_verify_status[1]
            except:
                verify_status = "-"

            try:
                display_name = self.driver.find_element(By.XPATH,
                    "/html/body/div[2]/div/div/div[3]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div/div/div["
                    +position+
                    "]/div/div/div/div[2]/div/div/span[2]/span"
                    ).text
            except:
                display_name = "-"

            followers_usernames.append({
                "username": username,
                "profile_link": self.url + "/" + username,
                "display_name": display_name,
                "verify_status": verify_status
            })

        print()

        return followers_usernames

    def get_comparisons(self):
        following_usernames = self.get_following()
        self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[3]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[1]/div/div[3]/div/button").click() # close dialog window
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
    def create_ratio_sorted_csv(self, result_list):
        print("Creating ratio sorted csv file...\n")

        for user in result_list:
            print("Profile:", user["username"])

            # go to profile
            self.driver.get(self.url + "/" + user["username"])
            
            print("Getting followers")

            # get number of followers
            followers_string = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span[class='_ac2a']")))[1].text
            
            followers_int = 0
            if "mil" in followers_string:
                # todo: is , being registered as . at all for different countries?
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

            # add to dict
            user["followers"] = followers_int

            print("Getting following")

            # get number of following
            following_string = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span[class='_ac2a']")))[2].text
            
            following_int = 0
            if "mil" in following_string:
                # todo: is , being registered as . at all?
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

            # add to dict
            user["following"] = following_int

            user["ratio"] = round(followers_int / following_int, 1)

            print(f"follower:following ratio for \"{user['username']}\": {user['ratio']}")
            print("------------------------------")

        # sort by ratio
        sorted_data = sorted(result_list, key=itemgetter("ratio"), reverse=True)

        # create csv file
        dir_name = "./results/csv/"
        if not os.path.isdir(dir_name):
            os.mkdir(dir_name)

        current_time = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        csv_file_path = dir_name + "/results_" + current_time + ".csv"
        
        df = pd.DataFrame(sorted_data)
        df.to_csv(csv_file_path, sep=",", index=False)

        print(f"\nCSV results are located here: {csv_file_path}")

        # create pickle for df
        dir_name = "pickles/"
        if not os.path.isdir(dir_name):
            os.mkdir(dir_name)
        pickle_file_path = f"{dir_name}data_{current_time}.pkl"
        df.to_pickle(pickle_file_path)

    def close_driver(self):
        self.driver.close()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_driver()

def put_results_in_file(result_list: list, fmt_amts_str: str) -> None:
    dir_name = "./results/text"
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)

    current_time = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    text_file_path = dir_name + "/results_" + current_time + ".txt"

    results_file = open(text_file_path, "a")

    results_file.write(str(fmt_amts_str.format(
        "Username",
        "Profile Link",
        "Display Name",
        "Verify Status")))
    results_file.write(str("\n"))
    results_file.write(str("-" * sum(fmt_amts)))
    results_file.write(str("\n"))

    for item in result_list:
        results_file.write(str(fmt_amts_str.format(
            item["username"],
            item["profile_link"],
            item["display_name"],
            item["verify_status"])))
        results_file.write(str("\n"))

    results_file.close()

    print(f"Text results are located here: {text_file_path}\n")

def print_results_to_console(l, fmt_amts_str):
    print(fmt_amts_str.format("Username", "Profile Link", "Display Name", "Verify Status"))
    print("-" * sum(fmt_amts))
    for item in l:
        print(fmt_amts_str.format(
            item["username"],
            item["profile_link"],
            item["display_name"],
            item["verify_status"]))
    print()

# for sorting by another column besides "ratio"
def use_pickle(sort_by_column):
    print(f"Creating {sort_by_column} sorted csv file...")

    dir_name = "pickles"
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)

    # get latest pickle file
    files = os.listdir(dir_name)
    paths = [os.path.join(dir_name, basename) for basename in files]
    pickle_file_path = max(paths, key=os.path.getctime)

    # get data from pickle file
    df = pd.read_pickle(pickle_file_path)

    # sort df
    df = df.sort_values(
        by=sort_by_column,
        ascending=False
    )

    # create csv file
    dir_name = "./results/csv"
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)

    current_time = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    csv_file_path = dir_name + "/results_" + current_time + ".csv"

    df.to_csv(csv_file_path, sep=",", index=False)

    print(f"CSV results are located here: {csv_file_path}\n")


# PAUSE FOR INSPECTION - Browser will stay open to allow for inspection
def pause_for_inspection():
    print("\n" + "="*80)
    print("BROWSER IS NOW PAUSED FOR INSPECTION")
    print("The following dialog should be open.")
    print("You can:")
    print("  1. Right-click any element and select 'Inspect' to see its XPath")
    print("  2. Find the scrollable container in the dialog")
    print("  3. Note the XPath of the scrollable div")
    print()
    print("Press ENTER in the terminal when you're done inspecting...")
    print("="*80)
    input()

if __name__ == "__main__":
    logging.info("Started")

    dir_name = "results"
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)

    print()

    # Set use_pickle_flag to True and change column_to_sort_by if you want to sort by a column other than "ratio" in the csv result file. Also can be used to use old data and not have to go through the whole process below again if it's already been done once.
    use_pickle_flag = False
    # use_pickle_flag = True
    column_to_sort_by = "followers"
    if use_pickle_flag:
        use_pickle(column_to_sort_by)
        logging.info("Completed")
        exit()
    
    ic = InstagramChecker()
    no_login_issue_found = ic.login()

    if no_login_issue_found:
        result_list = ic.get_comparisons()
        print()

        ic.create_ratio_sorted_csv(result_list)

        fmt_amts = [25, 55, 35, len("Verify Status")]
        fmt_amts_str = ""
        for i in fmt_amts: fmt_amts_str += "{:" + str(i) + "}"

        put_results_in_file(result_list, fmt_amts_str)
        # print_results_to_console(result_list, fmt_amts_str)

        print("Done\n")

    ic.close_driver()
    
    logging.info("Completed")