from flask import Blueprint, render_template, request, redirect
from models import orders
from datetime import datetime
from zoneinfo import ZoneInfo

tracking_bp = Blueprint("tracking", __name__)

@tracking_bp.route('/')
def bsdchdf():
    return render_template('landing.html')

@tracking_bp.route("/tracking", methods=["GET", "POST"])
def tracking():

    if request.method == "POST":

        tracking_code = request.form["tracking_code"]

        order = orders.find_one({
            "tracking_code": tracking_code
        })

        if not order:
            return render_template(
                "tracking/search.html",
                message="Resi tidak ditemukan."
            )

        return render_template(
            "tracking/result.html",
            order=order
        )

    return render_template("tracking/search.html")
@tracking_bp.route("/revision/<tracking_code>", methods=["POST"])
def send_revision(tracking_code):

    order = orders.find_one({
        "tracking_code": tracking_code
    })

    if not order:
        return "Order tidak ditemukan",404

    if order["revision_count"] >= order["max_revision"]:
        return redirect(f"/tracking/{tracking_code}")

    message = request.form["revision"].strip()

    if message:

        orders.update_one(

            {
                "tracking_code": tracking_code
            },

            {

                "$push":{

                    "revisions":{

                        "message":message,

                        "status":"Pending",

                        "time":datetime.now(
                            ZoneInfo("Asia/Jakarta")
                        )

                    }

                },

                "$inc":{

                    "revision_count":1

                }

            }

        )

    return redirect(f"/tracking/{tracking_code}")