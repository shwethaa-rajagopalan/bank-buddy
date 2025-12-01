
import pandas as pd
import sqlite3
import os

from pypdf import PdfReader
from google.adk.agents.callback_context import CallbackContext
from dotenv import load_dotenv


load_dotenv()

DB_FILE_NAME = 'customer_data.db'


def getLoanMetadata():
    """
    Extracts and returns text from the loan information PDF metadata file.
    Returns:
        Extracted text from the PDF file.
    """
    reader = PdfReader("loan_information_metadata.pdf")
    page = reader.pages[0]
    return page.extract_text()


def getCustomerData(customer_id):
    """
    Fetches customer demographic data based on the ID.
    Args:
        customer_id: The unique identifier for the customer.
    Returns: 
        A dictionary containing customer demographic data.
    """
    conn_read = sqlite3.connect(DB_FILE_NAME)
    query = f"SELECT * FROM customer WHERE CUSTOMER_ID = {customer_id};"
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

def getLoanApplication(customer_id: int, application_id: int ) -> pd.DataFrame:
    
    conn_read = sqlite3.connect(DB_FILE_NAME)
    query = f"SELECT * FROM loan_applications WHERE APPLICATION_ID = {application_id} AND CUSTOMER_ID = {customer_id};"
    result_df = pd.read_sql_query(query, conn_read)
    conn_read.close()
    return result_df.to_dict()

def getAllLoanApplications(customer_id: int) -> pd.DataFrame:
    
    conn_read = sqlite3.connect(DB_FILE_NAME)
    query = f"SELECT * FROM loan_applications WHERE CUSTOMER_ID = {customer_id};"
    result_df = pd.read_sql_query(query, conn_read)
    conn_read.close()
    return result_df.to_dict()

def saveLoanApplication(application_data: dict) -> int:
    """
    Saves a new loan application to the database.
    Args:
        application_data: A dictionary containing application details.  {customer_id, loan_type, loan_amount, identification}
    Returns:
        The saved application's ID, or -1 if failed.
    """
    try:
        conn = sqlite3.connect(DB_FILE_NAME)
        cursor = conn.cursor()

        columns = ', '.join(application_data.keys())
        placeholders = ', '.join(['?'] * len(application_data))
        values = tuple(application_data.values())

        insert_query = f"INSERT INTO loan_applications ({columns}) VALUES ({placeholders})"
        cursor.execute(insert_query, values)
        application_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return application_id
    except Exception as e:
        return -1
