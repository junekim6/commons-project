#!/bin/bash
LOGFILE="/root/historical_scrape.log"
echo "running historical scraping script at $(date)">>$LOGFILE
/usr/local/bin/python3 /root/jobs/historical_scrape/run.py>>$LOGFILE 2>&1
if [ $? -eq 0 ]; then
        echo "historical scraping script executed successfully">>$LOGFILE
else
        echo "historical scraping script failed">>$LOGFILE
        exit 1
fi
echo "historical scraping script completed at $(date)">>$LOGFILE