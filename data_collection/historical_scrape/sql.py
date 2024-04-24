INSERT_COMMENTS_STMT = """
INSERT INTO comments (
    comment_id,
    docket_id,
    agency_id,
    title,
    comment, 
    comment_pdf_extracted,
    commenter_first_name,
    commenter_last_name, 
    commenter_organization,
    commenter_address1,
    commenter_address2, 
    commenter_zip,
    commenter_city,
    commenter_state_province_region, 
    commenter_country,
    commenter_email,
    receive_date,
    posted_date, 
    postmark_date,
    duplicate_comments,
    attachment_read,
    attachment_url, 
    withdrawn,
    api_url,
    full_text,
    document_id
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (comment_id) DO NOTHING;
"""

INSERT_DOCKETS_STMT = """
INSERT INTO dockets (
    docket_id,
    agency_id,
    title,
    docket_type,
    keywords,
    abstract, 
    category,
    modify_date,
    effective_date,
    organization,
    program, 
    rin,
    object_id,
    docket_url
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (docket_id) DO UPDATE SET
    docket_id = EXCLUDED.docket_id,
    agency_id = EXCLUDED.agency_id,
    title = EXCLUDED.title,
    docket_type = EXCLUDED.docket_type,
    keywords = EXCLUDED.keywords,
    abstract = EXCLUDED.abstract,
    category = EXCLUDED.category,
    modify_date = EXCLUDED.modify_date,
    effective_date = EXCLUDED.effective_date,
    organization = EXCLUDED.organization,
    program = EXCLUDED.program,
    rin = EXCLUDED.rin,
    object_id = EXCLUDED.object_id,
    docket_url = EXCLUDED.docket_url;
"""

INSERT_DOCUMENTS_STMT = """
INSERT INTO documents (
    document_id,
    original_document_id,
    document_type,
    subtype,
    docket_id,
    agency_id,
    title,
    abstract,
    topics,
    subject,
    comment_start_date,
    comment_end_date,
    effective_date,
    implementation_date,
    modified_date,
    open_for_comment,
    allow_late_comment,
    object_id,
    withdrawn,
    document_url,
    attachments
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (document_id) DO UPDATE SET
    document_id = EXCLUDED.document_id,
    original_document_id = EXCLUDED.original_document_id,
    document_type = EXCLUDED.document_type,
    subtype = EXCLUDED.subtype,
    docket_id = EXCLUDED.docket_id,
    agency_id = EXCLUDED.agency_id,
    title = EXCLUDED.title,
    abstract = EXCLUDED.abstract,
    topics = EXCLUDED.topics,
    subject = EXCLUDED.subject,
    comment_start_date = EXCLUDED.comment_start_date,
    comment_end_date = EXCLUDED.comment_end_date,
    effective_date = EXCLUDED.effective_date,
    implementation_date = EXCLUDED.implementation_date,
    modified_date = EXCLUDED.modified_date,
    open_for_comment = EXCLUDED.open_for_comment,
    allow_late_comment = EXCLUDED.allow_late_comment,
    object_id = EXCLUDED.object_id,
    withdrawn = EXCLUDED.withdrawn,
    document_url = EXCLUDED.document_url,
    attachments = EXCLUDED.attachments;
"""

INSERT_STATUS_STMT = """
INSERT INTO status (
    date,
    data_date,
    number_of_comments,
    number_of_dockets,
    scrape_timestamp,
    number_of_documents
) VALUES (%s, %s, %s, %s, %s, %s)
ON CONFLICT (data_date) DO NOTHING;
"""
