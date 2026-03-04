"""
app.py
Flask web application for generating SmartDocs sample PDFs.
"""

import io
import os
import tempfile
import zipfile

from flask import Flask, jsonify, render_template, request, send_file

import generators
import ai_instruction_parser

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB max request


@app.get("/")
def index():
    return render_template("index.html", doc_types=generators.SUPPORTED_TYPES)


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/generate")
def generate():
    body = request.get_json(silent=True)
    if not body or "documents" not in body:
        return jsonify({"error": "Request body must contain a 'documents' list."}), 400

    documents = body["documents"]
    if not isinstance(documents, list) or len(documents) == 0:
        return jsonify({"error": "'documents' must be a non-empty list."}), 400

    instructions_parts = []
    zip_buffer = io.BytesIO()

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for spec in documents:
                    doc_type = spec.get("type", "")
                    if doc_type not in generators.SUPPORTED_TYPES:
                        return jsonify({"error": f"Unknown document type: {doc_type!r}"}), 400

                    count = int(spec.get("count") or 1)
                    if count < 1:
                        count = 1
                    if count > 20:
                        count = 20

                    # Merge explicit params with instruction-parsed params
                    form_params = spec.get("params") or {}
                    instruction_text = spec.get("instruction") or ""

                    # Get API key from environment variable (optional)
                    api_key = os.environ.get("ANTHROPIC_API_KEY")

                    parsed = ai_instruction_parser.parse(instruction_text, doc_type, api_key)
                    params = ai_instruction_parser.merge(form_params, parsed)

                    if instruction_text:
                        instructions_parts.append(
                            f"[{doc_type}] ({count} file(s)): {instruction_text}"
                        )

                    for i in range(count):
                        filename = f"{doc_type}_{i + 1:03d}.pdf"
                        filepath = os.path.join(tmpdir, filename)
                        generators.dispatch(doc_type, params, filepath)
                        zf.write(filepath, arcname=filename)

                if instructions_parts:
                    readme = "SmartDocs Sample Generator — Instructions\n"
                    readme += "=" * 42 + "\n\n"
                    readme += "\n".join(instructions_parts) + "\n"
                    zf.writestr("INSTRUCTIONS.txt", readme)

    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:  # noqa: BLE001
        app.logger.exception("PDF generation failed")
        return jsonify({"error": f"Generation failed: {exc}"}), 500

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name="smartdocs_samples.zip",
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
