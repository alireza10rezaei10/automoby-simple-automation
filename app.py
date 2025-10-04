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
    image_cropper,
    simple_watermark,
)
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
# image cropper -------------------
# ---------------------------------
@app.route("/image-cropper")
def cropper_main():
    return render_template_string(image_cropper.html_ui)


@app.route("/crop", methods=["POST"])
def crop():
    if "image" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["image"]
    buffer = image_cropper.place_subject_center_white_bg_full(file.read())
    return send_file(
        buffer, mimetype="image/jpeg", as_attachment=False, download_name="cropped.jpg"
    )


# ---------------------------------
# simple watermark ----------------
# ---------------------------------
@app.route("/simple-watermark")
def simple_watermark_main():
    return render_template_string(simple_watermark.html_ui)


@app.route("/apply-box", methods=["POST"])
@app.route("/apply-box", methods=["POST"])
def apply_box():
    if "image" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["image"]
    filename = file.filename  # نام اصلی فایل
    x1 = int(request.form.get("x1", 0))
    y1 = int(request.form.get("y1", 0))
    x2 = int(request.form.get("x2", 0))
    y2 = int(request.form.get("y2", 0))
    color = request.form.get("color", "#ff0000")

    buffer = simple_watermark.apply_colored_box(file.read(), x1, y1, x2, y2, color)

    # تشخیص فرمت برای mimetype
    img_out = Image.open(buffer)
    format_in = img_out.format
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype=f"image/{format_in.lower()}",
        as_attachment=False,
        download_name=filename,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=False, threaded=True)
