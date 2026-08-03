from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
import os
from datetime import datetime

app = Flask(__name__)

# Konfigurasi Upload
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # Maksimal ukuran file 16MB
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
# ==========================================
# 2. ABSENSI MINGGUAN
# ==========================================
# Tambahkan ini di bagian atas jika belum ada (untuk nama hari bahasa Indonesia)
indo_days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

# ---------------------------------------------------------
# KONEKSI MONGODB ATLAS
# Ganti string di bawah dengan URI MongoDB Atlas Anda
# ---------------------------------------------------------
MONGO_URI = "mongodb+srv://muhammaddarjuni76_db_user:dI42gI11RtTIw7YM@fyy.uddizvu.mongodb.net/?appName=fyy"
client = MongoClient(MONGO_URI)
db = client['medium'] # Nama database

# ==========================================
# 1. DASHBOARD & TOTAL TEAM BALANCE
# ==========================================
@app.route('/')
def index():
    # Menghitung Total Kas (Balance)
    incomes = list(db.finance.find({"type": "in"}))
    expenses = list(db.finance.find({"type": "out"}))
    
    total_in = sum(item['amount'] for item in incomes)
    total_out = sum(item['amount'] for item in expenses)
    balance = total_in - total_out

    # Mengambil Task yang masih berjalan (Preview)
    active_tasks = list(db.tasks.find({"status": "active"}).limit(5))
    
    return render_template('index.html', balance=balance, total_in=total_in, total_out=total_out, tasks=active_tasks)


# ==========================================
# 2. ABSENSI MINGGUAN & STATISTIK (UPDATE ROLE)
# ==========================================
@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    team_data = db.settings.find_one({"_id": "team_settings"})
    members_list = team_data.get('members_array', []) if team_data else []

    if request.method == 'POST':
        db.attendance.insert_one({
            "name": request.form.get('name'),
            "status": request.form.get('status'),
            "notes": request.form.get('notes'),
            "date_submitted": datetime.now()
        })
        return redirect(url_for('attendance'))
    
    records = list(db.attendance.find().sort("date_submitted", -1))
    
    # Siapkan wadah Statistik dengan membaca format baru (Objek) atau lama (String)
    stats = {}
    for m in members_list:
        if isinstance(m, dict): # Format baru dengan role
            m_name = m.get('name')
            m_role = m.get('role')
        else: # Format lama (hanya string nama)
            m_name = m
            m_role = 'Belum di-set'
            
        stats[m_name] = {'Hadir': 0, 'Izin': 0, 'Sakit': 0, 'Wajib_Hadir': 0, 'Role': m_role}
    
    for rec in records:
        name = rec.get('name')
        hari_index = rec['date_submitted'].weekday()
        
        rec['hari_indo'] = indo_days[hari_index]
        rec['is_wajib'] = hari_index in [0, 5] # 0 = Senin, 5 = Sabtu
        
        if rec['is_wajib'] and name in stats:
            stats[name]['Wajib_Hadir'] += 1
            status = rec.get('status')
            if status in stats[name]:
                stats[name][status] += 1

    return render_template('attendance.html', records=records, members=members_list, stats=stats)


# ==========================================
# FITUR: KELOLA ANGGOTA (UPDATE ROLE)
# ==========================================
@app.route('/members', methods=['GET', 'POST'])
def members():
    if request.method == 'POST':
        action = request.form.get('action')
        member_name = request.form.get('member_name')
        member_role = request.form.get('member_role')
        
        if action == 'add' and member_name and member_role:
            # Hapus data lama (jika ada nama yg sama) agar tidak duplikat, lalu push yang baru dengan role
            db.settings.update_one(
                {"_id": "team_settings"}, 
                {"$pull": {"members_array": {"name": member_name}}} # Hapus format objek
            )
            db.settings.update_one(
                {"_id": "team_settings"}, 
                {"$pull": {"members_array": member_name}} # Hapus format string lama jika ada
            )
            # Masukkan sebagai objek
            db.settings.update_one(
                {"_id": "team_settings"}, 
                {"$push": {"members_array": {"name": member_name, "role": member_role}}}, 
                upsert=True
            )
        elif action == 'delete' and member_name:
            # Hapus dari array (Cek format objek maupun string)
            db.settings.update_one(
                {"_id": "team_settings"}, 
                {"$pull": {"members_array": {"name": member_name}}}
            )
            db.settings.update_one(
                {"_id": "team_settings"}, 
                {"$pull": {"members_array": member_name}}
            )
        return redirect(url_for('members'))
    
    team_data = db.settings.find_one({"_id": "team_settings"})
    members_list = team_data.get('members_array', []) if team_data else []
    
    return render_template('members.html', members=members_list)
# ==========================================
# 3. KAS MASUK KELUAR (TRANSPARAN)
# ==========================================
@app.route('/finance', methods=['GET', 'POST'])
def finance():
    if request.method == 'POST':
        db.finance.insert_one({
            "type": request.form.get('type'), # 'in' (Pemasukan) atau 'out' (Pengeluaran)
            "amount": float(request.form.get('amount')),
            "description": request.form.get('description'),
            "user": request.form.get('user'), # Siapa yang input
            "date": datetime.now()
        })
        return redirect(url_for('finance'))
    
    transactions = list(db.finance.find().sort("date", -1))
    return render_template('finance.html', transactions=transactions)

# ==========================================
# 4. DAFTAR PROJECT & PASSED TASK
# ==========================================
@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    if request.method == 'POST':
        db.tasks.insert_one({
            "title": request.form.get('title'),
            "description": request.form.get('description'),
            "status": "active", # Default status
            "date_created": datetime.now()
        })
        return redirect(url_for('tasks'))
    
    active_tasks = list(db.tasks.find({"status": "active"}))
    passed_tasks = list(db.tasks.find({"status": "passed"}))
    return render_template('tasks.html', active_tasks=active_tasks, passed_tasks=passed_tasks)

@app.route('/task/complete/<task_id>')
def complete_task(task_id):
    # Ubah status task menjadi passed
    db.tasks.update_one({"_id": ObjectId(task_id)}, {"$set": {"status": "passed"}})
    return redirect(url_for('tasks'))

# ==========================================
# 5. UPLOAD ASSETS / DOKUMENTASI
# ==========================================
@app.route('/assets', methods=['GET', 'POST'])
def assets():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            db.assets.insert_one({
                "filename": filename,
                "description": request.form.get('description'),
                "upload_date": datetime.now()
            })
        return redirect(url_for('assets'))
    
    files = list(db.assets.find().sort("upload_date", -1))
    return render_template('assets.html', files=files)

# ==========================================
# 6. DATABASE CONSOLE (MIGRASI / BROADCAST KEY)
# ==========================================
@app.route('/console', methods=['GET', 'POST'])
def db_console():
    message = ""
    status_type = "success"
    
    # PERHATIKAN: Pengecekan form hanya terjadi JIKA methodnya POST (tombol diklik)
    if request.method == 'POST':
        target = request.form.get('target')        
        new_key = request.form.get('new_key')      
        default_val = request.form.get('default_val') 
        
        # Mencegah error jika default_val kosong
        if default_val and default_val.isdigit():
            default_val = int(default_val)
            
        if not new_key:
            message = "Nama Key tidak boleh kosong!"
            status_type = "danger"
        else:
            if target == 'members':
                team_data = db.settings.find_one({"_id": "team_settings"})
                if team_data and 'members_array' in team_data:
                    updated_members = []
                    for member in team_data['members_array']:
                        if isinstance(member, dict):
                            member[new_key] = default_val
                            updated_members.append(member)
                        else:
                            updated_members.append({
                                "name": member, 
                                "role": "Belum di-set", 
                                new_key: default_val
                            })
                    
                    db.settings.update_one(
                        {"_id": "team_settings"},
                        {"$set": {"members_array": updated_members}}
                    )
                    message = f"Berhasil broadcast key '{new_key}' ke semua data Anggota!"
                    
            elif target in ['attendance', 'finance', 'tasks', 'assets']:
                db[target].update_many({}, {"$set": {new_key: default_val}})
                message = f"Berhasil broadcast key '{new_key}' ke semua data di koleksi '{target}'!"
                
    # INI HARUS SEJAJAR DENGAN 'if request.method' (Jangan terlalu menjorok ke dalam)
    return render_template('console.html', message=message, status_type=status_type)
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)