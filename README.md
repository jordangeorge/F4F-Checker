# Follow for Follow (F4F) Instagram Checker

Alternative title: Instagram Mutual Follow Checker

The main use case is checking if average people you followed through a 'follow for follow' agreement are following you back.

Currently does not work with 2FA.

##### Use Details
- View Google Chrome version for ChromeDriver by selecting "Chrome" in the menu bar. Then select "About Google Chrome".
- Download the ChromeDriver version corresponding to the version of Chrome and OS [here](https://chromedriver.chromium.org/downloads)
- Unzip the downloaded zip file
- Download the repo
- Move the chromedriver file to the downloaded repo
- Put Facebook credentials into environment variables in the command line like the following:
  ```
  export FACEBOOK_EMAIL='xxx'
  export FACEBOOK_PASSWORD='xxx'
  ```
- Run with `python3 checker.py`
