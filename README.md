# Follow for Follow (F4F) Instagram Checker

Alternative titles:
- Instagram Mutual Follow Checker
- Petty Program

The main use case is checking if average people you followed through a 'follow for follow' agreement are following you back.

This currently does not work with 2FA. Therefore, it must be turned off in the Privacy and Security section of Instagram settings before using, which can be found [here](https://www.instagram.com/accounts/two_factor_authentication/).

##### Use Details
- View Google Chrome version for ChromeDriver by selecting "Chrome" in the menu bar. Then select "About Google Chrome".
- Download the ChromeDriver version corresponding to the version of Chrome and OS [here](https://chromedriver.chromium.org/downloads)
- Unzip the downloaded zip file
- Download the repository
- Move the chromedriver file to the downloaded repository
- Put Instagram credentials into environment variables in the command line like the following:
  ```
  export INSTAGRAM_USERNAME="xxx"
  export INSTAGRAM_PASSWORD="xxx"
  ```
- Run with a virtual environment
    - Create the virtual environment
      - `python3 -m venv f4f_venv`
    - Activate virtual environment
      - `source f4f_venv/bin/activate`
    - Put installed packages into requirements.txt file
      - `python3 -m pip install -r requirements.txt`
- Run with `python3 checker.py`
- Deactivate the virtual environment when done using the program
  - `deactivate`