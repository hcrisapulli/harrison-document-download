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
      el.value = el.type === "number" && el.dataset.field === "count" ? "1" : "";
    });
    card.querySelectorAll("select").forEach((el) => {
      el.selectedIndex = 0;
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

  // ── Build request payload ─────────────────────────────────────────────────

  // ── Validation ────────────────────────────────────────────────────────────

  function validateCards() {
    const errors = [];

    getCheckboxes().forEach((cb) => {
      if (!cb.checked) return;
      const type = cb.value;
      const card = document.getElementById("card-" + type);
      if (!card) return;

      const label = type.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

      card.querySelectorAll("[data-field]").forEach((el) => {
        const field = el.dataset.field;

        if (el.type === "number") {
          const raw = el.value.trim();

          // Must not be empty for count
          if (field === "count") {
            const val = parseInt(raw, 10);
            if (!raw || isNaN(val) || val < 1) {
              errors.push(`${label}: "How many?" must be at least 1.`);
            } else if (val > parseInt(el.max, 10)) {
              errors.push(`${label}: "How many?" cannot exceed ${el.max}.`);
            }
            return;
          }

          // Optional numeric fields — only validate if something was entered
          if (!raw) return;
          const val = parseFloat(raw);
          if (isNaN(val)) {
            errors.push(`${label}: "${field.replace(/_/g, " ")}" must be a number.`);
            return;
          }
          if (el.min !== "" && val < parseFloat(el.min)) {
            errors.push(`${label}: "${field.replace(/_/g, " ")}" must be at least ${el.min}.`);
          }
          if (el.max !== "" && val > parseFloat(el.max)) {
            errors.push(`${label}: "${field.replace(/_/g, " ")}" cannot exceed ${Number(el.max).toLocaleString()}.`);
          }
        }

        if (el.type === "text" && el.maxLength > 0) {
          if (el.value.length > el.maxLength) {
            errors.push(`${label}: "${field.replace(/_/g, " ")}" cannot exceed ${el.maxLength} characters.`);
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
        spec.count = Math.max(1, Math.min(parseInt(el.max, 10) || 10, parseInt(el.value, 10) || 1));
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

      // Numeric fields
      if (el.type === "number") {
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
      // Re-enable button if types are still selected
      updateGenerateButton();
    }
  });
})();
