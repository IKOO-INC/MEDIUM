from flask import Flask, render_template, request, redirect, url_for, send_file, send_from_directory, abort
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
from io import BytesIO
from urllib.parse import urlparse, urlsplit, urlunsplit, quote, unquote
import os
import uuid
from datetime import datetime

import cloudinary
import cloudinary.uploader
from cloudinary.exceptions import Error as CloudinaryError

import qrcode
from qrcode.constants import ERROR_CORRECT_M

app = Flask(__name__)

# Konfigurasi Upload
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Maksimal ukuran file 16MB
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Nama hari bahasa Indonesia
indo_days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

# ---------------------------------------------------------
# KONEKSI MONGODB ATLAS
# ---------------------------------------------------------
MONGO_URI = "mongodb+srv://muhammaddarjuni76_db_user:dI42gI11RtTIw7YM@fyy.uddizvu.mongodb.net/?appName=fyy"
client = MongoClient(MONGO_URI)
db = client['medium']


# ==========================================
# HELPER ANGGOTA & ABSENSI QR
# ==========================================
def ensure_member_qr_tokens():
    """Pastikan seluruh anggota berbentuk object dan memiliki qr_token unik."""
    team_data = db.settings.find_one({"_id": "team_settings"})
    raw_members = team_data.get('members_array', []) if team_data else []

    normalized_members = []
    used_tokens = set()
    changed = False

    for member in raw_members:
        if isinstance(member, dict):
            normalized = dict(member)
        else:
            normalized = {
                "name": member,
                "role": "Belum di-set"
            }
            changed = True

        normalized["name"] = str(normalized.get("name", "")).strip()
        normalized["role"] = normalized.get("role") or "Belum di-set"

        qr_token = str(normalized.get("qr_token", "")).strip()
        if not qr_token or qr_token in used_tokens:
            qr_token = uuid.uuid4().hex
            normalized["qr_token"] = qr_token
            changed = True

        used_tokens.add(qr_token)
        normalized_members.append(normalized)

        if normalized != member:
            changed = True

    if changed:
        db.settings.update_one(
            {"_id": "team_settings"},
            {"$set": {"members_array": normalized_members}},
            upsert=True
        )

    return normalized_members


def find_member_by_qr_token(qr_token):
    for member in ensure_member_qr_tokens():
        if member.get('qr_token') == qr_token:
            return member
    return None


def create_attendance_record(name, status, notes, method, qr_token=None):
    allowed_statuses = {"Hadir", "Izin", "Sakit"}
    clean_name = (name or "").strip()
    clean_status = (status or "").strip()
    clean_notes = (notes or "").strip()

    if not clean_name or clean_status not in allowed_statuses:
        return False

    record = {
        "name": clean_name,
        "status": clean_status,
        "notes": clean_notes,
        "method": method,
        "date_submitted": datetime.now()
    }
    if qr_token:
        record["qr_token"] = qr_token

    db.attendance.insert_one(record)
    return True


def get_attendance_context():
    members_list = ensure_member_qr_tokens()
    records = list(db.attendance.find().sort("date_submitted", -1))

    stats = {}
    for member in members_list:
        member_name = member.get('name')
        if not member_name:
            continue
        stats[member_name] = {
            'Hadir': 0,
            'Izin': 0,
            'Sakit': 0,
            'Wajib_Hadir': 0,
            'Role': member.get('role') or 'Belum di-set'
        }

    for record in records:
        submitted_at = record.get('date_submitted')
        if not isinstance(submitted_at, datetime):
            submitted_at = datetime.now()
            record['date_submitted'] = submitted_at

        day_index = submitted_at.weekday()
        record['hari_indo'] = indo_days[day_index]
        record['is_wajib'] = day_index in [0, 5]
        record['method'] = record.get('method') or 'manual'

        name = record.get('name')
        if record['is_wajib'] and name in stats:
            stats[name]['Wajib_Hadir'] += 1
            status = record.get('status')
            if status in stats[name]:
                stats[name][status] += 1

    return members_list, records, stats


# ==========================================
# 1. DASHBOARD & TOTAL TEAM BALANCE
# ==========================================
@app.route('/')
def index():
    incomes = list(db.finance.find({"type": "in"}))
    expenses = list(db.finance.find({"type": "out"}))

    total_in = sum(item['amount'] for item in incomes)
    total_out = sum(item['amount'] for item in expenses)
    balance = total_in - total_out

    active_tasks = list(db.tasks.find({"status": "active"}).limit(5))

    return render_template(
        'index.html',
        balance=balance,
        total_in=total_in,
        total_out=total_out,
        tasks=active_tasks
    )


# ==========================================
# 2. ABSENSI: REKAP, MANUAL, DAN SCAN QR
# ==========================================
@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    # Dukungan lama: POST ke /attendance tetap dianggap absen manual.
    if request.method == 'POST':
        create_attendance_record(
            request.form.get('name'),
            request.form.get('status'),
            request.form.get('notes'),
            method='manual'
        )
        return redirect(url_for('attendance'))

    members_list, records, stats = get_attendance_context()
    return render_template(
        'attendance.html',
        records=records,
        members=members_list,
        stats=stats,
        saved=request.args.get('saved')
    )


@app.route('/attendance/manual', methods=['GET', 'POST'])
def attendance_manual():
    members_list = ensure_member_qr_tokens()
    error = ""

    if request.method == 'POST':
        member_name = (request.form.get('name') or '').strip()
        valid_names = {member.get('name') for member in members_list}

        if member_name not in valid_names:
            error = "Anggota tidak ditemukan. Silakan pilih anggota dari daftar."
        elif create_attendance_record(
            member_name,
            request.form.get('status'),
            request.form.get('notes'),
            method='manual'
        ):
            return redirect(url_for('attendance', saved='manual'))
        else:
            error = "Data absensi belum lengkap atau status tidak valid."

    return render_template('attendance_manual.html', members=members_list, error=error)


@app.route('/attendance/scan')
def attendance_scan():
    return render_template('attendance_scan.html')


@app.route('/attendance/scan/<qr_token>', methods=['GET', 'POST'])
def attendance_scan_member(qr_token):
    member = find_member_by_qr_token(qr_token)
    if not member:
        abort(404)

    error = ""
    if request.method == 'POST':
        if create_attendance_record(
            member.get('name'),
            request.form.get('status'),
            request.form.get('notes'),
            method='scan',
            qr_token=qr_token
        ):
            return redirect(url_for('attendance', saved='scan'))
        error = "Status absensi tidak valid. Silakan periksa kembali."

    return render_template('attendance_scan_member.html', member=member, error=error)


# ==========================================
# FITUR: KELOLA ANGGOTA & QR
# ==========================================
@app.route('/members', methods=['GET', 'POST'])
def members():
    if request.method == 'POST':
        action = request.form.get('action')
        member_name = (request.form.get('member_name') or '').strip()
        member_role = (request.form.get('member_role') or '').strip()

        if action == 'add' and member_name and member_role:
            db.settings.update_one(
                {"_id": "team_settings"},
                {"$pull": {"members_array": {"name": member_name}}}
            )
            db.settings.update_one(
                {"_id": "team_settings"},
                {"$pull": {"members_array": member_name}}
            )
            db.settings.update_one(
                {"_id": "team_settings"},
                {"$push": {"members_array": {
                    "name": member_name,
                    "role": member_role,
                    "qr_token": uuid.uuid4().hex
                }}},
                upsert=True
            )
        elif action == 'delete' and member_name:
            db.settings.update_one(
                {"_id": "team_settings"},
                {"$pull": {"members_array": {"name": member_name}}}
            )
            db.settings.update_one(
                {"_id": "team_settings"},
                {"$pull": {"members_array": member_name}}
            )
        return redirect(url_for('members'))

    members_list = ensure_member_qr_tokens()
    return render_template('members.html', members=members_list)


@app.route('/members/qr')
def member_qr_list():
    members_list = ensure_member_qr_tokens()
    return render_template('member_qr.html', members=members_list)


@app.route('/members/qr/<qr_token>.png')
def member_qr_image(qr_token):
    member = find_member_by_qr_token(qr_token)
    if not member:
        abort(404)

    scan_url = url_for('attendance_scan_member', qr_token=qr_token, _external=True)
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_M,
        box_size=10,
        border=4
    )
    qr.add_data(scan_url)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white")

    image_buffer = BytesIO()
    image.save(image_buffer, format='PNG')
    image_buffer.seek(0)

    safe_name = secure_filename(member.get('name') or 'anggota') or 'anggota'
    return send_file(
        image_buffer,
        mimetype='image/png',
        as_attachment=request.args.get('download') == '1',
        download_name=f'QR-{safe_name}.png'
    )


# ==========================================
# 3. KAS MASUK KELUAR (TRANSPARAN)
# ==========================================
@app.route('/finance', methods=['GET', 'POST'])
def finance():
    if request.method == 'POST':
        db.finance.insert_one({
            "type": request.form.get('type'),
            "amount": float(request.form.get('amount')),
            "description": request.form.get('description'),
            "user": request.form.get('user'),
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
            "status": "active",
            "date_created": datetime.now()
        })
        return redirect(url_for('tasks'))

    active_tasks = list(db.tasks.find({"status": "active"}))
    passed_tasks = list(db.tasks.find({"status": "passed"}))
    return render_template('tasks.html', active_tasks=active_tasks, passed_tasks=passed_tasks)


@app.route('/task/complete/<task_id>')
def complete_task(task_id):
    db.tasks.update_one({"_id": ObjectId(task_id)}, {"$set": {"status": "passed"}})
    return redirect(url_for('tasks'))


# ==========================================
# 5. UPLOAD ASSETS / DOKUMENTASI — CLOUDINARY
# ==========================================
def get_cloudinary_config():
    """Ambil konfigurasi Cloudinary dari environment.

    Mendukung dua cara:
    1. CLOUDINARY_CLOUD_NAME + CLOUDINARY_API_KEY + CLOUDINARY_API_SECRET
    2. CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME
    """
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME', '').strip()
    api_key = os.getenv('CLOUDINARY_API_KEY', '').strip()
    api_secret = os.getenv('CLOUDINARY_API_SECRET', '').strip()

    cloudinary_url = os.getenv('CLOUDINARY_URL', '').strip()
    if cloudinary_url and cloudinary_url.startswith('cloudinary://'):
        parsed = urlparse(cloudinary_url)
        cloud_name = cloud_name or (parsed.hostname or '')
        api_key = api_key or (parsed.username or '')
        api_secret = api_secret or unquote(parsed.password or '')

    folder = os.getenv('CLOUDINARY_FOLDER', 'media-roudlotul-ulum').strip()
    return cloud_name, api_key, api_secret, folder


def configure_cloudinary():
    """Konfigurasi SDK Cloudinary untuk aplikasi Flask."""
    cloud_name, api_key, api_secret, folder = get_cloudinary_config()
    if not (cloud_name and api_key and api_secret):
        raise RuntimeError(
            'Cloudinary belum dikonfigurasi. Isi CLOUDINARY_CLOUD_NAME, '
            'CLOUDINARY_API_KEY, dan CLOUDINARY_API_SECRET.'
        )

    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True
    )
    return folder


def cloudinary_is_configured():
    cloud_name, api_key, api_secret, _ = get_cloudinary_config()
    return bool(cloud_name and api_key and api_secret)


def upload_to_cloudinary(file_storage):
    """Upload file dari Flask/Werkzeug menggunakan Cloudinary Python SDK."""
    folder = configure_cloudinary()

    original_filename = file_storage.filename or 'asset'
    content_type = file_storage.mimetype or 'application/octet-stream'

    try:
        # SDK menangani signature/authentication di sisi server.
        result = cloudinary.uploader.upload(
            file_storage.stream,
            resource_type='auto',
            folder=folder,
            use_filename=True,
            unique_filename=True,
            overwrite=False
        )
    except CloudinaryError as exc:
        raise RuntimeError(f'Upload ke Cloudinary gagal: {exc}') from exc
    except (OSError, ValueError, TypeError) as exc:
        raise RuntimeError(f'Upload ke Cloudinary gagal: {exc}') from exc

    return {
        'filename': original_filename,
        'description': '',
        'storage': 'cloudinary',
        'cloudinary_public_id': result.get('public_id'),
        'cloudinary_resource_type': result.get('resource_type'),
        'cloudinary_format': result.get('format'),
        'cloudinary_version': result.get('version'),
        'cloudinary_type': result.get('type'),
        'url': result.get('secure_url'),
        'bytes': result.get('bytes'),
        'content_type': content_type
    }

def cloudinary_download_url(asset):
    """Tambahkan fl_attachment agar browser mengunduh asset Cloudinary."""
    asset_url = asset.get('url')
    if not asset_url:
        return None

    filename = asset.get('filename') or 'asset'
    parsed = urlsplit(asset_url)
    marker = '/upload/'
    if marker not in parsed.path:
        return asset_url

    before, after = parsed.path.split(marker, 1)
    attachment_name = quote(filename, safe='')
    parsed_path = f'{before}{marker}fl_attachment:{attachment_name}/{after.lstrip("/")}'
    return urlunsplit((parsed.scheme, parsed.netloc, parsed_path, parsed.query, parsed.fragment))


@app.route('/assets', methods=['GET', 'POST'])
def assets():
    error = request.args.get('error', '')

    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(url_for('assets', error='File tidak ditemukan.'))

        file = request.files['file']
        if not file.filename:
            return redirect(url_for('assets', error='Silakan pilih file terlebih dahulu.'))

        try:
            asset = upload_to_cloudinary(file)
            asset['description'] = (request.form.get('description') or '').strip()
            asset['upload_date'] = datetime.now()
            db.assets.insert_one(asset)
        except RuntimeError as exc:
            return redirect(url_for('assets', error=str(exc)))

        return redirect(url_for('assets'))

    files = list(db.assets.find().sort("upload_date", -1))
    return render_template('assets.html', files=files, error=error)


@app.route('/assets/download/<asset_id>')
def download_asset(asset_id):
    """Download Cloudinary asset atau asset lokal lama."""
    try:
        object_id = ObjectId(asset_id)
    except Exception:
        abort(404)

    asset = db.assets.find_one({'_id': object_id})
    if not asset:
        abort(404)

    if asset.get('storage') == 'cloudinary':
        download_url = cloudinary_download_url(asset)
        if not download_url:
            abort(404)
        return redirect(download_url)

    filename = asset.get('filename')
    if not filename:
        abort(404)

    local_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.isfile(local_path):
        abort(404)

    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=True,
        download_name=filename
    )


# ==========================================
# 6. DATABASE CONSOLE (MIGRASI / BROADCAST KEY)
# ==========================================
@app.route('/console', methods=['GET', 'POST'])
def db_console():
    message = ""
    status_type = "success"

    if request.method == 'POST':
        target = request.form.get('target')
        new_key = request.form.get('new_key')
        default_val = request.form.get('default_val')

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

    return render_template('console.html', message=message, status_type=status_type)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
