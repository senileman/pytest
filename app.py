import sqlite3
from flask import Flask, render_template, g

app = Flask(__name__)


DATABASE = "MyDataBase.db"


def seed_data():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Partner (
            PartnerID    INTEGER PRIMARY KEY AUTOINCREMENT,
            PartnerName  NVARCHAR(100),
            AccountName  NVARCHAR(100),
            EmailAddress NVARCHAR(100),
            Password     NVARCHAR(50),
            Tel          NVARCHAR(50),
            FromDate     DATE
        )
    """)

    count = cursor.execute("SELECT COUNT(*) FROM Partner").fetchone()[0]
    if count == 0:
        sample_data = [
            ("abc",         "abc_corp",      "contact@abc.vn",      "abc@2024",   "0901234567", "2024-01-15"),
            ("XYZ",             "xyz_group",     "info@xyz.com.vn",     "xyz#pass1",  "0912345678", "2024-03-20"),
            ("phuquy",     "phuquy_dn",     "phuquy@email.vn",     "pq!secure2", "0923456789", "2024-05-10"),
            ("minhtan", "minhtan_cp",    "minhtan@business.vn", "mt@2024!",   "0934567890", "2024-07-01"),
            ("27_HoangCongThanh_01",     "hoancongthanh", "thanh27@student.vn",  "hct@2024",   "0945678901", "2024-09-05"),
        ]
        cursor.executemany("""
            INSERT INTO Partner (PartnerName, AccountName, EmailAddress, Password, Tel, FromDate)
            VALUES (?, ?, ?, ?, ?, ?)
        """, sample_data)
        print(f" Seed: đã chèn {len(sample_data)} bản ghi vào Partner")
    else:
        print(f"  Seed: bảng đã có {count} bản ghi")

    conn.commit()
    conn.close()


seed_data()



def get_db():

    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error=None):

    db = g.pop("db", None)
    if db is not None:
        db.close()



def get_partner_27_HoangCongThanh_01():

    db = get_db()
    return db.execute(
        "SELECT * FROM Partner WHERE PartnerName = ?",
        ("27_HoangCongThanh_01",)
    ).fetchone()


def get_all_partners():

    db = get_db()
    return db.execute("SELECT * FROM Partner ORDER BY PartnerID").fetchall()



@app.route("/")
def index():
    partner  = get_partner_27_HoangCongThanh_01()
    partners = get_all_partners()
    return render_template("index.html", partner=partner, partners=partners)


if __name__ == "__main__":
    app.run(debug=True, port=5000)