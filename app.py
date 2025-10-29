from flask import (
    Flask,
    render_template_string,
    Response,
    request,
    send_file,
    jsonify,
)
from apps import (
    form_to_json,
    main,
    digi_attributes_scraping,
    photoshop,
)
from apps.emami_ghafari_quantity_syncer import main as emami_ghafari_quantity_syncer
import cv2
import numpy as np
from PIL import Image

app = Flask(__name__)


# ---------------------------------
# main ----------------------------
# ---------------------------------
@app.route("/")
def home():
    return main.main_html


# ---------------------------------
# form to json --------------------
# ---------------------------------
@app.route("/form-to-json")
def form_to_json_page():
    return form_to_json.form_to_json_html


# ---------------------------------
# attributes scraping -------------
# ---------------------------------
@app.route("/attributes-scraping")
def index():
    return render_template_string(digi_attributes_scraping.html)


@app.route("/scrape")
def scrape():
    category_url = request.args.get("category_url")
    return Response(
        digi_attributes_scraping.generate(category_url), mimetype="text/event-stream"
    )


# ---------------------------------
# photoshop -----------------------
# ---------------------------------
@app.route("/photoshop")
def photoshop_main():
    return render_template_string(photoshop.html_ui)


# ---------------------------------
# emami ghafari syncer -------------
# ---------------------------------
@app.route("/emami-ghafari-sync")
def emami_sync_page():
    return render_template_string(emami_ghafari_quantity_syncer.main_html)


@app.route("/emami-ghafari-sync-run")
def emami_sync_run():
    return Response(
        emami_ghafari_quantity_syncer.generate(), mimetype="text/event-stream"
    )


@app.route("/apply-all", methods=["POST"])
def apply_all():
    if "image" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["image"]
    filename = file.filename
    image_data = file.read()

    crop_coords = None
    if all(key in request.form for key in ["x1_c", "y1_c", "x2_c", "y2_c"]):
        crop_coords = (
            int(request.form["x1_c"]),
            int(request.form["y1_c"]),
            int(request.form["x2_c"]),
            int(request.form["y2_c"]),
        )

    watermark_coords = None
    if all(key in request.form for key in ["x1_w", "y1_w", "x2_w", "y2_w", "color"]):
        watermark_coords = (
            int(request.form["x1_w"]),
            int(request.form["y1_w"]),
            int(request.form["x2_w"]),
            int(request.form["y2_w"]),
        )
        color = request.form["color"]

    buffer = photoshop.apply_combined(
        image_data,
        crop_coords,
        watermark_coords,
        color if watermark_coords else "#ffffff",
    )

    return send_file(
        buffer,
        mimetype="image/jpeg",
        as_attachment=False,
        download_name=filename,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=False, threaded=True)
