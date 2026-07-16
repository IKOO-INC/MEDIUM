from flask import Blueprint, render_template, request, redirect
from models import orders

tracking_bp = Blueprint("tracking", __name__)

@tracking_bp.route('/')
def bsdchdf():
    return redirect('/tracking')

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