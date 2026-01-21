function getCSRFToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  return meta ? meta.getAttribute("content") : "";
}

function isoToDate(iso) {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(y, m - 1, d);
}

function dateToISO(dt) {
  const y = dt.getFullYear();
  const m = String(dt.getMonth() + 1).padStart(2, "0");
  const d = String(dt.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function eachDayInclusive(startISO, endISO) {
  const start = isoToDate(startISO);
  const end = isoToDate(endISO);
  const out = [];
  for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
    out.push(dateToISO(d));
  }
  return out;
}

document.addEventListener("DOMContentLoaded", () => {
  const dayButtons = Array.from(document.querySelectorAll(".day[data-date]"));
  const reserved = new Set(window.RESERVED_DATES || []);

  const checkInLabel = document.getElementById("checkInLabel");
  const checkOutLabel = document.getElementById("checkOutLabel");
  const confirmBtn = document.getElementById("confirmBtn");
  const clearBtn = document.getElementById("clearBtn");
  const errorBox = document.getElementById("errorBox");

  let startISO = null;
  let endISO = null;

  function showError(msg) {
    errorBox.hidden = false;
    errorBox.textContent = msg;
  }

  function clearError() {
    errorBox.hidden = true;
    errorBox.textContent = "";
  }

  function paintReserved() {
    dayButtons.forEach(btn => {
      const iso = btn.dataset.date;
      if (reserved.has(iso)) {
        btn.classList.add("reserved");
        btn.disabled = true; // clave: no seleccionar ocupados
      }
    });
  }

  function resetSelectionPaint() {
    dayButtons.forEach(btn => {
      btn.classList.remove("selected", "in-range");
    });
  }

  function paintSelection() {
    resetSelectionPaint();
    if (!startISO) return;

    const s = startISO;
    const e = endISO || startISO;

    const range = eachDayInclusive(s, e);
    range.forEach((iso, idx) => {
      const btn = dayButtons.find(b => b.dataset.date === iso);
      if (!btn) return;
      if (idx === 0 || idx === range.length - 1) btn.classList.add("selected");
      else btn.classList.add("in-range");
    });
  }

  function updateUI() {
    checkInLabel.textContent = startISO || "—";
    checkOutLabel.textContent = endISO || "—";
    confirmBtn.disabled = !(startISO && endISO);
  }

  function normalizeRange(a, b) {
    return (a <= b) ? [a, b] : [b, a];
  }

  function rangeHitsReserved(a, b) {
    const [s, e] = normalizeRange(a, b);
    const days = eachDayInclusive(s, e);
    return days.some(d => reserved.has(d));
  }

  async function createReserva(checkIn, checkOut) {
    const res = await fetch("/api/reservas/crear/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken(),
      },
      body: JSON.stringify({ check_in: checkIn, check_out: checkOut }),
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      throw new Error(data.error || "Error creando la reserva.");
    }
    return data.reserva;
  }

  // Inicial
  paintReserved();
  updateUI();

  dayButtons.forEach(btn => {
    btn.addEventListener("click", async () => {
      clearError();
      const iso = btn.dataset.date;

      if (reserved.has(iso)) {
        showError("Ese día ya está reservado.");
        return;
      }

      // Primer click: set check-in
      if (!startISO) {
        startISO = iso;
        endISO = null;
        paintSelection();
        updateUI();
        return;
      }

      // Segundo click: set check-out (ordenar rango)
      const [s, e] = normalizeRange(startISO, iso);

      // No permitas rangos que atraviesen reservados
      if (rangeHitsReserved(s, e)) {
        showError("El rango incluye días ya reservados. Elige otro rango.");
        return;
      }

      startISO = s;
      endISO = e;
      paintSelection();
      updateUI();
    });
  });

  clearBtn.addEventListener("click", () => {
    clearError();
    startISO = null;
    endISO = null;
    resetSelectionPaint();
    updateUI();
  });

  confirmBtn.addEventListener("click", async () => {
    clearError();
    if (!(startISO && endISO)) return;

    try {
      const reserva = await createReserva(startISO, endISO);

      // Marca reservado en UI
      eachDayInclusive(reserva.check_in, reserva.check_out).forEach(d => reserved.add(d));
      resetSelectionPaint();
      paintReserved();

      startISO = null;
      endISO = null;
      updateUI();
    } catch (err) {
      showError(err.message || "Error.");
    }
  });
});
