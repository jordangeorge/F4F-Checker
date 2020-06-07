# Follow for Follow (F4F) Instagram Checker
The main use case is checking if average people you followed through a 'follow for follow' agreement are following you back.

##### Use Details
- View Google Chrome version for ChromeDriver by selecting "Chrome" in the menu bar. Then select "About Google Chrome".
- Download the ChromeDriver version corresponding to the version of Chrome and OS [here](https://chromedriver.chromium.org/downloads)
- Unzip the downloaded zip file
- Download the repo
- Move the chromedriver file to the downloaded repo
- Put Facebook credentials into a config.py file like the following:
  ```
  FACEBOOK_EMAIL='xxx'
  FACEBOOK_PASSWORD='xxx'
  ```
- Run with `python3 checker.py`
