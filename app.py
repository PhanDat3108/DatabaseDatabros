from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os
import random
from datetime import datetime

app = Flask(__name__)

db_config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'DatabrosPTIT',
    'password': 'databros123!',
    'database': 'QuanLyChuyenBay_Databros'
}

def get_connection():
    return mysql.connector.connect(**db_config)

def get_statistics_data():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT NgayDat, SUM(GiaVe) AS DoanhThu
        FROM DatVe
        GROUP BY NgayDat
        ORDER BY NgayDat
    """)
    doanh_thu_data = cursor.fetchall()
    labels = [row['NgayDat'].strftime('%d/%m') for row in doanh_thu_data]
    revenues = [float(row['DoanhThu']) for row in doanh_thu_data]

    cursor.execute("""
        SELECT NgayDat, COUNT(DISTINCT MaChuyenBay) AS SoChuyenBay
        FROM DatVe
        GROUP BY NgayDat
        ORDER BY NgayDat
    """)
    chuyen_bay_data = cursor.fetchall()
    flights = [int(row['SoChuyenBay']) for row in chuyen_bay_data]

    cursor.close()
    conn.close()
    return labels, revenues, flights
def get_nhanvien_list():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM NhanVien")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data
def get_image_list():
    image_folder = os.path.join(app.static_folder, 'anh')
    return [f"anh/{f}" for f in os.listdir(image_folder) if f.endswith(('.jpg', '.jpeg', '.png'))]

def get_unpaid_passengers():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT hk.MaHanhKhach, hk.HoTen, hk.GioiTinh, hk.QuocTich,
               dv.MaVe, dv.MaChuyenBay, dv.SoGhe, dv.HangVe, dv.GiaVe, dv.TrangThaiThanhToan
        FROM HanhKhach hk
        JOIN DatVe dv ON hk.MaHanhKhach = dv.MaHanhKhach
        WHERE dv.TrangThaiThanhToan = 'Chưa thanh toán'
        ORDER BY dv.NgayDat DESC
    """)
    passengers = cursor.fetchall()
    cursor.close()
    conn.close()
    return passengers

@app.route("/")
def thong_ke_trang_chu():
    labels, revenues, flights = get_statistics_data()
    images = get_image_list()
    unpaid_passengers = get_unpaid_passengers()
    nhanvien_list = get_nhanvien_list()  # <- dòng mới thêm vào
    return render_template("index.html", labels=labels, revenues=revenues,
                           flights=flights, images=images,
                           unpaid_passengers=unpaid_passengers,
                           nhanvien_list=nhanvien_list)  # <- truyền vào template

@app.route('/book_ticket', methods=['POST'])
def book_ticket():
    try:
        data = request.form
        ma_hanh_khach = 'HK' + str(random.randint(1000, 9999))
        ma_ve = 'VE' + str(random.randint(1000, 9999))
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO HanhKhach (MaHanhKhach, HoTen, GioiTinh, QuocTich, LoaiGiayTo, SoGiayTo, MaChuyenBay)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (ma_hanh_khach, data['hoten'], data['gioitinh'], data['quoctich'],
              data['loaigiayto'], data['sogiayto'], data['machuyenbay']))

        cursor.execute("""
            INSERT INTO HanhKhach_Contact (MaHanhKhach, SDT)
            VALUES (%s, %s)
        """, (ma_hanh_khach, data['sdt']))

        cursor.execute("""
            INSERT INTO DatVe (MaVe, MaChuyenBay, MaHanhKhach, NgayDat, SoGhe, HangVe, GiaVe, TrangThaiThanhToan)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (ma_ve, data['machuyenbay'], ma_hanh_khach, datetime.today().date(),
              data['soghe'], data['hangve'], data['giave'], data['trangthaithanhtoan']))

        conn.commit()
        cursor.close()
        conn.close()
        return "Đặt vé thành công!"
    except Exception as e:
        return f"Lỗi khi đặt vé: {e}"

@app.route('/add_luggage', methods=['POST'])
def add_luggage():
    try:
        data = request.form
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM HanhLy")
        ma_hanh_ly = f"HL{cursor.fetchone()[0] + 1:03d}"

        cursor.execute("""
            INSERT INTO HanhLy (MaHanhLy, MaHanhKhach, TrongLuong, MoTa)
            VALUES (%s, %s, %s, %s)
        """, (ma_hanh_ly, data['mahanhkhach'], data['trongluong'], data['mota']))

        conn.commit()
        cursor.close()
        conn.close()
        return "Thêm hành lý thành công!"
    except Exception as e:
        return f"Lỗi thêm hành lý: {e}"

@app.route('/search_ticket', methods=['POST'])
def search_ticket():
    searched = request.form['searchve']
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT hk.MaHanhKhach, hk.HoTen, hk.QuocTich, dv.MaVe, dv.SoGhe,
               dv.HangVe, dv.GiaVe, dv.TrangThaiThanhToan, dv.MaChuyenBay
        FROM HanhKhach hk
        JOIN DatVe dv ON hk.MaHanhKhach = dv.MaHanhKhach
        WHERE hk.MaHanhKhach = %s
    """, (searched,))
    tickets = cursor.fetchall()
    cursor.close()
    conn.close()

    labels, revenues, flights = get_statistics_data()
    images = get_image_list()
    unpaid_passengers = get_unpaid_passengers()
    return render_template("index.html", tickets=tickets, searched=searched,
                           labels=labels, revenues=revenues, flights=flights,
                           images=images, unpaid_passengers=unpaid_passengers)
@app.route('/search_flight', methods=['POST'])
def search_flight():
    machuyenbay = request.form['search_machuyenbay']
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM ChuyenBay WHERE MaChuyenBay = %s
    """, (machuyenbay,))
    flights_list = cursor.fetchall()

    cursor.close()
    conn.close()

    labels, revenues, flights = get_statistics_data()
    images = get_image_list()
    unpaid_passengers = get_unpaid_passengers()
    return render_template("index.html", flights_list=flights_list,
                           labels=labels, revenues=revenues,
                           flights=flights, images=images,
                           unpaid_passengers=unpaid_passengers)
@app.route('/update_flight', methods=['POST'])
def update_flight():
    try:
        data = request.form
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE ChuyenBay
            SET MaMayBay = %s, SoHieu = %s, MaSanBayDoiTac = %s,
                HuongBay = %s, TrangThai = %s
            WHERE MaChuyenBay = %s
        """, (
            data['mamaybay'], data['sohieu'], data['masanbaydoitac'],
            data['huongbay'], data['trangthai'], data['machuyenbay']
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return "<script>alert('Cập nhật chuyến bay thành công!'); window.location.href = '/';</script>"
    except Exception as e:
        return f"<script>alert('Lỗi khi cập nhật: {str(e)}'); window.location.href = '/';</script>"


@app.route('/update_ticket', methods=['POST'])
def update_ticket():
    try:
        data = request.form
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE DatVe
            SET SoGhe = %s, HangVe = %s, GiaVe = %s, TrangThaiThanhToan = %s
            WHERE MaVe = %s
        """, (data['soghe'], data['hangve'], data['giave'], data['trangthai'], data['mave']))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('search_ticket'), code=307)
    except Exception as e:
        return f"<script>alert('Lỗi khi cập nhật: {str(e)}'); window.location.href = "/";</script>"

@app.route('/search_luggage', methods=['POST'])
def search_luggage():
    ma_hk = request.form['search_mahanhkhach']
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM HanhLy WHERE MaHanhKhach = %s", (ma_hk,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    labels, revenues, flights = get_statistics_data()
    images = get_image_list()
    unpaid_passengers = get_unpaid_passengers()
    return render_template("index.html", luggage_list=data,
                           labels=labels, revenues=revenues,
                           flights=flights, images=images,
                           unpaid_passengers=unpaid_passengers)

@app.route('/update_luggage', methods=['POST'])
def update_luggage():
    try:
        data = request.form
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE HanhLy
            SET TrongLuong = %s, MoTa = %s
            WHERE MaHanhLy = %s
        """, (data['trongluong'], data['mota'], data['mahanhly']))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('thong_ke_trang_chu'))
    except Exception as e:
        return f"<script>alert('Lỗi khi cập nhật: {str(e)}'); window.location.href = "/";</script>"

@app.route("/update_payment", methods=["POST"])
def update_payment():
    mave = request.form["mave"]

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE DatVe SET TrangThaiThanhToan = 'Đã thanh toán' WHERE MaVe = %s
    """, (mave,))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('thong_ke_trang_chu'))
@app.route('/search_unpaid', methods=['POST'])
def search_unpaid():
    ma_hk = request.form['search_mahk']
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Kết quả tìm kiếm theo mã hành khách
    cursor.execute("""
        SELECT hk.MaHanhKhach, hk.HoTen, hk.GioiTinh, hk.QuocTich,
               dv.MaVe, dv.MaChuyenBay, dv.SoGhe, dv.HangVe, dv.GiaVe, dv.TrangThaiThanhToan
        FROM HanhKhach hk
        JOIN DatVe dv ON hk.MaHanhKhach = dv.MaHanhKhach
        WHERE dv.TrangThaiThanhToan = 'Chưa thanh toán' AND hk.MaHanhKhach = %s
    """, (ma_hk,))
    filtered_results = cursor.fetchall()

    # Bảng tổng toàn bộ hành khách chưa thanh toán
    cursor.execute("""
        SELECT hk.MaHanhKhach, hk.HoTen, hk.GioiTinh, hk.QuocTich,
               dv.MaVe, dv.MaChuyenBay, dv.SoGhe, dv.HangVe, dv.GiaVe, dv.TrangThaiThanhToan
        FROM HanhKhach hk
        JOIN DatVe dv ON hk.MaHanhKhach = dv.MaHanhKhach
        WHERE dv.TrangThaiThanhToan = 'Chưa thanh toán'
        ORDER BY dv.NgayDat DESC
    """)
    unpaid_passengers_all = cursor.fetchall()

    cursor.close()
    conn.close()

    labels, revenues, flights = get_statistics_data()
    images = get_image_list()

    return render_template("index.html",
                           labels=labels,
                           revenues=revenues,
                           flights=flights,
                           images=images,
                           unpaid_passengers=unpaid_passengers_all,
                           search_result=filtered_results,
                           search_mahk=ma_hk,
                           show_unpaid=True)

@app.route("/add_flight", methods=["POST"])
def add_flight():
    try:
        data = request.form
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO ChuyenBay (MaChuyenBay, MaMayBay, SoHieu, MaSanBayDoiTac, HuongBay, TrangThai)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data['machuyenbay'],
            data['mamaybay'],
            data['sohieu'],
            data['masanbaydoitac'],
            data['huongbay'],
            data['trangthai']
        ))

        conn.commit()
        cursor.close()
        conn.close()

        # Trả về thông báo alert
        return """
        <script>
            alert("Đã thêm chuyến bay thành công!");
            window.location.href = "/";
        </script>
        """
    except Exception as e:
        return f"""
        <script>
            alert("Lỗi khi thêm chuyến bay: {str(e)}");
            window.location.href = "/";
        </script>
        """

@app.route("/add_nhanvien", methods=["POST"])
def add_nhanvien():
    try:
        data = request.form
        conn = get_connection()
        cursor = conn.cursor()

        # Sinh mã NV tiếp theo
        cursor.execute("SELECT COUNT(*) FROM NhanVien")
        next_id = cursor.fetchone()[0] + 101
        ma_nv = f"NV{next_id}"

        cursor.execute("""
            INSERT INTO NhanVien (MaNhanVien, HoTen, GioiTinh, VaiTro, MaChuyenBay, TrangThaiLamViec)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (ma_nv, data["hoten"], data["gioitinh"], data["vaitro"],
              data["machuyenbay"] if data["machuyenbay"] else None,
              data["trangthai"]))

        conn.commit()
        cursor.close()
        conn.close()

        return "<script>alert('Thêm nhân viên thành công!'); window.location.href = '/';</script>"
    except Exception as e:
        return f"<script>alert('Lỗi khi thêm nhân viên: {str(e)}'); window.location.href = '/';</script>"

if __name__ == "__main__":
    app.run(debug=True)