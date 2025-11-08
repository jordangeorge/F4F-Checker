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
        if os.getenv("INSTAGRAM_USERNAME") is None:
            print("INSTAGRAM_USERNAME is not set")
            exit()
        if os.getenv("INSTAGRAM_PASSWORD") is None:
            print("INSTAGRAM_PASSWORD is not set")
            exit()

        # Configure Chrome options
        chrome_options = Options()
        
        # Check if running in Docker (environment variable or Chrome path detection)
        is_docker = os.path.exists("/.dockerenv") or os.getenv("RUNNING_IN_DOCKER") == "true"
        
        if is_docker:
            # Docker configuration - use system Chrome
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Use system chromedriver in Docker
            service = Service(executable_path="/usr/local/bin/chromedriver")
        else:
            # Local macOS configuration - use Chrome for Testing
            chrome_options.binary_location = "./chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            
            # Use local chromedriver
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
        # Go to instagram
        try:
            self.driver.get(self.url)
        except Exception as e:
            print(e)

            print(f"Unable to open {self.url}\nExiting program.\n")
            logging.error(f"Unable to open {self.url}. Error: {e}")

            return False
        
        # Input username and password
        self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
        self.wait.until(EC.presence_of_element_located((By.NAME, "password")))

        self.driver.find_element(By.NAME, "username").send_keys(self.target_profile_username)
        self.driver.find_element(By.NAME, "password").send_keys(os.getenv("INSTAGRAM_PASSWORD"))
        
        # Click login button - use a more reliable selector
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
        
        # Looking for alerts (red text) on the login page that will not allow user to login
        time.sleep(2)  # Wait for potential alert to appear
        try:
            alert = self.driver.find_element(By.CSS_SELECTOR, "div[class='_ab2z']")
            print(f"Alert found: {alert.text}\nExiting program.\n")
            logging.error(f"Need to wait before executing again. Alert found: {alert.text}")
            return False
        except:
            print("No alert found")
            pass

        # If next page is asking for 2FA code
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

        # Go to profile
        self.driver.get(self.url + "/" + self.target_profile_username)

        print("Login successful\n")

        return True

    def _scroll_through_dialog(self, dialog_ul_div_xpath, num, class_name):
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
            # Scroll using JavaScript
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
            
            time.sleep(1)  # Give it more time to load
            
            # Count divs
            items = self.driver.find_elements(By.CSS_SELECTOR, "div[class='x1qnrgzn x1cek8b2 xb10e19 x19rwo8q x1lliihq x193iq5w xh8yej3']")
            li_num = len(items)
            
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

    # Try multiple methods to find verification status
    def _get_verify_status(self, position, username) -> str:
        verify_status = "-"
        
        try:
            # First, get the user row element
            user_row = self.driver.find_element(By.XPATH,
                f"/html/body/div[4]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/div[1]/div/div[{position}]"
            )
            
            # # Debug: Print the HTML structure for the first few users
            # if i < 3:
            #     print(f"\n=== DEBUG: HTML structure for user {username} (position {position}) ===")
            #     html_content = user_row.get_attribute('innerHTML')
            #     # Look for verification-related content
            #     if 'verif' in html_content.lower():
            #         print("Found 'verif' in HTML!")
            #         # Extract a snippet around it
            #         idx = html_content.lower().find('verif')
            #         print(html_content[max(0, idx-100):idx+100])
            #     else:
            #         print("No 'verif' found in HTML")
            #     print("=== END DEBUG ===\n")
            
            # Method 1: Look for SVG title with verification text
            try:
                title_elements = user_row.find_elements(By.TAG_NAME, "title")
                for title_elem in title_elements:
                    title_text = title_elem.get_attribute('textContent') or title_elem.text
                    if title_text and ('verif' in title_text.lower()):
                        verify_status = title_text
                        print(f"✓ Found verification via title: {verify_status}")
                        break
            except Exception as e:
                print(f"Method 1 failed: {e}")
            
            # Method 2: Look for aria-label with verification
            if verify_status == "-":
                try:
                    verified_elements = user_row.find_elements(By.XPATH, ".//*[contains(@aria-label, 'erif')]")
                    if verified_elements:
                        verify_status = verified_elements[0].get_attribute('aria-label')
                        print(f"✓ Found verification via aria-label: {verify_status}")
                except Exception as e:
                    print(f"Method 2 failed: {e}")
            
            # Method 3: Look for specific verification SVG
            if verify_status == "-":
                try:
                    svg_elements = user_row.find_elements(By.TAG_NAME, "svg")
                    for svg in svg_elements:
                        aria_label = svg.get_attribute('aria-label')
                        if aria_label and 'verif' in aria_label.lower():
                            verify_status = aria_label
                            print(f"✓ Found verification via SVG aria-label: {verify_status}")
                            break
                except Exception as e:
                    print(f"Method 3 failed: {e}")
                    
        except Exception as e:
            print(f"Error checking verification for {username}: {e}")
            verify_status = "-"
        
        return verify_status

    def _get_following(self):
        print("Getting people \"" + self.target_profile_username + "\" is following...")

        # Wait for page to be fully loaded
        time.sleep(2)

        # Get number of following
        try:
            following_link = self.wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href,'/following')]")))
            following_text = following_link.text
            num_of_following = int(re.search(r'[\d,]+', following_text.replace(',', '')).group())
        except Exception as e:
            print(f"Error getting following count: {e}")
            raise

        # Click on following dialog
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'/following')]"))).click()
        
        # Wait for dialog to open
        time.sleep(2)
        
        actual_count = self._scroll_through_dialog(
            "/html/body/div[4]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]",
            num_of_following,
            "x1dm5mii x16mil14 xiojian x1yutycm x1lliihq x193iq5w xh8yej3"
        )
        
        # Use the actual count found instead of the expected count
        items_to_process = min(actual_count, num_of_following)
        print(f"Processing {items_to_process} items...")

        following_usernames = list()

        for i in range(0, items_to_process):
            position = str(i+1)

            try:
                user_info = self.driver.find_element(By.XPATH,
                    "/html/body/div[4]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/div[1]/div/div["
                    +position+
                    "]/div/div/div/div[2]/div/div"
                    ).text.split("\n")
            except:
                user_info = ["-", "-"]

            username = user_info[0]
            
            try:
                display_name = user_info[1]
            except:
                display_name = "-"

            verify_status = self._get_verify_status(position, username)

            following_usernames.append({
                "username": username,
                "profile_link": self.url + "/" + username,
                "display_name": display_name,
                "verify_status": verify_status
            })

        print()

        return following_usernames

    def _get_followers(self):
        print("Getting people that are following \"" + self.target_profile_username + "\"...")

        # Get number of followers
        try:
            followers_link = self.wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href,'/followers')]")))
            followers_text = followers_link.text
            num_of_followers = int(re.search(r'[\d,]+', followers_text.replace(',', '')).group())
        except Exception as e:
            print(f"Error getting followers count: {e}")
            raise

        # Click on followers dialog
        self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[2]/div[1]/section/main/div/div/header/div/section[2]/div/div[3]/div[2]/a").click()

        actual_count = self._scroll_through_dialog(
            "/html/body/div[4]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]",
            num_of_followers,
            "x1i10hfl x1qjc9v5 xjbqb8w xjqpnuy xa49m3k xqeqjp1 x2hbi6w x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xdl72j9 x2lah0s xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r x2lwn1j xeuugli xexx8yu x4uap5 x18d9i69 xkhd6sd x1n2onr6 x16tdsg8 x1hl2dhg xggy1nq x1ja2u2z x1t137rt x1q0g3np x87ps6o x1lku1pv x1a2a7pz xh8yej3 x193iq5w x1lliihq x1dm5mii x16mil14 xiojian x1yutycm")

        # Use the actual count found instead of the expected count
        items_to_process = min(actual_count, num_of_followers)
        print(f"Processing {items_to_process} items...")

        followers_usernames = list()

        for i in range(0, items_to_process):
            position = str(i+1)

            try:
                user_info_element = self.driver.find_element(By.XPATH,
                    "/html/body/div[4]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/div[1]/div/div["
                    +position+
                    "]/div/div/div/div[2]/div/div"
                    ).text.split("\n")
            except:
                user_info_element = ["-", "-"]

            username = user_info_element[0]
            
            try:
                display_name = user_info_element[1]
            except:
                display_name = "-"

            verify_status = self._get_verify_status(position, username)

            followers_usernames.append({
                "username": username,
                "profile_link": self.url + "/" + username,
                "display_name": display_name,
                "verify_status": verify_status
            })

        print()

        return followers_usernames

    def get_comparisons(self):
        # Wait for page to be fully loaded
        time.sleep(2)

        following_usernames = self._get_following()
        self.driver.find_element(
            By.XPATH,
            "/html/body/div[4]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[1]/div/div[3]/div/button"
            ).click() # close dialog window
        followers_usernames = self._get_followers()

        result_list = list()

        for i in range(len(following_usernames)):
            for j in range(len(followers_usernames)):
                iu = following_usernames[i]["username"] 
                ju = followers_usernames[j]["username"]
                
                if iu == ju:
                    break
                elif iu != ju and j == len(followers_usernames)-1:
                    result_list.append(following_usernames[i])

        return result_list

    def _get_count(self, position):
        """
        Get a count value from Instagram page and parse it to integer.
        Handles formats like: '1,234', '1.5K', '2.3M', '5 mil', '1.2B'
        
        Args:
            position: Index of the element in the found elements list
            
        Returns:
            Integer value of the count
        """
        category_string = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, f"span[class='x5n08af x1s688f']")))[position].text
        
        # Define multipliers for different suffixes
        multipliers = {
            'k': 1000, # thousand, english
            'mil': 1000, # thousand, spanish
            'm': 1000000, # million, english
            'm': 1000000, # million, spanish
            'mm': 1000000000, # billion, english
            'b': 1000000000, # billion, spanish
        }
        
        match = re.match(r'^([0-9.,]+)\s*([a-zA-Z]*)$', category_string.strip())
        
        if not match:
            print(f"Warning: Could not parse count string: '{category_string}'")
            return 0
        
        number_str, suffix = match.groups()
        number = float(number_str.replace(',', '.'))
        multiplier = multipliers.get(suffix.lower(), 1)
        return int(number * multiplier)

    def create_ratio_sorted_csv(self, result_list):
        print("Creating ratio sorted csv file...\n")

        for user in result_list:
            print("Profile:", user["username"])

            # Go to profile
            self.driver.get(self.url + "/" + user["username"])
            
            # Get number of followers
            print("Getting followers")
            followers_int = self._get_count(1)
            user["followers"] = followers_int

            # Get number of following
            print("Getting following")
            following_int = self._get_count(2)
            user["following"] = following_int
            
            # Anticipate division by zero
            if following_int == 0:
                user["ratio"] = followers_int
            else:
                user["ratio"] = round(followers_int / following_int, 1)

            print(f"follower:following ratio for \"{user['username']}\": {user['ratio']}")
            print("------------------------------")

        # Sort by ratio
        sorted_data = sorted(result_list, key=itemgetter("ratio"), reverse=True)

        # Create csv file
        dir_name = "./results/csv/"
        create_dir_if_it_does_not_exist(dir_name)

        current_time = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        csv_file_path = dir_name + "results_" + current_time + ".csv"
        
        df = pd.DataFrame(sorted_data)
        df.to_csv(csv_file_path, sep=",", index=False, encoding='utf-8')

        print(f"\nCSV results are located here: {csv_file_path}")

        # Create pickle for df
        dir_name = "pickles/"
        create_dir_if_it_does_not_exist(dir_name)
        pickle_file_path = f"{dir_name}data_{current_time}.pkl"
        df.to_pickle(pickle_file_path)

    def close_driver(self):
        self.driver.close()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_driver()

def put_results_in_file(result_list: list, fmt_amts_str: str) -> None:
    dir_name = "./results/text"
    create_dir_if_it_does_not_exist(dir_name)

    current_time = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    text_file_path = dir_name + "/results_" + current_time + ".txt"

    results_file = open(text_file_path, "a", encoding='utf-8')

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

# For sorting by another column besides "ratio"
def use_pickle(sort_by_column):
    print(f"Creating {sort_by_column} sorted csv file...")

    dir_name = "pickles"
    create_dir_if_it_does_not_exist(dir_name)

    # Get latest pickle file
    files = os.listdir(dir_name)
    paths = [os.path.join(dir_name, basename) for basename in files]
    pickle_file_path = max(paths, key=os.path.getctime)

    # Get data from pickle file
    df = pd.read_pickle(pickle_file_path)

    # Sort df
    df = df.sort_values(
        by=sort_by_column,
        ascending=False
    )

    # Create csv file
    dir_name = "./results/csv"
    create_dir_if_it_does_not_exist(dir_name)

    current_time = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    csv_file_path = dir_name + "/results_" + current_time + ".csv"

    df.to_csv(csv_file_path, sep=",", index=False)

    print(f"CSV results are located here: {csv_file_path}\n")

# Browser will stay open to allow for inspection
def pause_for_inspection():
    print("\n" + "="*80)
    print("BROWSER IS NOW PAUSED FOR INSPECTION")
    print("Press ENTER in the terminal when you're done inspecting...")
    print("="*80)
    input()

def create_dir_if_it_does_not_exist(dir_name):
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)

if __name__ == "__main__":
    logging.info("Started")

    dir_name = "results"
    create_dir_if_it_does_not_exist(dir_name)

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