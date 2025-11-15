import psycopg2

conn = psycopg2.connect(
    host="127.0.0.1",
    database="frauddb",
    user="fraud_user",
    password="ayush123",
    port="5432"
)

print("✅ Connected to PostgreSQL")
conn.close()
