from flask import (
    Flask,
    render_template_string,
    Response,
    request,
    send_file,
    jsonify,
)
from apps import form_to_json, main, digi_attributes_scraping, image_cropper

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=False, threaded=True)
