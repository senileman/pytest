import sqlite3
from flask import Flask, render_template, g, request

app = Flask(__name__)

DATABASE = "MyDataBase.db"


# ============================================================
# SEED DỮ LIỆU: Bảng Partner + Bảng DonHang
# ============================================================

def seed_data():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # --- Tạo bảng Partner nếu chưa tồn tại ---
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

    # --- Tạo bảng DonHang nếu chưa tồn tại ---
    # Mỗi đơn hàng thuộc về một Partner (quan hệ 1-nhiều qua PartnerID)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS DonHang (
            DonHangID   INTEGER PRIMARY KEY AUTOINCREMENT,
            PartnerID   INTEGER NOT NULL,
            TenSanPham  NVARCHAR(100),
            SoLuong     INTEGER,
            DonGia      REAL,
            NgayDat     DATE,
            FOREIGN KEY (PartnerID) REFERENCES Partner(PartnerID)
        )
    """)

    # --- Seed bảng Partner ---
    count_partner = cursor.execute("SELECT COUNT(*) FROM Partner").fetchone()[0]
    if count_partner == 0:
        sample_partners = [
            ("abc",                  "abc_corp",      "contact@abc.vn",      "abc@2024",   "0901234567", "2024-01-15"),
            ("XYZ",                  "xyz_group",     "info@xyz.com.vn",     "xyz#pass1",  "0912345678", "2024-03-20"),
            ("phuquy",               "phuquy_dn",     "phuquy@email.vn",     "pq!secure2", "0923456789", "2024-05-10"),
            ("minhtan",              "minhtan_cp",    "minhtan@business.vn", "mt@2024!",   "0934567890", "2024-07-01"),
            ("27_HoangCongThanh_01", "hoancongthanh", "thanh27@student.vn",  "hct@2024",   "0945678901", "2024-09-05"),
        ]
        cursor.executemany("""
            INSERT INTO Partner (PartnerName, AccountName, EmailAddress, Password, Tel, FromDate)
            VALUES (?, ?, ?, ?, ?, ?)
        """, sample_partners)
        print(f"  Seed: đã chèn {len(sample_partners)} bản ghi vào Partner")
    else:
        print(f"  Seed: bảng Partner đã có {count_partner} bản ghi")

    # --- Seed bảng DonHang ---
    count_donhang = cursor.execute("SELECT COUNT(*) FROM DonHang").fetchone()[0]
    if count_donhang == 0:
        # Lấy PartnerID thực tế từ DB để đảm bảo FK hợp lệ
        ids = {row[0]: row[1] for row in cursor.execute("SELECT PartnerName, PartnerID FROM Partner").fetchall()}

        sample_donhang = [
            (ids.get("abc"),                  "Bàn phím cơ",    2, 850000,  "2024-02-01"),
            (ids.get("abc"),                  "Chuột không dây", 5, 320000,  "2024-02-15"),
            (ids.get("XYZ"),                  "Màn hình 24 inch",1, 4500000, "2024-04-10"),
            (ids.get("phuquy"),               "Tai nghe gaming", 3, 750000,  "2024-06-05"),
            (ids.get("minhtan"),              "USB Hub 7 cổng",  4, 280000,  "2024-07-20"),
            (ids.get("minhtan"),              "Webcam HD",       2, 960000,  "2024-08-01"),
            (ids.get("27_HoangCongThanh_01"), "Balo laptop",     1, 550000,  "2024-09-10"),
            (ids.get("27_HoangCongThanh_01"), "Đế tản nhiệt",   1, 390000,  "2024-10-01"),
        ]
        # Lọc bỏ các dòng có PartnerID = None (phòng trường hợp seed Partner chưa chạy)
        sample_donhang = [row for row in sample_donhang if row[0] is not None]

        cursor.executemany("""
            INSERT INTO DonHang (PartnerID, TenSanPham, SoLuong, DonGia, NgayDat)
            VALUES (?, ?, ?, ?, ?)
        """, sample_donhang)
        print(f"  Seed: đã chèn {len(sample_donhang)} bản ghi vào DonHang")
    else:
        print(f"  Seed: bảng DonHang đã có {count_donhang} bản ghi")

    conn.commit()
    conn.close()


seed_data()


# ============================================================
# HELPER: Kết nối DB trong request context
# ============================================================

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row   # Trả kết quả dạng dict-like
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


# ============================================================
# HELPER nội bộ cho trang chủ
# ============================================================

def get_partner_27_HoangCongThanh_01():
    db = get_db()
    return db.execute(
        "SELECT * FROM Partner WHERE PartnerName = ?",
        ("27_HoangCongThanh_01",)
    ).fetchone()


def get_all_partners():
    db = get_db()
    return db.execute("SELECT * FROM Partner ORDER BY PartnerID").fetchall()


# ============================================================
# ROUTE: Trang chủ
# ============================================================

@app.route("/")
def index():
    partner  = get_partner_27_HoangCongThanh_01()
    partners = get_all_partners()
    return render_template("index.html", partner=partner, partners=partners)


# ============================================================
# CÂU 2 – CRUD CƠ BẢN
# ============================================================

@app.route("/partners", methods=["GET"])
def get_Partner():
    rows = get_db().execute("SELECT * FROM Partner ORDER BY PartnerID").fetchall()
    return {"partners": [dict(r) for r in rows]}


@app.route("/partners/<int:partner_id>", methods=["DELETE"])
def delete_Partner(partner_id):
    db = get_db()
    db.execute("DELETE FROM Partner WHERE PartnerID = ?", (partner_id,))
    db.commit()
    return {"deleted": partner_id}


# ============================================================
# CÂU 3 – THÊM / CẬP NHẬT PARTNER
# ============================================================

@app.route("/partners", methods=["POST"])
def add_Partner():
    data = request.json
    db = get_db()
    cursor = db.execute(
        "INSERT INTO Partner (PartnerName, AccountName, EmailAddress, Password, Tel, FromDate) VALUES (?, ?, ?, ?, ?, ?)",
        (data["PartnerName"], data["AccountName"], data["EmailAddress"], data["Password"], data["Tel"], data["FromDate"])
    )
    db.commit()
    return {"PartnerID": cursor.lastrowid}


@app.route("/partners/<int:partner_id>", methods=["PUT"])
def update_Partner(partner_id):
    data = request.json
    db = get_db()
    db.execute(
        "UPDATE Partner SET PartnerName=?, AccountName=?, EmailAddress=?, Password=?, Tel=?, FromDate=? WHERE PartnerID=?",
        (data["PartnerName"], data["AccountName"], data["EmailAddress"], data["Password"], data["Tel"], data["FromDate"], partner_id)
    )
    db.commit()
    return {"updated": partner_id}


# ============================================================
# METHOD MỚI 1 – ĐĂNG NHẬP (Login)
# POST /partners/login
# Body JSON: { "EmailAddress": "...", "Password": "..." }
# ============================================================

@app.route("/partners/login", methods=["POST"])
def login_partner():
    data = request.json  # Nhận dữ liệu JSON từ client

    # Lấy email và password từ body; strip() loại bỏ khoảng trắng thừa
    email    = (data.get("EmailAddress") or "").strip()
    password = (data.get("Password")     or "").strip()

    # Kiểm tra đầu vào – trả lỗi 400 nếu thiếu thông tin
    if not email or not password:
        return {"success": False, "message": "EmailAddress và Password không được để trống."}, 400

    # Truy vấn tìm Partner khớp cả email lẫn password
    # Dùng tham số hóa (?) để ngăn SQL Injection
    row = get_db().execute(
        "SELECT * FROM Partner WHERE EmailAddress = ? AND Password = ?",
        (email, password)
    ).fetchone()

    if row:
        # Tìm thấy → đăng nhập thành công, trả thông tin Partner (bỏ Password)
        partner_info = dict(row)
        partner_info.pop("Password", None)   # Không trả Password về client
        return {"success": True, "message": "Đăng nhập thành công.", "partner": partner_info}
    else:
        # Không tìm thấy → sai email hoặc password
        return {"success": False, "message": "Email hoặc mật khẩu không đúng."}, 401


# ============================================================
# METHOD MỚI 2 – TÌM KIẾM GẦN ĐÚNG (Search)
# GET /partners/search?q=<chuỗi tìm kiếm>
# ============================================================

@app.route("/partners/search", methods=["GET"])
def search_partners():
    # Lấy chuỗi tìm kiếm từ query parameter ?q=...
    query = (request.args.get("q") or "").strip()

    # Nếu không truyền gì, trả danh sách rỗng kèm thông báo
    if not query:
        return {"partners": [], "message": "Vui lòng cung cấp tham số tìm kiếm ?q=..."}

    # Bọc chuỗi tìm kiếm bằng % để dùng với LIKE (tìm kiếm gần đúng / chứa chuỗi con)
    like_query = f"%{query}%"

    # Tìm trên 3 cột: PartnerName, AccountName, EmailAddress
    # LIKE trong SQLite không phân biệt hoa thường với ký tự ASCII
    rows = get_db().execute(
        """
        SELECT * FROM Partner
        WHERE PartnerName  LIKE ?
           OR AccountName  LIKE ?
           OR EmailAddress LIKE ?
        ORDER BY PartnerID
        """,
        (like_query, like_query, like_query)   # 3 tham số tương ứng 3 dấu ?
    ).fetchall()

    # Chuyển list sqlite3.Row → list dict để Flask tự serialize sang JSON
    return {"count": len(rows), "partners": [dict(r) for r in rows]}


# ============================================================
# METHOD MỚI 3 – DANH SÁCH ĐƠN HÀNG THEO PARTNER
# GET /partners/<partner_id>/orders
# ============================================================

@app.route("/partners/<int:partner_id>/orders", methods=["GET"])
def get_orders_by_partner(partner_id):
    db = get_db()

    # Bước 1: Kiểm tra Partner có tồn tại không
    partner = db.execute(
        "SELECT PartnerID, PartnerName FROM Partner WHERE PartnerID = ?",
        (partner_id,)
    ).fetchone()

    if not partner:
        # Không tìm thấy Partner → trả lỗi 404
        return {"message": f"Không tìm thấy Partner với ID = {partner_id}."}, 404

    # Bước 2: Lấy tất cả đơn hàng thuộc Partner này
    # Sắp xếp theo NgayDat mới nhất lên đầu
    orders = db.execute(
        """
        SELECT * FROM DonHang
        WHERE PartnerID = ?
        ORDER BY NgayDat DESC
        """,
        (partner_id,)
    ).fetchall()

    # Bước 3: Tính tổng giá trị đơn hàng (SoLuong * DonGia) cho tiện theo dõi
    total_value = sum(row["SoLuong"] * row["DonGia"] for row in orders)

    # Bước 4: Trả JSON bao gồm thông tin Partner, danh sách đơn và tổng giá trị
    return {
        "partner": dict(partner),
        "total_orders": len(orders),
        "total_value": total_value,
        "orders": [dict(o) for o in orders]
    }


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    app.run(debug=True, port=5000)