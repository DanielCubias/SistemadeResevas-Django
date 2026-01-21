function getCSRFToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  return meta ? meta.getAttribute("content") : "";
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".cancelBtn").forEach(btn => {
    btn.addEventListener("click", async () => {
      const card = btn.closest(".card");
      const id = card.dataset.id;

      const ok = confirm("¿Cancelar esta reserva?");
      if (!ok) return;

      const res = await fetch(`/api/reservas/eliminar/${id}/`, {
        method: "POST",
        headers: { "X-CSRFToken": getCSRFToken() }
      });

      if (res.ok) {
        card.remove();
      } else {
        alert("No se pudo cancelar.");
      }
    });
  });
});
