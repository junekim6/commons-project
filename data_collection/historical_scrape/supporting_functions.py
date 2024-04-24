import html
import json
import math
import os
import subprocess
import time
from datetime import datetime, timedelta
from glob import glob
from io import BytesIO
import psycopg2

import boto3
import botocore
import pdfplumber
import PyPDF2
import requests
from flatten_json import flatten
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTChar, LTTextContainer

import config  # pylint: disable=unused-import


def get_ids(data_date):
    api_key = os.getenv("REGGOV_API_KEY_L00")
    # Figure out how many times we have to call the API to get all the comment ids
    url = f"https://api.regulations.gov/v4/comments?filter[postedDate]={data_date}&page[size]=5&page[number]=1&sort=lastModifiedDate&api_key={api_key}"
    response = requests.get(url)
    result = response.json()
    # There are maximum 4750 comments per call, so we divide the total number of comments by 4750,
    # round up to get the number of calls we need to make, and add 1 just to be safe
    rounds = math.ceil(result["meta"]["totalElements"] / 4750) + 1

    # Handle the case where there are no comments
    if result["meta"]["totalElements"] == 0:
        print("No comments found for this date")
        return []
    else:
        # Create lists to store the comment ids and the API responses
        api_response = []
        comment_metadata = []

        # Call the API the first time and get the comment ids
        for page in range(1, 20):
            url = f"https://api.regulations.gov/v4/comments?filter[postedDate]={data_date}&page[size]=250&page[number]={page}&sort=lastModifiedDate&api_key={api_key}"
            response = requests.get(url)
            result = response.json()

            if result["data"] is None or not result["data"]:
                print("Got no comments from the API call")
                continue
            else:
                api_response.append(result)
                for comment in result["data"]:
                    comment_metadata.append(comment["id"])

        # Reset the time variables to get the last modified date of the last comment in the first API call. Thus we can use this date to get the next batch of comments
        greater_than = api_response[-1]["data"][-1]["attributes"]["lastModifiedDate"][
            :-1
        ]
        greater_than = greater_than.replace("T", " ")
        date_str = greater_than
        date_format = "%Y-%m-%d %H:%M:%S"

        date_obj = datetime.strptime(date_str, date_format)
        greater_than = date_obj - timedelta(
            hours=5
        )  ## Correct the time variable to account for difference the time zone in the API response and the API call

        for _ in range(0, rounds):
            for page in range(1, 20):
                url = f"https://api.regulations.gov/v4/comments?filter[postedDate]={data_date}&filter[lastModifiedDate][ge]={greater_than}&page[size]=250&page[number]={page}&sort=lastModifiedDate&api_key={api_key}"
                response = requests.get(url)
                result = response.json()

                # Save the API response to a list if there are comments in the response
                if result["data"] is None or not result["data"]:
                    continue
                else:
                    api_response.append(result)
                    for comment in result["data"]:
                        comment_metadata.append(
                            comment["id"]
                        )  ## Save the comment ids to a list

            try:
                greater_than = api_response[-1]["data"][-1]["attributes"][
                    "lastModifiedDate"
                ][:-1]
                greater_than = greater_than.replace("T", " ")
                date_obj = datetime.strptime(greater_than, date_format)
                greater_than = date_obj - timedelta(hours=5)
                print("Fetched data")
            except:
                print("Got no comments from the API call")

        ## Remove duplicate elements in the list of comment IDS
        comment_ids = []
        [comment_ids.append(x) for x in comment_metadata if x not in comment_ids]

        # Make sure we got all the comments
        scrape_count = len(comment_ids)
        api_count = api_response[0]["meta"]["totalElements"]

        if scrape_count == api_count:
            print(f"We got all the {scrape_count} comments")
        else:
            # raise
            print(
                f"We didn't get all the comments. We got {scrape_count} comments, but the API says there are {api_count} comments"
            )
            # Here we want to send emails to the team to alert them that we didn't get all the comments

        return comment_ids


def check_file_exists(bucket, key):
    try:
        boto3.resource("s3").Object(bucket, key).load()
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        else:
            raise
    else:
        return True


def get_comments(ids, s3_client, bucket_name):

    # Load in the API keys
    keys = [
        "L01",
        "L02",
        "L03",
        "L04",
        "L05",
        "J06",
        "J07",
        "J08",
        "J09",
        "J10",
        "H11",
        "M12",
        "M13",
        "M14",
        "M15",
    ]

    # Figure out how many rounds it will take to scrape all the comments
    rounds = len(ids) / 500
    rounds = math.ceil(rounds)

    comment_details = []

    num = 0

    for _ in range(rounds):
        for key in keys:
            api_key = os.getenv(f"REGGOV_API_KEY_{key}")
            for _ in range(50):
                # In the last round, there might not be 50 comments left, so we break when we run out of comments to scrape
                try:
                    comment_id = ids[num]
                    docket_id = comment_id[:-5]
                    url = f"https://api.regulations.gov/v4/comments/{comment_id}?include=attachments&api_key={api_key}"
                    response = requests.get(url)
                    result = response.json()

                    # And append the data to the today_comments list so we can access the download links and store the pdfs
                    comment_details.append(result)

                    # Try to write the data to the S3 bucket to store a copy of the data so we don't have to scrape it again
                    try:
                        # create a directory for each regulation, save each comment as is own json named the comment ID
                        filename = f"data/raw/{docket_id}/{comment_id}.json"

                        comment_text_buffer = BytesIO()
                        comment_text_buffer.write(
                            json.dumps(json.dumps(result)).encode()
                        )

                        s3_client.upload_fileobj(
                            comment_text_buffer, "commons-docs", filename
                        )
                        s3_client.get_waiter("object_exists").wait(
                            Bucket=bucket_name, Key=filename
                        )
                    except Exception as e:
                        print(f"Error uploading to S3: {e}")

                except Exception as e:
                    break

                num = num + 1
                time.sleep(0.4)
                print(num)

    return comment_details


def get_comment_text(comments):

    # Function to extract text
    def text_extraction(element):
        # Extracting the text from the in-line text element
        line_text = element.get_text()

        # Find the formats of the text
        # Initialize the list with all the formats that appeared in the line of text
        line_formats = []
        for text_line in element:
            if isinstance(text_line, LTTextContainer):
                # Iterating through each character in the line of text
                for character in text_line:
                    if isinstance(character, LTChar):
                        # Append the font name of the character
                        line_formats.append(character.fontname)
                        # Append the font size of the character
                        line_formats.append(character.size)
        # Find the unique font sizes and names in the line
        format_per_line = list(set(line_formats))

        # Return a tuple with the text in each line along with its format
        return (line_text, format_per_line)

    # Loop through the comments and extract the text from the attached pdfs
    for comment in comments:
        id = comment["data"]["id"]
        try:
            num = 1
            attachment_url = ""
            for files in comment["included"]:
                try:
                    result = ""
                    # Loop through the files and get the pdfs
                    for file in files["attributes"]["fileFormats"]:
                        url = file["fileUrl"]
                        response = requests.get(url)
                        attachment_url = attachment_url + str(url) + " "

                        # pdf_path = f"{id}_attachment_{num}.pdf"
                        pdf_path = os.path.abspath(f"{id}_attachment_{num}.pdf")
                        doc_path = os.path.abspath("temp.docx")
                        soffice_path = (
                            "/Applications/LibreOffice.app/Contents/MacOS/soffice"
                        )

                        if url.endswith(".docx"):
                            with open(doc_path, "wb") as f:
                                f.write(response.content)
                            subprocess.run(
                                [
                                    soffice_path,
                                    "--convert-to",
                                    "pdf",
                                    "--headless",
                                    doc_path,
                                ]
                            )
                            os.rename("temp.pdf", pdf_path)
                            os.remove("temp.docx")

                        else:
                            with open(pdf_path, "wb") as f:
                                f.write(response.content)

                        # ADD PDF SCRAPER HERE
                        pdfFileObj = open(pdf_path, "rb")
                        pdfReaded = PyPDF2.PdfReader(pdfFileObj)

                        # Get the number of pages in the PDF file
                        num_pages = len(pdfReaded.pages)

                        # Create the dictionary to extract text from each image
                        text_per_page = {}

                        # We extract the pages from the PDF
                        for pagenum, page in enumerate(extract_pages(pdf_path)):
                            if pagenum > 2:
                                break
                            # Initialize the variables needed for the text extraction from the page
                            pageObj = pdfReaded.pages[pagenum]
                            page_text = []
                            line_format = []
                            page_content = []

                            # Open the pdf file
                            pdf = pdfplumber.open(pdf_path)

                            # Find the examined page
                            page_tables = pdf.pages[pagenum]

                            # Find all the elements
                            page_elements = [
                                (element.y1, element) for element in page._objs
                            ]

                            # Sort all the elements as they appear in the page
                            page_elements.sort(key=lambda a: a[0], reverse=True)

                            # Find the elements that composed a page
                            for i, component in enumerate(page_elements):
                                # Extract the position of the top side of the element in the PDF
                                pos = component[0]

                                # Extract the element of the page layout
                                element = component[1]

                                # Check if the element is a text element
                                if isinstance(element, LTTextContainer):
                                    # Use the function to extract the text and format for each text element
                                    (line_text, format_per_line) = text_extraction(
                                        element
                                    )

                                    # Append the text of each line to the page text
                                    page_text.append(line_text)

                                    # Append the format for each line containing text
                                    line_format.append(format_per_line)
                                    page_content.append(line_text)
                                # Create the key of the dictionary
                                dctkey = "Page_" + str(pagenum)

                                # Add the list of list as the value of the page key
                                text_per_page[dctkey] = [
                                    page_text,
                                    line_format,
                                    page_content,
                                ]

                            # Display the content of the page
                            page_result = "".join(
                                text_per_page["Page_" + str(pagenum)][0]
                            )
                            result = result + "\n \n" + page_result

                            # Close the pdf file
                            pdfFileObj.close()

                            # Remove pdf files that are not needed anymore
                        try:
                            os.remove(pdf_path)
                            files = glob(f"*.pdf")
                            for f in files:
                                os.remove(f)
                        except:
                            print("No files to remove")

                        num = num + 1

                    # Save the extracted text to the json file from the api call
                    comment["data"]["attributes"]["pdf_extracted_text"] = result
                    comment["data"]["attributes"][
                        "attachment_read"
                    ] = "attachment extracted"
                    comment["data"]["attributes"]["attachments_url"] = attachment_url

                except Exception as inst:
                    print(type(inst))  # the exception type
                    x = inst.args  # unpack args
                    print("x =", x)
                    comment["data"]["attributes"][
                        "attachment_read"
                    ] = "attachment failed"
                    comment["data"]["attributes"]["attachments_url"] = attachment_url
                except:
                    comment["data"]["attributes"][
                        "attachment_read"
                    ] = "attachment failed"
                    comment["data"]["attributes"]["attachments_url"] = attachment_url
                    raise
        except KeyError:
            comment["data"]["attributes"]["attachment_read"] = "no attachment"
            comment["data"]["attributes"]["attachments_url"] = None
    return comments


def structure_data(data):
    keys_to_include = [
        "data_id",
        "data_attributes_commentOnDocumentId",
        "data_attributes_docketId",
        "data_attributes_agencyId",
        "data_attributes_title",
        "data_attributes_comment",
        "data_attributes_pdf_extracted_text",
        "data_attributes_firstName",
        "data_attributes_lastName",
        "data_attributes_organization",
        "data_attributes_address1",
        "data_attributes_address2",
        "data_attributes_zip",
        "data_attributes_city",
        "data_attributes_country",
        "data_attributes_stateProvinceRegion",
        "data_attributes_email",
        "data_attributes_receiveDate",
        "data_attributes_postedDate",
        "data_attributes_postmarkDate",
        "data_links_self",
        "data_attributes_attachments_url",
        "data_attributes_attachment_read",
        "data_attributes_duplicateComments",
        "data_attributes_withdrawn",
    ]
    final_data = []
    for comment in data:
        # Flatten the nested dictionaries
        flat_comment = flatten(comment)
        result_dict = {}
        for key, value in flat_comment.items():
            if key in keys_to_include:
                if isinstance(value, dict):
                    # Recursively process nested dictionaries
                    result_dict[key] = structure_data(value, keys_to_include)
                else:
                    # Include non-dictionary values
                    result_dict[key] = value if value is not None else ""
        final_data.append(result_dict)

    # Rename the keys to match the database
    key_mapping = {
        "data_id": "comment_id",
        "data_attributes_commentOnDocumentId": "document_id",
        "data_attributes_docketId": "docket_id",
        "data_attributes_agencyId": "agency_id",
        "data_attributes_title": "title",
        "data_attributes_comment": "comment",
        "data_attributes_pdf_extracted_text": "comment_pdf_extracted",
        "data_attributes_firstName": "commenter_first_name",
        "data_attributes_lastName": "commenter_last_name",
        "data_attributes_organization": "commenter_organization",
        "data_attributes_address1": "commenter_address1",
        "data_attributes_address2": "commenter_address2",
        "data_attributes_zip": "commenter_zip",
        "data_attributes_city": "commenter_city",
        "data_attributes_stateProvinceRegion": "commenter_state_province_region",
        "data_attributes_country": "commenter_country",
        "data_attributes_email": "commenter_email",
        "data_attributes_receiveDate": "receive_date",
        "data_attributes_postedDate": "posted_date",
        "data_attributes_postmarkDate": "postmark_date",
        "data_attributes_duplicateComments": "duplicate_comments",
        "data_attributes_attachment_read": "attachment_read",
        "data_attributes_attachments_url": "attachment_url",
        "data_attributes_withdrawn": "withdrawn",
        "data_links_self": "api_url",
    }

    # Rename the keys so they match the database
    for i in final_data:
        for old_key, new_key in key_mapping.items():
            i[new_key] = i.pop(old_key, "")
    return final_data


def get_dockets(result):
    # Load in the API key
    extra_api_key = os.getenv("REGGOV_API_KEY_N1")

    docket_ids = []
    # Loop through the scraped comments to get the docket ids
    for id in result:
        docket_ids.append(id["docket_id"])

    # Remove duplicate elements in the list of docket IDS
    unique_docket_ids = []
    [unique_docket_ids.append(x) for x in docket_ids if x not in unique_docket_ids]

    # Get the metadata for each docket
    docket_metadata = []
    for docket_id in unique_docket_ids:
        url = f"https://api.regulations.gov/v4/dockets/{docket_id}?api_key={extra_api_key}"
        response = requests.get(url)
        result = response.json()
        docket_metadata.append(result)
        time.sleep(1.5)

    # Only keep some of the keys
    cleaned_docket_metadata = []
    for docket in docket_metadata:
        docket = docket["data"]
        docket = {
            "docket_id": docket["id"],
            "agency_id": docket["attributes"]["agencyId"],
            "title": docket["attributes"]["title"],
            "docket_type": docket["attributes"]["docketType"],
            "keywords": docket["attributes"]["keywords"],
            "abstract": docket["attributes"]["dkAbstract"],
            "category": docket["attributes"]["category"],
            "modify_date": docket["attributes"]["modifyDate"],
            "effective_date": docket["attributes"]["effectiveDate"],
            "organization": docket["attributes"]["organization"],
            "program": docket["attributes"]["program"],
            "rin": docket["attributes"]["rin"],
            "object_id": docket["attributes"]["objectId"],
            "docket_url": docket["links"]["self"],
        }

        cleaned_docket_metadata.append(docket)

    return cleaned_docket_metadata


def get_documents(result):
    # Load in the API key
    extra_api_key = os.getenv("REGGOV_API_KEY")

    document_ids = []
    # Loop through the scraped comments to get the docket ids
    for id in result:
        document_ids.append(id["document_id"])

    # Remove duplicate elements in the list of docket IDS
    unique_document_ids = []
    [
        unique_document_ids.append(x)
        for x in document_ids
        if x not in unique_document_ids
    ]

    # Get the metadata for each docket
    document_metadata = []
    for document_id in unique_document_ids:
        url = f"https://api.regulations.gov/v4/documents/{document_id}?include=attachments&api_key={extra_api_key}"
        response = requests.get(url)
        result = response.json()
        document_metadata.append(result)
        time.sleep(1.5)

    # Only keep some of the keys
    cleaned_document_metadata = []
    for document in document_metadata:
        try:
            document = document["data"]
            document = {
                "document_id": document["id"],
                "original_document_id": document["attributes"]["originalDocumentId"],
                "document_type": document["attributes"]["documentType"],
                "subtype": document["attributes"]["subtype"],
                "docket_id": document["attributes"]["docketId"],
                "agency_id": document["attributes"]["agencyId"],
                "title": document["attributes"]["title"],
                "abstract": document["attributes"]["docAbstract"],
                "topics": document["attributes"]["topics"],
                "subject": document["attributes"]["subject"],
                "comment_start_date": document["attributes"]["commentStartDate"],
                "comment_end_date": document["attributes"]["commentEndDate"],
                "effective_date": document["attributes"]["effectiveDate"],
                "implementation_date": document["attributes"]["implementationDate"],
                "modified_date": document["attributes"]["modifyDate"],
                "open_for_comment": document["attributes"]["openForComment"],
                "allow_late_comments": document["attributes"]["allowLateComments"],
                "object_id": document["attributes"]["objectId"],
                "withdrawn": document["attributes"]["withdrawn"],
                "document_url": document["links"]["self"],
                "attachments": [
                    file["fileUrl"]
                    for file in document["attributes"].get("fileFormats", [])
                    if "fileUrl" in file
                ]
                or None,
            }
            cleaned_document_metadata.append(document)
        except:
            print(f"Error in the document metadata for {document_id}")

    return cleaned_document_metadata


def clean_string(input_string):
    """Remove NULL characters from a string."""
    if input_string is not None:
        # clean up html - list all the html characters that need to be changed and what they should be changed to
        html_chars = {
            "&amp;": "&",
            "&gt;": ">",
            "&lt;": "<",
            "&nbsp;": " ",
            "&quot;": '"',
            "&#39;": "'",
            "&#34;": '"',
            "nan": "",
            "<br>": " ",
            "<br/>": " ",
            "\n": " ",
            "\x00": "",
        }
        for key, value in html_chars.items():
            input_string = input_string.replace(key, value)

        input_string = input_string.replace("See Attached", "")
        input_string = input_string.replace("See attached file(s)", "")
        input_string = html.unescape(input_string)

    return input_string
