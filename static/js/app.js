/**
 * app.js — SmartDocs Sample Generator frontend logic
 */

(function () {
  "use strict";

  const typeGrid = document.getElementById("typeGrid");
  const selectAllBtn = document.getElementById("selectAllBtn");
  const generateBtn = document.getElementById("generateBtn");
  const btnText = document.getElementById("btnText");
  const btnSpinner = document.getElementById("btnSpinner");
  const errorBanner = document.getElementById("errorBanner");

  // ── Checkbox / card toggle ────────────────────────────────────────────────

  function getCheckboxes() {
    return Array.from(typeGrid.querySelectorAll("input[type='checkbox']"));
  }

  function updateCard(checkbox) {
    const type = checkbox.value;
    const card = document.getElementById("card-" + type);
    const chip = checkbox.closest(".type-chip");
    if (!card) return;

    if (checkbox.checked) {
      card.style.display = "block";
      chip.classList.add("checked");
    } else {
      card.style.display = "none";
      chip.classList.remove("checked");
      clearCard(card);
    }
  }

  function clearCard(card) {
    card.querySelectorAll("input[type='text'], input[type='number']").forEach((el) => {
      el.value = "";
      clearFieldError(el);
    });
    card.querySelectorAll("select").forEach((el) => {
      el.selectedIndex = 0;
      clearFieldError(el);
    });
    card.querySelectorAll("input[type='checkbox']").forEach((el) => {
      el.checked = false;
    });
  }

  function updateGenerateButton() {
    const anyChecked = getCheckboxes().some((cb) => cb.checked);
    generateBtn.disabled = !anyChecked;
  }

  typeGrid.addEventListener("change", (e) => {
    if (e.target.type === "checkbox") {
      updateCard(e.target);
      updateGenerateButton();
      const allChecked = getCheckboxes().every((cb) => cb.checked);
      selectAllBtn.textContent = allChecked ? "Deselect All" : "Select All";
    }
  });

  selectAllBtn.addEventListener("click", () => {
    const checkboxes = getCheckboxes();
    const allChecked = checkboxes.every((cb) => cb.checked);
    checkboxes.forEach((cb) => {
      cb.checked = !allChecked;
      updateCard(cb);
    });
    selectAllBtn.textContent = allChecked ? "Select All" : "Deselect All";
    updateGenerateButton();
  });

  // ── Inline field error helpers ────────────────────────────────────────────

  function setFieldError(el, msg) {
    el.classList.add("field-error");
    let hint = el.parentElement.querySelector(".field-error-msg");
    if (!hint) {
      hint = document.createElement("span");
      hint.className = "field-error-msg";
      el.parentElement.appendChild(hint);
    }
    hint.textContent = msg;
  }

  function clearFieldError(el) {
    el.classList.remove("field-error");
    const hint = el.parentElement.querySelector(".field-error-msg");
    if (hint) hint.remove();
  }

  // ── Real-time clamping for number inputs ──────────────────────────────────

  document.getElementById("cards").addEventListener("input", (e) => {
    const el = e.target;
    if (el.type !== "number" || !el.hasAttribute("data-clamp")) return;

    clearFieldError(el);

    const raw = el.value;
    if (raw === "" || raw === "-") return;

    const val = parseFloat(raw);
    if (isNaN(val)) return;

    const max = el.max !== "" ? parseFloat(el.max) : null;
    const min = el.min !== "" ? parseFloat(el.min) : null;

    if (max !== null && val > max) {
      el.value = max;
      setFieldError(el, `Maximum value is ${Number(max).toLocaleString()}`);
      // Clear the hint after 2 seconds
      setTimeout(() => clearFieldError(el), 2000);
    } else if (min !== null && val < 0) {
      // Block negative numbers immediately
      el.value = "";
    }
  });

  // ── Build request payload ─────────────────────────────────────────────────

  // ── Validation ────────────────────────────────────────────────────────────

  function validateCards() {
    const errors = [];

    // Clear all existing field errors first
    document.querySelectorAll(".field-error").forEach((el) => clearFieldError(el));

    getCheckboxes().forEach((cb) => {
      if (!cb.checked) return;
      const type = cb.value;
      const card = document.getElementById("card-" + type);
      if (!card) return;

      const label = type.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

      card.querySelectorAll("[data-field]").forEach((el) => {
        const field = el.dataset.field;
        const fieldLabel = field.replace(/_/g, " ");

        if (el.type === "number") {
          const typed = el.valueAsNumber;
          const hasValue = el.value !== "";
          const min = el.min !== "" ? parseFloat(el.min) : null;
          const max = el.max !== "" ? parseFloat(el.max) : null;

          if (field === "count") return; // select, always valid

          if (!hasValue) return; // optional field, skip if empty

          if (isNaN(typed)) {
            const msg = `Must be a valid number.`;
            errors.push(`${label}: "${fieldLabel}" must be a valid number.`);
            setFieldError(el, msg);
            return;
          }
          if (min !== null && typed < min) {
            const msg = `Minimum value is ${min}.`;
            errors.push(`${label}: "${fieldLabel}" must be at least ${min}.`);
            setFieldError(el, msg);
          }
          if (max !== null && typed > max) {
            const msg = `Maximum value is ${Number(max).toLocaleString()}.`;
            errors.push(`${label}: "${fieldLabel}" cannot exceed ${Number(max).toLocaleString()}.`);
            setFieldError(el, msg);
          }
        }

        if (el.type === "text" && el.maxLength > 0) {
          if (el.value.length > el.maxLength) {
            const msg = `Cannot exceed ${el.maxLength} characters.`;
            errors.push(`${label}: "${fieldLabel}" cannot exceed ${el.maxLength} characters.`);
            setFieldError(el, msg);
          }
        }
      });
    });

    return errors;
  }

  function readCard(card, type) {
    const spec = { type, count: 1, params: {}, instruction: "" };

    card.querySelectorAll("[data-field]").forEach((el) => {
      const field = el.dataset.field;

      if (field === "count") {
        spec.count = Math.max(1, Math.min(10, parseInt(el.value, 10) || 1));
        return;
      }

      if (field === "instruction") {
        spec.instruction = el.value.trim();
        return;
      }

      if (el.type === "checkbox") {
        if (el.checked) spec.params[field] = true;
        return;
      }

      const val = el.value.trim();
      if (!val) return;

      // Numeric fields — use valueAsNumber to read typed value accurately
      if (el.type === "number") {
        const num = el.valueAsNumber;
        if (!isNaN(num)) spec.params[field] = num;
      } else if (el.tagName === "SELECT" && el.dataset.numeric === "true") {
        // Select fields that carry numeric values (e.g. num_items, billing_days)
        const num = parseFloat(val);
        if (!isNaN(num)) spec.params[field] = num;
      } else {
        spec.params[field] = val;
      }
    });

    return spec;
  }

  function buildPayload() {
    const documents = [];
    getCheckboxes().forEach((cb) => {
      if (!cb.checked) return;
      const card = document.getElementById("card-" + cb.value);
      if (card) documents.push(readCard(card, cb.value));
    });
    return { documents };
  }

  // ── Generate & download ───────────────────────────────────────────────────

  function showError(msg) {
    errorBanner.textContent = msg;
    errorBanner.style.display = "block";
    errorBanner.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function hideError() {
    errorBanner.style.display = "none";
    errorBanner.textContent = "";
  }

  function setLoading(loading) {
    generateBtn.disabled = loading;
    btnText.textContent = loading ? "Generating…" : "Generate & Download ZIP";
    btnSpinner.style.display = loading ? "inline-block" : "none";
  }

  generateBtn.addEventListener("click", async () => {
    hideError();
    document.querySelectorAll(".field-error").forEach((el) => clearFieldError(el));

    const payload = buildPayload();
    if (payload.documents.length === 0) {
      showError("Please select at least one document type.");
      return;
    }

    const validationErrors = validateCards();
    if (validationErrors.length > 0) {
      showError(validationErrors.join("\n"));
      return;
    }

    setLoading(true);

    try {
      const response = await fetch("/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        let errMsg = `Server error (${response.status})`;
        try {
          const json = await response.json();
          if (json.error) errMsg = json.error;
        } catch (_) {
          // ignore JSON parse error
        }
        showError(errMsg);
        return;
      }

      // Trigger file download
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "smartdocs_samples.zip";
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      showError("Network error: " + err.message);
    } finally {
      setLoading(false);
      updateGenerateButton();
    }
  });
})();
