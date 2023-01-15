# Follow for Follow (F4F) Instagram Checker

Alternative title: Instagram Mutual Follow Checker

The main use case is checking if average people you followed through a 'follow for follow' agreement are following you back.

Currently does not work with 2FA. Therefore, it must be turned off in the Privacy and Security section of Instagram settings before using which can be found [here](https://www.instagram.com/accounts/privacy_and_security/).

##### Use Details
- View Google Chrome version for ChromeDriver by selecting "Chrome" in the menu bar. Then select "About Google Chrome".
- Download the ChromeDriver version corresponding to the version of Chrome and OS [here](https://chromedriver.chromium.org/downloads)
- Unzip the downloaded zip file
- Download the repo
- Move the chromedriver file to the downloaded repo
- Put Instagram credentials into environment variables in the command line like the following:
  ```
  export INSTAGRAM_USERNAME="xxx"
  export INSTAGRAM_PASSWORD="xxx"
  ```
- Run with `python3 checker.py`
