from flask import *
import os, uuid
import certifi
from datetime import timedelta, datetime
banner = 'Untitled-2.png'
from pymongo import MongoClient

######### cek cek ################
def check_mongo(cl, idw):
    try:
        cl.admin.command("ping")
        print(f"[ DB{idw} ] MongoDB connected")
    except Exception as e:
        print(f"[DB{idw}] MongoDB FAILED")
        print(e)

######### database pertama / berita  #########
c1 = MongoClient(
    "mongodb+srv://farhans:ikoo@web.do21pri.mongodb.net/?appName=web",tls=True,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=20000
)
db1 = c1["pondok"]
db_news = db1["news"]
check_mongo(c1, 1)
######### database kedua / conf, nontif  #########
c2 = MongoClient(
    f"mongodb+srv://ikoo:farhans@web2.ndwn5ag.mongodb.net/?appName=web2",tls=True,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=20000
)
db2 = c2["pondok"]
db_conf = db2["configure"]
db_nontif = db2["nontif"]
check_mongo(c2, 2)
######### database ketiga / galery  #########
c3 = MongoClient(
    f"mongodb+srv://farfar:hanshans@web3.hg8xpqu.mongodb.net/?appName=web3",tls=True,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=20000
)
db3 = c3["pondok"]
db_galery = db3["galery"]
check_mongo(c3, 3)
####################################################
# i x4 k x4 o x4 o x4
a = Flask('ya')
a.secret_key = 'iiiikkkkoooooooo'
a.config['MAX_CONTENT_LENGTH'] = 80 * 1024 * 1024
a.permanent_session_lifetime = timedelta(days=1)
login_devices = []
#==============================================
DATA_FOLDER = 'data'
os.makedirs(DATA_FOLDER, exist_ok=True)
UPLOAD_FOLDER = 'static'
a.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
conf = {
    'arab': 'اَلْمَعْهَدُ الْإِسْلَامِيُّ السَّلَفِيُّ رَوْضَةُ الْعُلُومِ',
    'tentang': """Selamat datang di website Al-Ma’had al-Islami as-Salafi Roudlotul Ulum.
Website ini disediakan untuk memudahkan para wali santri dan masyarakat dalam memperoleh informasi terbaru tentang kegiatan dan perkembangan ma’had.

Dengan motto <strong>“Ilmiyah – Amaliyah – Amaliyah – Ilmiyah”</strong>, Al-Ma’had al-Islami as-Salafi Roudlotul Ulum berkomitmen meningkatkan kualitas pendidikan santri melalui berbagai jenjang pendidikan, mulai dari SMP, SMK, hingga Perguruan Tinggi. Setiap kegiatan pembelajaran diarahkan agar ilmu dapat diamalkan dengan benar sesuai tuntunan syar’i.

Semoga seluruh ikhtiar ini menjadi langkah meraih ridha Allah SWT. """
}
hit_pg1_p = 1
hit_pg1 = 0

nontifikasi = [{
    'ic': '#custom-security-safe',
    't': 'Visited',
    'kt': 'Developer membuat website ini',
    'tm': '11 Desember 2025'
}]
from datetime import datetime, timedelta
import threading
import time

###############      database image 25 gb free hehehehehehe
import cloudinary
import cloudinary.uploader
import cloudinary.api
cloudinary.config(
    cloud_name="dakwyt1c4",
    api_key="263124236154547",
    api_secret="j4SZavaBMFs7YhEKZDWlyGoBF4E"
)



###############
def upclod(fl, nm, typ, code=0):
    if code == 0:
        cloudinary.config(
            cloud_name="dakwyt1c4",
            api_key="263124236154547",
            api_secret="j4SZavaBMFs7YhEKZDWlyGoBF4E"
        )

        rr = cloudinary.uploader.upload(
            fl,
            folder=nm,
            resource_type=typ
        )
        return rr
    else :
        cloudinary.config(
            cloud_name='dd4l93bpc',
            api_key='571195999223591',
            api_secret='x20kpXFFYAxIOmWrnUh29Id5L3k'
        )
        rr = cloudinary.uploader.upload(
            fl,
            folder=nm,
            resource_type=typ
        )
        cloudinary.config(
            cloud_name="dakwyt1c4",
            api_key="263124236154547",
            api_secret="j4SZavaBMFs7YhEKZDWlyGoBF4E"
        )
        return rr



def nontif(a1, a2,a3):
    match a1:
        case 'security':
            ica = '#custom-security-safe'
        case 'user':
            ica = '#custom-user-bold'
        case 'news':
            ica = '#custom-document-text'
    yy = {
        'ic': ica,
        't': a2,
        'kt': a3,
        'tm': tanggal()
    }
    print (yy)
    db_nontif.insert_one(yy)
    nontifikasi.insert(0, yy)
    return print ('[nontifikasi] berhasil')

import re

def parse_user_agent(ua: str):
    ua_l = ua.lower()

    # Device type
    is_mobile = any(x in ua_l for x in ["android", "iphone", "ipad", "mobile"])
    device_type = "Mobile" if is_mobile else "Desktop"

    # OS + version
    os_name = "Unknown"
    os_version = ""

    m = re.search(r'android\s([\d\.]+)', ua_l)
    if m:
        os_name = "Android"
        os_version = m.group(1)
    else:
        m = re.search(r'windows nt\s([\d\.]+)', ua_l)
        if m:
            os_name = "Windows"
            win_map = {
                "10.0": "10 / 11",
                "6.3": "8.1",
                "6.2": "8",
                "6.1": "7"
            }
            os_version = win_map.get(m.group(1), m.group(1))

    # Browser
    if "edg" in ua_l:
        browser = "Edge"
    elif "opr" in ua_l or "opera" in ua_l:
        browser = "Opera"
    elif "chrome" in ua_l and "safari" in ua_l:
        browser = "Chrome"
    elif "firefox" in ua_l:
        browser = "Firefox"
    elif "safari" in ua_l:
        browser = "Safari"
    else:
        browser = "Unknown"

    return {
        "device_type": device_type,
        "os": f"{os_name} {os_version}".strip(),
        "browser": browser
    }



def analisa_view(view_lama, view_baru):
    if view_lama == 0:
        return {'s': False, 'v':"0%"}

    selisih = view_baru - view_lama
    persen = (selisih / view_lama) * 100

    if selisih > 0:
        ya = {'s': True, 'v':f"{persen:.2f}%"}
        return ya
    elif selisih < 0:
        ya = {'s': False, 'v':f"{abs(persen):.2f}%"}
        return ya
    else:
        return {'s': False, 'v':"0%"}

def recap_hit_dasboard():
    global hit_pg1, hit_pg1_p

    while True:
        now = datetime.now()
        # jika jam == 00 dan menit == 00
        if now.hour == 0 and now.minute == 0:
            hit_pg1_p = hit_pg1
            hit_pg1 = 0
            print("RESET di jam 00:00 -> my_value kembali ke 0")

            # tidur 60 detik agar tidak reset berkali-kali
            time.sleep(60)

        time.sleep(1)  # cek setiap 1 detik

import os

if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    print(' [ pemantauan recap active ]')
    threading.Thread(target=recap_hit_dasboard, daemon=True).start()

def tanggal():
    now_jkt = datetime.utcnow() + timedelta(hours=7)

    bulan_id = [
        "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]

    return f"{now_jkt.day} {bulan_id[now_jkt.month]} {now_jkt.year}"


def ldb():
    with open('./data/post.json', "r") as f:
        return json.load(f)

def sdb(data):
    with open('./data/post.json', "w") as f:
        json.dump(data, f, indent=4) 

def get_index(value):
    data = list(
    db_news.find()
    .sort("_id", -1)
    )   # data = list

    for index, item in enumerate(data):
        if item.get('idpost') == value:
            return index

    return -1   # kalau tidak ditemukan
def sih(yaa):
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(yaa, "html.parser")

    teks_bersih = soup.get_text(separator=" ", strip=True)
    return teks_bersih

def caplek(text, max_words=30):
    words = text.split()
    if len(words) <= max_words:
        return sih(text + ' ...')
    return sih(" ".join(words[:max_words]) + " ...")

@a.route('/admin')
def brkfbkbfer():
    if not session.get('admin'):
        return redirect('/admin/login')
    nec = ldb()
    nyy = list(
    db_nontif.find({}, {"_id": 0})
        .sort("created_at", -1)
)

    dts = {
        'hit': hit_pg1,
        'hit_stats': analisa_view(hit_pg1_p, hit_pg1)['s'],
        'hit_persent': analisa_view(hit_pg1_p, hit_pg1)['v'],
        'a_n': len(nec),
        'a_t': nec[len(nec) - 1]['content']['title'],
        'n': nyy
    }
    return render_template('dmin.html', d = dts)

@a.route('/admin/news')
def nnww():
    bv = ''

@a.route('/admin/new')
def brkfbkerbfer():
    return render_template('new.html')
@a.route('/admin/add_galery')
def sdvjcv():
    return render_template('neg.html')

@a.route('/admin/db')
def u():
    ass = ldb()
    return ass
@a.route('/admin/Login', methods=['GET', 'POST'])
@a.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin'):
        return redirect('/admin')

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # LOGIN SEMENTARA (NANTI GANTI DB)
        if username == 'admin' and password == '12345':
            session.permanent = True
            session['admin'] = True
            session['username'] = username

            ua = request.headers.get('User-Agent', '')
            device_type = "Mobile" if "mobile" in ua.lower() else "Desktop"

            device_info = {
                "username": username,
                "ip": request.remote_addr,
                "user_agent": ua,
                "device_type": device_type,
                "login_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            login_devices.append(device_info)

            return redirect('/admin')

        return render_template('admin_login.html', error="Hayoloh salah!!!")

    return render_template('admin_login.html')

@a.route('/admin/login/recent')
def admin_login_recent():
    if not session.get('admin'):
        return redirect('/admin/login')

    # terbaru di atas
    recent_logins = login_devices[::-1]

    return render_template(
        'admin_login_recent.html',
        logins=recent_logins
    )

@a.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect('/admin/login')

@a.route('/mf')
def ghk():
    return 'ID857-2765-4067'

@a.route('/galery/new', methods=['POST'])
def ddss():
    file = request.files['cover']
    if file.filename == '':
        return "Tidak ada file dipilih"
    rr = upclod(
        file,
        "galery",
        "image",
        code=1
    )
    nontif('news', 'Upload sukses', "Sukses menambahkan foto pada galery santri")
    db_galery.insert_one({'image': rr["secure_url"], 'title': request.form.get('judul')})
    return redirect('/galery')

@a.route('/upload-image', methods=['POST'])
def upload_image():
    file = request.files['image']
    res = upclod(file,'post_img','image', code=1)
    print('\n\n\n\nimage sukses di upload ke partikel\n\n\n\n\n')
    return jsonify({
        "url": res["secure_url"]
    })

@a.route('/news/new', methods=['post'])
def jbsrfu():
    file = request.files['cover']

    # Jika tidak ada file
    if file.filename == '':
        return "Tidak ada file dipilih"

    # Buat folder jika belum ada
    if not os.path.exists(a.config['UPLOAD_FOLDER']):
        os.makedirs(a.config['UPLOAD_FOLDER'])

    ext = file.filename.rsplit('.', 1)[1].lower()
    random_name = f"{uuid.uuid4().hex}.{ext}"
    idpage = uuid.uuid4().hex
    # Simpan file

    rr = upclod(
        file,
        "berita",
        "image",
        code=0
    )

    filepath = os.path.join(a.config['UPLOAD_FOLDER'], random_name)
    #file.save(filepath)
    ax = ldb()
    nontif('news', 'New Posted', f"Admin membuat berita : {request.form.get('judul')}")
    db_news.insert_one({'idpost': idpage,
               'view': 0,
              'content' :{
                  'title' : request.form.get('judul'),
                 'tag' : request.form.get('tag'),
                  'cover' : rr["secure_url"],
                  'id_cv' : rr["public_id"],
                'isi': request.form.get('isi'),
                'date': tanggal(),
                }
    })
    ax.append({'idpost': idpage,
               'view': 0,
              'content' :{
                  'title' : request.form.get('judul'),
                 'tag' : request.form.get('tag'),
                  'cover' : rr["secure_url"],
                  'id_cv' : rr["public_id"],
                'isi': request.form.get('isi'),
                'date': tanggal(),
                }
    })
    sdb(ax)
    return redirect('/news/'+idpage)

@a.route('/n_d', methods= ['post'])
def jsjhvddjvjsj():
    data = request.json
    nontif('user', 'Visited web', f"{data['platform']} Mengakses berita")
    return redirect('#')

#============================================== 
@a.route('/img/<nm>')
def ebgudgue(nm):
    return send_file('./static/'+nm)

@a.route('/assets/<path:nm>')
def abcggggg(nm):
    return send_from_directory('assets', nm)

@a.route('/pages/<path:nm>')
def abcggggssg(nm):
    return send_from_directory('pages', nm)

@a.route('/layouts/<path:nm>')
def abdc(nm):
    return send_from_directory('layouts', nm)

@a.route('/elements/<path:nm>')
def abcd(nm):
    return send_from_directory('elements', nm)



# dasboard item #
@a.route('/')
def re():
    global hit_pg1
    hit_pg1 += 1
    #b = ldb()
    docs = list(
    db_news.find()
    .sort("_id", -1)
    .limit(3)
    )
    nontif('news', 'Visited', "+1 Viewer index")
    ns = {
    'n1' : docs[0],
    'n2' : docs[1],
    'n3' : docs[2]
    }
    return render_template('ini.html', ns = ns, cplk = caplek)
@a.route('/berita')
def tottfvjdfjvf():
    global caplek
    ad = list(
    db_news.find()
    .sort("_id", -1)
    )

    bri = {}
    l = 1
    for i in ad:
        bri[l] = i
        l += 1
    print(bri)
    return render_template('listn.html', ber = ad, bra = bri, cplk = caplek)

@a.route('/public/<id>')
def yas(id):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FOTO_DIR = os.path.join(BASE_DIR, "bahan ex foto")
    return send_from_directory(FOTO_DIR, id)
    #return send_file('/bahan ex foto/'+id)

#    nav item  #
@a.route('/news')
def nss():
    return render_template('news.html')

@a.route('/news/<idps>')
def nssdd(idps):
    global hit_pg1
    hit_pg1 += 1
    docs = list(
    db_news.find()
    .sort("_id", -1)
    .limit(3)
    )
    totol = list(
    db_news.find()
    .sort("_id", -1)
    )
    print(docs)
    ns = {
    'n1' : docs[0],
    'n2' : docs[1],
    'n3' : docs[2]
    }
    return render_template('news.html', dt = totol[get_index(idps)]['content'], ns = ns, cplk = caplek, n = nontif)


#  profile 
@a.route('/profile/visi-misi')
def yayaya():
    global hit_pg1
    hit_pg1 += 1
    return render_template('visi.html')

@a.route('/profile/sejarah')
def yayayjgega():
    global hit_pg1
    hit_pg1 += 1
    return render_template('sejarah.html')

@a.route('/profile/struktur')
def yayayjgdhdega():
    global hit_pg1
    hit_pg1 += 1
    return render_template('struktur.html')

# pendidikan nav
@a.route('/pendidikan/misriu')
def yagega():
    global hit_pg1
    hit_pg1 += 1
    return render_template('misriu.html')

@a.route('/pendidikan/formal')
def yagdega():
    global hit_pg1
    hit_pg1 += 1
    return render_template('formal.html')

#galery
@a.route('/galery')
def evfcrv():
    ga = list(
    db_galery.find({}, {"_id": 0})
        .sort("created_at", -1)
)
    return render_template('galery.html', data=ga)

@a.route('/ppdb')
def yodfc():
    return redirect(" https://forms.gle/EqHVxx1J9DeZnHZh7")
#####
#eror 404
@a.errorhandler(404)
def page_not_found(e):
    return render_template('mainten.html'), 404











