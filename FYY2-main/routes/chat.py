from flask import Blueprint, render_template, request, redirect, jsonify
from datetime import datetime
from models import orders
from zoneinfo import ZoneInfo
from models import orders, messages
from bson import ObjectId
chat_bp = Blueprint(
    "chat",
    __name__
)

@chat_bp.route("/chat/<tracking_code>", methods=["GET", "POST"])
def customer_chat(tracking_code):

    order = orders.find_one({
        "tracking_code": tracking_code
    })

    if not order:
        return "Order tidak ditemukan.", 404

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

            "sender": "customer",

            "message": message,

            "time": now,

            "read": False

        })

        return jsonify({

            "success": True,

            "message": message,

            "sender": "customer",

            "time": now.strftime("%H:%M")

        })

    chat_messages = list(

        messages.find({

            "tracking_code": tracking_code

        }).sort("time", 1)

    )

    return render_template(

        "chat/customer_chat.html",

        order=order,

        chat_messages=chat_messages

    )
@chat_bp.route("/chat-api/<tracking_code>")
def customer_chat_api(tracking_code):

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