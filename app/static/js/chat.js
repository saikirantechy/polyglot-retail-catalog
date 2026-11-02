(function () {
  "use strict";

  const form = document.getElementById("chat-form");
  if (!form) {
    return;
  }

  const input = document.getElementById("chat-input");
  const log = document.getElementById("chat-log");
  const status = document.getElementById("chat-status");
  const notice = document.getElementById("chat-notice");
  const history = [];
  let busy = false;

  function userId() {
    const key = "polyglot-user";
    let value = window.localStorage.getItem(key);
    if (!value) {
      value = "web-" + Math.random().toString(36).slice(2, 10);
      window.localStorage.setItem(key, value);
    }
    return value;
  }

  function appendMessage(role, text) {
    const wrapper = document.createElement("div");
    wrapper.className = "message " + role;
    const body = document.createElement("div");
    body.className = "message-body";
    text.split("\n").forEach(function (line) {
      if (!line.trim()) {
        return;
      }
      const paragraph = document.createElement("p");
      paragraph.textContent = line;
      body.appendChild(paragraph);
    });
    wrapper.appendChild(body);
    log.appendChild(wrapper);
    log.scrollTop = log.scrollHeight;
    return wrapper;
  }

  function appendProducts(container, products) {
    if (!products || !products.length) {
      return;
    }
    const grid = document.createElement("div");
    grid.className = "message-products";
    products.forEach(function (product) {
      const link = document.createElement("a");
      link.className = "chat-product";
      link.href = "/product/" + encodeURIComponent(product.sku);

      const name = document.createElement("strong");
      name.textContent = product.name;

      const meta = document.createElement("span");
      meta.className = "meta";
      meta.textContent = product.sku + " | $" + Number(product.price).toFixed(2);

      const stock = document.createElement("span");
      stock.className = "meta";
      stock.textContent = product.in_stock
        ? product.stock + " in stock"
        : "Currently sold out";

      link.appendChild(name);
      link.appendChild(meta);
      link.appendChild(stock);
      grid.appendChild(link);
    });
    container.appendChild(grid);
  }

  function setStatus(text) {
    status.textContent = text;
  }

  function setBusy(value) {
    busy = value;
    form.querySelector("button").disabled = value;
    input.disabled = value;
  }

  async function send(message) {
    if (busy || !message.trim()) {
      return;
    }
    appendMessage("user", message);
    history.push({ role: "user", content: message });
    notice.hidden = true;
    setBusy(true);
    setStatus("Thinking across the catalog...");

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: message,
          user_id: userId(),
          history: history.slice(-12),
        }),
      });
      const payload = await response.json().catch(function () {
        return {};
      });
      if (!response.ok) {
        throw new Error(payload.error || "The assistant request failed");
      }

      const wrapper = appendMessage("assistant", payload.reply || "No reply was returned.");
      appendProducts(wrapper.querySelector(".message-body"), payload.products);

      if (payload.reply) {
        history.push({ role: "assistant", content: payload.reply });
      }
      if (payload.notice) {
        notice.textContent = payload.notice;
        notice.hidden = false;
      }
      if (payload.tool_calls && payload.tool_calls.length) {
        setStatus("Tools used: " + payload.tool_calls.join(", "));
      } else {
        setStatus("");
      }
    } catch (error) {
      appendMessage("assistant", error.message || "Something went wrong. Please try again.");
      setStatus("");
    } finally {
      setBusy(false);
      input.focus();
    }
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    const message = input.value.trim();
    if (!message) {
      return;
    }
    input.value = "";
    send(message);
  });

  input.addEventListener("keydown", function (event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      form.requestSubmit();
    }
  });

  document.querySelectorAll("[data-prompt]").forEach(function (button) {
    button.addEventListener("click", function () {
      const prompt = button.dataset.prompt;
      if (prompt) {
        send(prompt);
      }
    });
  });

  const initial = new URLSearchParams(window.location.search).get("q");
  if (initial) {
    input.value = initial;
    send(initial);
    input.value = "";
  }
})();
