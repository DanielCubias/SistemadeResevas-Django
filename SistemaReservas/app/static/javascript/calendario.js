(function () {
  const overlay = document.getElementById("modalOverlay");
  const modalText = document.getElementById("modalText");
  const btnClose = document.getElementById("btnClose");
  const btnReserve = document.getElementById("btnReserveRange");
  const btnCancel = document.getElementById("btnCancelRange");

  if (!overlay || !modalText || !btnClose || !btnReserve || !btnCancel) return;

  const year = Number(document.body.dataset.year);
  const month = Number(document.body.dataset.month);
  if (!Number.isFinite(year) || !Number.isFinite(month)) return;

  const csrf = document.querySelector('meta[name="csrf-token"]')?.content;
  const storageKey = `reservas_${year}_${month}`;

  function loadSelectedDays() {
    try {
      const v = JSON.parse(localStorage.getItem(storageKey));
      return Array.isArray(v) ? v.map(Number) : [];
    } catch {
      return [];
    }
  }

  function saveSelectedDays(days) {
    const uniq = Array.from(new Set(days.map(Number))).sort((a, b) => a - b);
    localStorage.setItem(storageKey, JSON.stringify(uniq));
  }

  function paintFromList(days) {
    const selected = new Set(days);
    document.querySelectorAll(".js-day").forEach((cell) => {
      const d = Number(cell.dataset.day);
      cell.classList.toggle("selected", selected.has(d));
    });
  }

  async function syncFromServer() {
    const res = await fetch(`/reservas/mes/?year=${year}&month=${month}`);
    if (!res.ok) return;
    const data = await res.json();
    if (!data.ok) return;
    paintFromList(data.days);
    saveSelectedDays(data.days); // opcional
  }

  function clearPreview() {
    document.querySelectorAll(".js-day").forEach((cell) => {
      cell.classList.remove("preview", "start", "end");
    });
  }

  function previewRange(from, to) {
    clearPreview();
    const a = Math.min(from, to);
    const b = Math.max(from, to);

    document.querySelectorAll(".js-day").forEach((cell) => {
      const d = Number(cell.dataset.day);
      if (d >= a && d <= b) cell.classList.add("preview");
      if (d === a) cell.classList.add("start");
      if (d === b) cell.classList.add("end");
    });
  }

  let startDay = null;
  let endDay = null;
  let pendingRange = null;

  function openModal(from, to) {
    const a = Math.min(from, to);
    const b = Math.max(from, to);
    pendingRange = { from: a, to: b };

    modalText.textContent =
      a === b
        ? `¿Qué quieres hacer con el día ${a}/${month}/${year}?`
        : `Has seleccionado del ${a}/${month}/${year} al ${b}/${month}/${year}. ¿Quieres reservar o cancelar ese rango?`;

    overlay.classList.remove("hidden");
  }

  function closeModal() {
    overlay.classList.add("hidden");
    pendingRange = null;
  }

  function resetSelection() {
    startDay = null;
    endDay = null;
    clearPreview();
  }

  async function postJSON(url, body) {
    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrf || "",
      },
      body: JSON.stringify(body),
    });

    let data = null;
    try { data = await res.json(); } catch {}
    return { res, data };
  }

  async function reserveRange(range) {
    if (!csrf) {
      alert("Falta CSRF token en el HTML (meta csrf-token).");
      return;
    }

    const { res, data } = await postJSON("/reservas/rango/", {
      year,
      month,
      from: range.from,
      to: range.to,
      hora_inicio: "09:00",
      hora_fin: "10:00",
    });

    if (!res.ok || !data?.ok) {
      alert("Error guardando en servidor");
      return;
    }

    await syncFromServer();
  }

  async function cancelRange(range) {
    if (!csrf) {
      alert("Falta CSRF token en el HTML (meta csrf-token).");
      return;
    }

    const { res, data } = await postJSON("/reservas/cancelar-rango/", {
      year,
      month,
      from: range.from,
      to: range.to,
      hora_inicio: "09:00",
      hora_fin: "10:00",
    });

    if (!res.ok || !data?.ok) {
      alert("Error cancelando en servidor");
      return;
    }

    await syncFromServer();
  }

  document.querySelectorAll(".js-day").forEach((cell) => {
    cell.addEventListener("click", () => {
      const d = Number(cell.dataset.day);

      if (startDay === null) {
        startDay = d;
        endDay = null;
        previewRange(startDay, startDay);
        return;
      }

      if (endDay === null) {
        endDay = d;
        previewRange(startDay, endDay);
        openModal(startDay, endDay);
        return;
      }

      startDay = d;
      endDay = null;
      previewRange(startDay, startDay);
    });

    cell.addEventListener("mouseenter", () => {
      if (startDay !== null && endDay === null) {
        previewRange(startDay, Number(cell.dataset.day));
      }
    });
  });

  btnReserve.addEventListener("click", async () => {
    if (!pendingRange) return;
    await reserveRange(pendingRange);
    closeModal();
    resetSelection();
  });

  btnCancel.addEventListener("click", async () => {
    if (!pendingRange) return;
    await cancelRange(pendingRange);
    closeModal();
    resetSelection();
  });

  btnClose.addEventListener("click", () => {
    closeModal();
    resetSelection();
  });

  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) {
      closeModal();
      resetSelection();
    }
  });

  // cargar reservas del mes desde BD y pintar
  syncFromServer();
})();
