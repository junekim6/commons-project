# Load in python libraries
import logging
import os
import sys
from datetime import datetime, timedelta

import boto3
import pytz

import config  # pylint: disable=unused-import
from connectors.postgres import PostgresConnector
from jobs.historical_scrape.sql import (
    INSERT_COMMENTS_STMT,
    INSERT_DOCKETS_STMT,
    INSERT_DOCUMENTS_STMT,
    INSERT_STATUS_STMT,
)
from jobs.historical_scrape.supporting_functions import (
    clean_string,
    get_comment_text,
    get_comments,
    get_dockets,
    get_documents,
    get_ids,
    structure_data,
)

BUCKET_NAME: str = "commons-docs"

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    # Set up DB connection
    pg_conn = PostgresConnector()

    # Set up AWS connection
    s3_client = boto3.client(
        service_name="s3",
        region_name=os.getenv("AWS_REGION"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    logging.info("Getting Earliest Scraped Date!")
    result = pg_conn.select("SELECT MIN(data_date) FROM status;")
    earliest_date = datetime.strptime(result["min"][0], "%Y-%m-%d")

    data_date = earliest_date - timedelta(days=1)
    data_date = data_date.strftime("%Y-%m-%d")

    logging.info(f"Starting Scraping for {data_date}...")

    # To keep better track of the scrapes, we add a timestamp for when the data is added to the database.
    ts = datetime.now().astimezone(pytz.timezone("EST"))
    timestamp = datetime.strftime(ts, "%Y-%m-%d %H:%M:%S")
    today = datetime.strftime(ts, "%Y-%m-%d")

    # STEP 1
    comment_ids = get_ids(data_date)
    if len(comment_ids) == 0:
        pg_conn.execute(
            """
            status (
                date, data_date, number_of_comments, number_of_dockets, scrape_timestamp, number_of_documents
            ) VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (data_date) DO NOTHING;
            """,
            (
                today,
                data_date,
                0,
                0,
                timestamp,
                0,
            ),
        )
        logging.info("No comments to scrape for this date.")

    logging.info("Completed Step 1: get ids")

    # STEP 2
    comments = get_comments(comment_ids, s3_client, BUCKET_NAME)
    logging.info("Completed Step 2: get comments")

    # STEP 3
    full_data = get_comment_text(comments)
    logging.info("Completed Step 3: get comment text")

    # STEP 4
    result = structure_data(full_data)
    logging.info("Completed Step 4: structure data")

    # STEP 5: GET INFORMATION ON THE DOCKETS
    dockets = get_dockets(result)
    logging.info("Completed Step 5: get dockets")

    # STEP 6: GET INFORMATION ON THE DOCUMENTS
    documents = get_documents(result)
    logging.info("Completed Step 6: get documents")

    # STEP 7: CREATE THE FULL TEXT AND CLEAN_TEXT COLUMNS:
    for item in result:
        # Create a new column that combines the comment and the extracted text from the pdf
        item["full_text"] = item["comment"] + " " + item["comment_pdf_extracted"]
    logging.info("Completed Step 7: create full text")

    # STEP 8: WRITE DATA TO DATABASE
    # STEP 8.1: WRITE INFORMATION ON THE COMMENTS TO THE DATABASE
    for item in result:
        pg_conn.execute(
            INSERT_COMMENTS_STMT,
            (
                clean_string(item["comment_id"]),
                clean_string(item["docket_id"]),
                clean_string(item["agency_id"]),
                clean_string(item["title"]),
                clean_string(item["comment"]),
                clean_string(item.get("comment_pdf_extracted")),
                clean_string(item.get("commenter_first_name")),
                clean_string(item.get("commenter_last_name")),
                clean_string(item.get("commenter_organization")),
                clean_string(item.get("commenter_address1")),
                clean_string(item.get("commenter_address2")),
                clean_string(item.get("commenter_zip")),
                clean_string(item.get("commenter_city")),
                clean_string(item.get("commenter_state_province_region")),
                clean_string(item.get("commenter_country")),
                clean_string(item.get("commenter_email")),
                clean_string(item.get("receive_date")),
                clean_string(item.get("posted_date")),
                clean_string(item.get("postmark_date")),
                item.get("duplicate_comments"),
                clean_string(item.get("attachment_read")),
                clean_string(item.get("attachment_url")),
                item.get("withdrawn"),
                clean_string(item.get("api_url")),
                clean_string(item.get("full_text")),
                item.get("document_id"),
            ),
        )

    # STEP 8.2: WRITE INFORMATION ON THE DOCKETS TO THE DATABASE
    # contrary to with the comments, we want to update the dockets if they already exist in the database
    for item in dockets:
        pg_conn.execute(
            INSERT_DOCKETS_STMT,
            (
                item["docket_id"],
                item["agency_id"],
                clean_string(item["title"]),
                clean_string(item["docket_type"]),
                item["keywords"],
                clean_string(item["abstract"]),
                item["category"],
                item["modify_date"],
                item["effective_date"],
                clean_string(item["organization"]),
                clean_string(item["program"]),
                item["rin"],
                item["object_id"],
                item["docket_url"],
            ),
        )

    # STEP 8.3: WRITE INFORMATION ON THE DOCUMENTS TO THE DATABASE
    for item in documents:
        pg_conn.execute(
            INSERT_DOCUMENTS_STMT,
            (
                item["document_id"],
                item["original_document_id"],
                item["document_type"],
                item["subtype"],
                item["docket_id"],
                item["agency_id"],
                item["title"],
                item["abstract"],
                item["topics"],
                item["subject"],
                item["comment_start_date"],
                item["comment_end_date"],
                item["effective_date"],
                item["implementation_date"],
                item["modified_date"],
                item["open_for_comment"],
                item["allow_late_comments"],
                item["object_id"],
                item["withdrawn"],
                item["document_url"],
                item["attachments"],
            ),
        )
    logging.info("Completed Step 8: Wrote to Database")

    # STEP 9: WRITE STATUS TO FILE
    # this will keep track of the number of comments and dockets scraped each day

    # the try connecting to the database and add today's row of data.
    pg_conn.execute(
        INSERT_STATUS_STMT,
        (
            today,
            data_date,
            len(result),
            len(dockets),
            timestamp,
            len(documents),
        ),
    )

    print("Completed Step 9: Logged to Status")
