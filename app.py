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
import instruction_parser

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB max request

# Field limits (must match frontend)
_TEXT_MAX_LEN = 80       # longest allowed text field (address)
_INSTRUCTION_MAX_LEN = 200
_NUMERIC_LIMITS = {
    "subtotal":          (1, 9_999_999),
    "amount_due":        (1, 9_999_999),
    "opening_balance":   (1, 9_999_999),
    "usage_amount":      (1, 99_999),
    "property_value":    (1, 99_999_999),
    "total_rates":       (1, 999_999),
    "purchase_price":    (1, 99_999_999),
    "deposit_paid":      (1, 999_999),
    "quantity":          (1, 9_999_999),
    "price":             (0.01, 99_999),
    "shares":            (1, 9_999_999),
    "rate_per_share":    (0.0001, 99_999),
    "franking_percentage": (0, 100),
    "billing_days":      (1, 365),
    "num_items":         (1, 10),
    "num_transactions":  (1, 50),
}


@app.get("/")
def index():
    return render_template("index.html", doc_types=generators.SUPPORTED_TYPES)


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/generate")
def generate():
    body = request.get_json(force=False, silent=False)
    if body is None:
        return jsonify({"error": "Request body must be valid JSON."}), 400
    if "documents" not in body:
        return jsonify({"error": "Request body must contain a 'documents' list."}), 400

    documents = body["documents"]
    if not isinstance(documents, list) or len(documents) == 0:
        return jsonify({"error": "'documents' must be a non-empty list."}), 400

    zip_buffer = io.BytesIO()

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for spec in documents:
                    doc_type = spec.get("type", "")
                    if doc_type not in generators.SUPPORTED_TYPES:
                        return jsonify({"error": f"Unknown document type: {doc_type!r}"}), 400

                    count = int(spec.get("count") or 1)
                    count = max(1, min(10, count))

                    # Validate and sanitise params
                    form_params = spec.get("params") or {}
                    validation_error = _validate_params(doc_type, form_params)
                    if validation_error:
                        return jsonify({"error": validation_error}), 400

                    # Validate instruction length
                    instruction_text = spec.get("instruction") or ""
                    if len(instruction_text) > _INSTRUCTION_MAX_LEN:
                        return jsonify({"error": f"Instruction text for '{doc_type}' exceeds {_INSTRUCTION_MAX_LEN} characters."}), 400

                    parsed = instruction_parser.parse(instruction_text)
                    params = instruction_parser.merge(form_params, parsed)

                    for i in range(count):
                        filename = f"{doc_type}_{i + 1:03d}.pdf"
                        filepath = os.path.join(tmpdir, filename)
                        try:
                            generators.dispatch(doc_type, params, filepath)
                        except (ValueError, TypeError) as exc:
                            return jsonify({"error": f"Failed to generate {doc_type}: {exc}"}), 400
                        zf.write(filepath, arcname=filename)

    except Exception as exc:
        app.logger.exception("PDF generation failed")
        return jsonify({"error": f"Generation failed: {exc}"}), 500

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name="smartdocs_samples.zip",
    )


def _validate_params(doc_type: str, params: dict):
    """Validate params against known limits. Returns error string or None."""
    for key, value in params.items():
        # Text field length check
        if isinstance(value, str):
            max_len = 60 if key not in ("property_address",) else 80
            if len(value) > max_len:
                return f"'{key}' exceeds maximum length of {max_len} characters."

        # Numeric range check
        if isinstance(value, (int, float)) and key in _NUMERIC_LIMITS:
            lo, hi = _NUMERIC_LIMITS[key]
            if value < lo or value > hi:
                return f"'{key}' value {value} is outside allowed range ({lo}–{hi:,})."

    return None


if __name__ == "__main__":
    app.run(debug=True, port=5000)
