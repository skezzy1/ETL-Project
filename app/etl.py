# ETL Process
import os
import pandas as pd
from sqlalchemy import create_engine, text
from faker import Faker
from dotenv import load_dotenv
load_dotenv()

def generate_csv(file_path, num_records=1000):
    fake = Faker()
    data = []
    for count in range(num_records):
        user_id = count + 1
        name = fake.name()
        email = fake.email()
        signup_date = fake.date_time_between(start_date="-1y", end_date="now").strftime("%Y-%m-%d %H:%M:%S")
        data.append([user_id, name, email, signup_date])

    df = pd.DataFrame(data, columns=["user_id", "name", "email", "signup_date"])
    df.to_csv(file_path, index=False)
    print(f"CSV file generated at {file_path}")

def transform_data(file_path):
    df = pd.read_csv(file_path)
    df["signup_date"] = pd.to_datetime(df["signup_date"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    email_pattern = r"^[^@]+@[^@]+\.[^@]+$"
    df = df[df["email"].str.match(email_pattern)]
    df["domain"] = df["email"].str.split("@").str[1]
    return df

def load_data_to_postgresql(df, db_url, sql_file=os.getenv('SQL_FILE_PATH')):
    engine = create_engine(db_url)
    with open(sql_file, "r") as file:
        create_table_query = file.read()

    with engine.connect() as connection:
        connection.execute(text(create_table_query))
        print("Table created successfully!")

    df.to_sql("users", engine, if_exists="replace", index=False)
    print("Data loaded successfully!")

if __name__ == "__main__":
    csv_file_path = os.getenv('csv_name')
    db_url = os.getenv('db_url')

    generate_csv(csv_file_path)
    transformed_data = transform_data(csv_file_path)
    load_data_to_postgresql(transformed_data, db_url)
