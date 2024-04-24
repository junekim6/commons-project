# Collect data from regulations.gov

This folder contains the code to collect data from regulations.gov API. 

## 1. Content of the directory

This directory is split into three main folders: `daily_scrape`, `historical_scrape`, and `notebooks`.

- `daily_scrape`: Contains the code to collect data from regulations.gov on a daily basis. These scripts are run on a daily basis to collect the latest data.
- `historical_scrape`: Contains the code to collect historical data from regulations.gov. These scripts are run continuously to collect data further and further back in time. 
- `notebooks`: Contains the notebooks

## 2. Setup

To run the code, you need to have a multiple valid API kes from regulations.gov. You can request an API key [here](https://open.gsa.gov/api/regulationsgov/).

Because the API has a limit on the number of requests you can make per day, we have multiple API keys that we use to collect data. You can add your own API keys to the `.env` file in the root directory of the repository.

```bash
REGGOV_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Daily scrape
REGGOV_API_KEY_L1 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
REGGOV_API_KEY_L2 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
REGGOV_API_KEY_L3 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
REGGOV_API_KEY_L4 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
REGGOV_API_KEY_L5 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
REGGOV_API_KEY_J1 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
REGGOV_API_KEY_J2 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
REGGOV_API_KEY_J3 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
REGGOV_API_KEY_J4 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
REGGOV_API_KEY_J5 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
REGGOV_API_KEY_M1 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
REGGOV_API_KEY_M2 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
REGGOV_API_KEY_M3 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
REGGOV_API_KEY_M4 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
REGGOV_API_KEY_M5 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
REGGOV_API_KEY_N1 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Historical scrape
REGGOV_API_KEY_L00 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
REGGOV_API_KEY_L01 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
REGGOV_API_KEY_L02 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
REGGOV_API_KEY_L03 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
REGGOV_API_KEY_L04 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
REGGOV_API_KEY_L05 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
REGGOV_API_KEY_J06 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
REGGOV_API_KEY_J07 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
REGGOV_API_KEY_J08 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
REGGOV_API_KEY_J09 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
REGGOV_API_KEY_J10 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
REGGOV_API_KEY_H11 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
REGGOV_API_KEY_M12 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
REGGOV_API_KEY_M13 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
REGGOV_API_KEY_M14 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
REGGOV_API_KEY_M15 = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```
