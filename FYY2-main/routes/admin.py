from flask import Blueprint, render_template, request, redirect, jsonify
from datetime import datetime
from models import orders
from zoneinfo import ZoneInfo
from models import messages
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ===========================
# Buat Order
# ===========================
@admin_bp.route("/create", methods=["GET", "POST"])
def create():

    if request.method == "POST":

        tracking_code = request.form["tracking_code"]

        if orders.find_one({"tracking_code": tracking_code}):
            return render_template(
                "admin/create_order.html",
                message="Kode resi sudah digunakan."
            )

        customer_name = request.form["customer_name"]
        customer_phone = request.form["customer_phone"]

        product_name = request.form["product_name"]
        product_category = request.form["product_category"]
        product_price = int(request.form["product_price"])
        product_description = request.form["product_description"]

        deadline = request.form["deadline"]
        estimated_finish = request.form["estimated_finish"]

        payment_status = request.form["payment_status"]

        orders.insert_one({

            "tracking_code": tracking_code,
            "result_link": "",

            "max_revision": 2,
            "revision_count": 0,
            "revisions": [],

            "customer_name": customer_name,
            "customer_phone": customer_phone,

            "product_name": product_name,
            "product_category": product_category,
            "product_price": product_price,
            "product_description": product_description,

            "payment_status": payment_status,

            "deadline": deadline,
            "estimated_finish": estimated_finish,

            "progress": 0,

            "created_at": datetime.now(ZoneInfo("Asia/Jakarta")),

            "statuses": [

                {

                    "status": "Order Dibuat",

                    "time": datetime.now(ZoneInfo("Asia/Jakarta"))

                }

            ]

        })

        return render_template(
            "admin/create_order.html",
            message="Order berhasil dibuat."
        )

    return render_template("admin/create_order.html")


# ===========================
# Daftar Order
# ===========================
@admin_bp.route("/orders")
def order_list():

    data = list(
        orders.find().sort("created_at", -1)
    )

    total_order = orders.count_documents({})

    progress_order = orders.count_documents({
        "progress": {
            "$lt": 100
        }
    })

    selesai_order = orders.count_documents({
        "progress": 100
    })

    unread_chat = messages.count_documents({
        "sender": "customer",
        "read": False
    })

    return render_template(

        "admin/order_list.html",

        orders=data,

        total_order=total_order,

        progress_order=progress_order,

        selesai_order=selesai_order,

        unread_chat=unread_chat

    )


# ===========================
# Tambah Status
# ===========================
@admin_bp.route("/add-status/<tracking_code>", methods=["GET", "POST"])
def add_status(tracking_code):

    if request.method == "POST":

        status = request.form.get("status", "").strip()
        progress = int(request.form["progress"])

        update_data = {

            "$set": {

                "progress": progress,

                "updated_at": datetime.now(
                    ZoneInfo("Asia/Jakarta")
                )

            }

        }

        # Hanya tambah timeline jika status tidak kosong
        if status:

            update_data["$set"]["order_status"] = status

            update_data["$push"] = {

                "statuses": {

                    "status": status,

                    "time": datetime.now(
                        ZoneInfo("Asia/Jakarta")
                    )

                }

            }

        orders.update_one(

            {
                "tracking_code": tracking_code
            },

            update_data

        )

        return redirect(f"/admin/order/{tracking_code}")

    return render_template(

        "admin/add_status.html",

        tracking_code=tracking_code

    )
@admin_bp.route("/chats")
def chats():

    unread_pipeline = [
        {
            "$group": {
                "_id": "$tracking_code",
                "last_message": {"$last": "$message"},
                "last_sender": {"$last": "$sender"},
                "unread": {
                    "$sum": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$eq": ["$sender", "customer"]},
                                    {"$eq": ["$read", False]}
                                ]
                            },
                            1,
                            0
                        ]
                    }
                }
            }
        }
    ]

    chat_list = list(messages.aggregate(unread_pipeline))

    for chat in chat_list:

        order = orders.find_one({
            "tracking_code": chat["_id"]
        })

        chat["order"] = order

    return render_template(
        "admin/chat_list.html",
        chat_list=chat_list
    )
@admin_bp.route("/chat/<tracking_code>", methods=["GET", "POST"])
def admin_chat(tracking_code):

    order = orders.find_one({
        "tracking_code": tracking_code
    })

    if not order:
        return "Order tidak ditemukan", 404

    # ===========================
    # AJAX Kirim Pesan
    # ===========================
    if request.method == "POST":

        message = request.form.get("message", "").strip()

        if not message:
            return jsonify({
                "success": False
            })

        now = datetime.now(
            ZoneInfo("Asia/Jakarta")
        )

        messages.insert_one({

            "tracking_code": tracking_code,

            "sender": "admin",

            "message": message,

            "time": now,

            "read": True

        })

        return jsonify({

            "success": True,

            "message": message,

            "time": now.strftime("%H:%M"),

            "sender": "admin"

        })

    # ===========================
    # Tandai Dibaca
    # ===========================
    messages.update_many(

        {
            "tracking_code": tracking_code,
            "sender": "customer",
            "read": False
        },

        {
            "$set": {
                "read": True
            }
        }

    )

    chat_messages = list(

        messages.find({

            "tracking_code": tracking_code

        }).sort("time", 1)

    )

    return render_template(

        "admin/admin_chat.html",

        order=order,

        chat_messages=chat_messages

    )
@admin_bp.route("/order/<tracking_code>")
def order_detail(tracking_code):

    order = orders.find_one({
        "tracking_code": tracking_code
    })

    if not order:
        return "Order tidak ditemukan.",404

    return render_template(
        "admin/order_detail.html",
        order=order
    )
@admin_bp.route("/save-result/<tracking_code>", methods=["POST"])
def save_result(tracking_code):

    result_link = request.form["result_link"].strip()

    orders.update_one(

        {
            "tracking_code": tracking_code
        },

        {
            "$set": {

                "result_link": result_link,

                "updated_at": datetime.now(
                    ZoneInfo("Asia/Jakarta")
                )

            },

            "$push": {

                "statuses": {

                    "status": "Hasil telah diupload",

                    "time": datetime.now(
                        ZoneInfo("Asia/Jakarta")
                    )

                }

            }

        }

    )

    return redirect(f"/admin/order/{tracking_code}")
from bson import ObjectId

# ===========================
# API Chat Admin
# ===========================
@admin_bp.route("/chat-api/<tracking_code>")
def admin_chat_api(tracking_code):

    after = request.args.get("after")

    query = {
        "tracking_code": tracking_code
    }

    if after:

        query["_id"] = {

            "$gt": ObjectId(after)

        }

    chat_messages = list(

        messages.find(query).sort("_id", 1)

    )

    data = []

    for chat in chat_messages:

        data.append({

            "id": str(chat["_id"]),

            "sender": chat["sender"],

            "message": chat["message"],

            "time": chat["time"].strftime("%H:%M")

        })

    return jsonify(data)