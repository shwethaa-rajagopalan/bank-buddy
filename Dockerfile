    # Example Dockerfile for a Python application
    FROM python:3.9-slim-buster

    WORKDIR /app

    COPY requirements.txt .
    RUN pip install -r requirements.txt

    COPY . . # This will copy your application code and the db file

    CMD ["streamlit run", "app.py"]