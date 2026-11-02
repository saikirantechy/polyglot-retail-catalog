(function () {
  "use strict";

  const toast = document.getElementById("toast");
  let toastTimer;

  function showToast(message) {
    if (!toast) {
      return;
    }
    toast.textContent = message;
    toast.classList.add("visible");
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(function () {
      toast.classList.remove("visible");
    }, 2600);
  }

  function userId() {
    const key = "polyglot-user";
    let value = window.localStorage.getItem(key);
    if (!value) {
      value = "web-" + Math.random().toString(36).slice(2, 10);
      window.localStorage.setItem(key, value);
    }
    return value;
  }

  async function recordInteraction(productId, eventType) {
    const response = await fetch("/api/interactions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: userId(),
        product_id: productId,
        event_type: eventType,
      }),
    });
    if (!response.ok) {
      const payload = await response.json().catch(function () {
        return {};
      });
      throw new Error(payload.error || "Request failed");
    }
    return response.json();
  }

  document.addEventListener("click", async function (event) {
    const button = event.target.closest("[data-track]");
    if (!button || button.disabled) {
      return;
    }
    const productId = button.dataset.productId;
    const eventType = button.dataset.eventType || "view";
    if (!productId) {
      return;
    }
    button.disabled = true;
    try {
      await recordInteraction(productId, eventType);
      showToast(eventType === "add_to_cart" ? "Added to cart" : "Saved to your interests");
    } catch (error) {
      showToast(error.message || "Could not record interaction");
    } finally {
      button.disabled = false;
    }
  });

  window.PolyglotStore = { showToast: showToast, userId: userId };
})();
