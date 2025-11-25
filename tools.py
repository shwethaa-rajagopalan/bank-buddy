
import pandas as pd
import sqlite3
import os

from pypdf import PdfReader
from google.adk.agents.callback_context import CallbackContext
from dotenv import load_dotenv


load_dotenv()

DB_FILE_NAME = os.getenv("DB_FILE_NAME")
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH")
CUSTOMER_TABLE = os.getenv("CUSTOMER_TABLE")


def getLoanMetadata():
    """
    Extracts and returns text from the loan information PDF metadata file.
    Returns:
        Extracted text from the PDF file.
    """
    reader = PdfReader("loan_information_metadata.pdf")
    page = reader.pages[0]
    return page.extract_text()

def load_csv_to_sqlite_file(callback_context: CallbackContext):
    """
    Loads data from a CSV file into a persistent SQLite database file.
    Returns the database connection object.
    """
       
    if not (CSV_FILE_PATH):
        return None

    try:
        df = pd.read_csv(CSV_FILE_PATH)
    except Exception as e:
        return None

    try:
        conn = sqlite3.connect(DB_FILE_NAME)
    except Exception as e:
        return None
    
    df.to_sql(CUSTOMER_TABLE, conn, if_exists='replace', index=False)
    
    conn.close()

def getCustomerData(customer_id):
    """
    Fetches customer demographic data based on the ID.
    Args:
        customer_id: The unique identifier for the customer.
    Returns: 
        A dictionary containing customer demographic data.
    """
    conn_read = sqlite3.connect(DB_FILE_NAME)
    query = f"SELECT * FROM {CUSTOMER_TABLE} WHERE CUSTOMER_ID = {customer_id};"
    result_df = pd.read_sql_query(query, conn_read)
    conn_read.close()
    return result_df.iloc[0].to_dict()

def setCustomerContext(customer_id: str) -> dict:
    """
    Fetches customer demographic data based on the ID and updates the agent's session state.
    Args:
        customer_id: The unique identifier for the customer.
    Returns:
        A confirmation message indicating success or failure.
    """
    
    return getCustomerData(customer_id)

