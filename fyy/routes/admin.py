from flask import Blueprint, render_template, request, redirect
from datetime import datetime
from models import orders

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

        orders.insert_one({
            "tracking_code": tracking_code,
            "created_at": datetime.utcnow(),
            "statuses": [
                {
                    "status": "Order Dibuat",
                    "time": datetime.utcnow()
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

    data = list(orders.find())

    return render_template(
        "admin/order_list.html",
        orders=data
    )


# ===========================
# Tambah Status
# ===========================
@admin_bp.route("/add-status/<tracking_code>", methods=["GET", "POST"])
def add_status(tracking_code):

    if request.method == "POST":

        status = request.form["status"]

        orders.update_one(
            {"tracking_code": tracking_code},
            {
                "$push": {
                    "statuses": {
                        "status": status,
                        "time": datetime.utcnow()
                    }
                }
            }
        )

        return redirect("/admin/orders")

    return render_template(
        "admin/add_status.html",
        tracking_code=tracking_code
    )