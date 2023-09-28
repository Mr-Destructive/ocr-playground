import os
from pathlib import Path

from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import jinja2
from .config import Config
from .utils import (
    rotate_image,
    get_image_boxes,
    get_ocr_value_of_pdf,
    identify_columns,
    extract_rows_from_column,
)

app = Flask(__name__)
app.config.from_object(Config)
app.jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"),
)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


@app.route("/")
def index():
    template = "base.html"
    Template = app.jinja_env.get_template(template)
    return Template.render()


@app.route("/upload", methods=["POST", "GET"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            return jsonify({"error": "Missing file"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            return (
                jsonify({"message": f"File uploaded successfully as {filename}"}),
                200,
            )
        else:
            return jsonify({"error": "File type not allowed"}), 400
    else:
        template = "upload.html"
        Template = app.jinja_env.get_template(template)
        return Template.render()


@app.route("/file/<filename>", methods=["GET"])
def uploaded_file(filename):
    UPLOAD_FOLDER = "/home/meet/code/intern/doc/ocr-demo/api/uploads"
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/rotate", methods=["POST", "GET"])
def rotate():
    if request.method == "POST":
        print(request.form)
        if "file" not in request.files or "angle" not in request.form:
            return jsonify({"error": "Invalid request"}), 400

        file = request.files["file"]
        angle = int(request.form["angle"])

        if file and allowed_file(file.filename):
            filename = file.filename
            uploaded_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            output_file = f"rotated-{filename}"
            output_path = os.path.join(app.config["UPLOAD_FOLDER"], output_file)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            rotate_image(uploaded_path, output_path, angle)
            return (
                jsonify(
                    {
                        "message": f"Image rotated successfully",
                        "link": f"http://localhost:5000/file/{output_file}",
                    }
                ),
                200,
            )
        else:
            return jsonify({"error": "File type not allowed"}), 400
    else:
        template = "rotate.html"
        Template = app.jinja_env.get_template(template)
        return Template.render()


@app.route("/boxes", methods=["GET", "POST"])
def boxes():
    if request.method == "POST":
        if "file" not in request.files:
            return jsonify({"error": "Missing file"}), 400

        file = request.files["file"]

        if allowed_file(file.filename):
            filename = file.filename
            uploaded_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            output_file = f"boxes-{filename}"
            output_path = os.path.join(app.config["UPLOAD_FOLDER"], output_file)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            get_image_boxes(uploaded_path, output_path)
            return jsonify(
                {
                    "message": f"Boxes saved as {output_path}",
                    "link": f"http://localhost:5000/file/{output_file}",
                },
                200,
            )
        else:
            return jsonify({"error": "File type not allowed"}), 400
    else:
        template = "boxes.html"
        Template = app.jinja_env.get_template(template)
        return Template.render()


@app.route("/extract", methods=["GET", "POST"])
def extract_text():
    if request.method == "POST":
        if "file" not in request.files:
            return jsonify({"error": "Missing file"}), 400

        file = request.files["file"]
        if allowed_file(file.filename):
            filename = file.filename
            uploaded_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            if not Path(uploaded_path).exists():
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            ocr_values = get_ocr_value_of_pdf(uploaded_path)
            columns = identify_columns(ocr_values)
            desired_column_names = [request.form["columns"]] or ["Name"]
            desired_column = extract_rows_from_column(columns, desired_column_names)
            rows_in_desired_column = [item[4] for item in desired_column]
            if len(rows_in_desired_column) > 0:
                return jsonify({"rows": rows_in_desired_column})
            else:
                values = identify_columns(ocr_values)
                text = []
                for item in values:
                    item = item[0]
                    if len(item) > 0:
                        text.append(item[4])
                return jsonify({"columns": text})
    else:
        template = "text.html"
        Template = app.jinja_env.get_template(template)
        return Template.render()
