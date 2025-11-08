# Follow for Follow (F4F) Instagram Checker

Alternative titles:
- Instagram Mutual Follow Checker
- Petty Program

The main use case is checking if average people you followed through a "follow for follow" agreement are following you back.

In other words, this shows you people you're following that aren't following you back. For most people this might mean seeing a lot of verified or influencer-like accounts. For profiles that are a lot more private and personal and only follow people that they know, this might mean seeing very useful information about who in their life has unfollowed them.

## Prerequisites

- **Turn off VPN** - Instagram may block requests from VPN IPs
- **Disable 2FA** - This tool currently does not work with two-factor authentication. Disable it temporarily in [Instagram's Password and Security settings](https://accountscenter.instagram.com/password_and_security/two_factor/?theme=dark)
- **Instagram Credentials** - Your username and password

## Installation & Usage

You can run this tool either with **Docker** (recommended) or **locally** on your machine.

---

### Option 1: Docker (Recommended)

Docker provides a consistent environment and handles all dependencies automatically, including Chrome and ChromeDriver.

#### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) installed
- [Docker Compose](https://docs.docker.com/compose/install/) installed

#### Quick Start (Easiest)

1. **Clone the repository**
```bash
git clone <repository-url>
cd F4F-Checker
```

2. **Set up environment variables**

Create a `.env` file in the project root:
```bash
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
```

3. **Run the helper script**
```bash
./run-docker.sh
```

The script will:
- Check if Docker is installed and running
- Create a `.env` file if needed (prompts for credentials)
- Create necessary directories
- Build and run the Docker container
- Clean up when finished

#### Manual Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd F4F-Checker
```

2. **Set up environment variables**

Create a `.env` file in the project root:
```bash
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
```

> **Note:** Never commit your `.env` file to version control. It's already in `.gitignore`.

3. **Build and run with Docker Compose**
```bash
docker-compose up --build
```

The tool will:
- Automatically set up Chrome and ChromeDriver in headless mode
- Log into Instagram
- Compare your followers and following
- Generate results in `results/csv/` and `results/text/`
- Save data snapshots in `pickles/`

4. **Cleanup**
```bash
docker-compose down
```

---

### Option 2: Local Installation (macOS)

Run directly on your machine without Docker.

#### Prerequisites
- Python 3.10+
- Google Chrome installed
- ChromeDriver matching your Chrome version

#### Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd F4F-Checker
```

2. **Install Google Chrome** (if not already installed)

3. **Download ChromeDriver**
   - Check your Chrome version: Chrome menu → "About Google Chrome"
   - Download matching ChromeDriver from [chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads)
   - Extract and move the `chromedriver` file to the project directory

4. **Set up Python virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. **Set environment variables**
```bash
export INSTAGRAM_USERNAME="your_username"
export INSTAGRAM_PASSWORD="your_password"
```

Or create a `.env` file:
```
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
```

6. **Run the script**
```bash
python checker.py
```

7. **View results** (same as Docker option above)

8. **Deactivate virtual environment**
```bash
deactivate
```

---

## Output Files

The tool generates three types of output:

1. **CSV Results** - `results/csv/results_YYYY-MM-DD_HHMMSS.csv`
   - Sorted by follower-to-following ratio (highest first)
   - Columns: username, profile_link, display_name, verify_status, followers, following, ratio

2. **Text Results** - `results/text/results_YYYY-MM-DD_HHMMSS.txt`
   - Human-readable format

3. **Pickle Files** - `pickles/data_YYYY-MM-DD_HHMMSS.pkl`
   - Reusable data for sorting by different columns without re-scraping

## Advanced Usage

### Re-sorting Existing Data

To sort by a different column without re-running the scraper, edit `checker.py`:

```python
use_pickle_flag = True
column_to_sort_by = "followers"  # or "following", "ratio", etc.
```

Then run the script again.

## Troubleshooting

- **Login fails**: Check that 2FA is disabled and credentials are correct
- **VPN issues**: Disable your VPN before running
- **Docker Chrome crashes**: Increase `shm_size` in `docker-compose.yml`
- **Rate limiting**: Instagram may temporarily block if run too frequently

## Notes

- Remember to turn 2FA back on if wanted and remove env information after each session.
- This tool uses web scraping via Selenium, which can break if Instagram changes their UI.
- Results are saved locally and never shared.
- Be mindful of Instagram's rate limits and terms of service.
- This tool relies on a mix of English and Spanish Instagram terms and phrases. Future improvements may be made to expand on the languages able to be used.