import sqlite3

# Create/connect database file
conn = sqlite3.connect("MyDataBase.db")

cursor = conn.cursor()

# Create Partner table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Partner (
    PartnerID INTEGER PRIMARY KEY AUTOINCREMENT,
    PartnerName NVARCHAR(100),
    AccountName NVARCHAR(100),
    EmailAddress NVARCHAR(100),
    Password NVARCHAR(50),
    Tel NVARCHAR(50),
    FromDate DATE
)
""")

conn.commit()

print("Database and table created successfully.")

conn.close()
