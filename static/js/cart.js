/**
 * Mood Code — 장바구니 드로어, 담기 확인 모달, 헤더 카운트
 */
(function () {
  "use strict";

  function formatPrice(value) {
    return Number(value).toLocaleString("ko-KR");
  }

  function updateHeaderCount(count) {
    document.querySelectorAll(".util-cart__count").forEach((el) => {
      el.textContent = String(count);
    });
    document.querySelectorAll(".util-cart").forEach((btn) => {
      btn.setAttribute("aria-label", `장바구니 ${count}개`);
    });
  }

  function renderDrawerItems(items) {
    const empty = document.getElementById("cart-drawer-empty");
    const list = document.getElementById("cart-drawer-list");
    if (!empty || !list) return;

    if (!items.length) {
      empty.hidden = false;
      list.hidden = true;
      list.innerHTML = "";
      return;
    }

    empty.hidden = true;
    list.hidden = false;
    list.innerHTML = items
      .map(
        (item) => `
        <li class="cart-drawer__item">
          <a href="/products/${item.slug}" class="cart-drawer__thumb">
            ${
              item.image_url
                ? `<img src="${item.image_url}" alt="${item.name}" loading="lazy">`
                : "<span>🏠</span>"
            }
          </a>
          <div class="cart-drawer__info">
            <p class="cart-drawer__name">${item.name}</p>
            <p class="cart-drawer__meta">${item.quantity}개 · ${formatPrice(item.subtotal)}원</p>
          </div>
        </li>`
      )
      .join("");
  }

  async function fetchCart() {
    const res = await fetch("/api/cart", { credentials: "same-origin" });
    if (!res.ok) return null;
    return res.json();
  }

  async function refreshCartUI() {
    const data = await fetchCart();
    if (!data) return;
    updateHeaderCount(data.count || 0);
    renderDrawerItems(data.items || []);
  }

  async function addToCart(slug, quantity = 1) {
    const qty = Math.max(parseInt(quantity, 10) || 1, 1);
    const res = await fetch("/api/cart/add", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ slug, quantity: qty }),
    });
    const data = await res.json();
    if (!res.ok || !data.ok) {
      alert(data.message || "장바구니에 담지 못했습니다.");
      return false;
    }
    updateHeaderCount(data.count || 0);
    renderDrawerItems(data.items || []);
    return true;
  }

  function initCartModal() {
    const overlay = document.getElementById("cart-modal-overlay");
    const modal = document.getElementById("cart-modal");
    const closeBtn = document.getElementById("cart-modal-close");
    if (!overlay || !modal) return;

    function openModal() {
      overlay.hidden = false;
      overlay.setAttribute("aria-hidden", "false");
      requestAnimationFrame(() => overlay.classList.add("is-visible"));
      document.body.classList.add("cart-modal-open");
      closeBtn?.focus();
    }

    function closeModal() {
      overlay.classList.remove("is-visible");
      overlay.setAttribute("aria-hidden", "true");
      document.body.classList.remove("cart-modal-open");
      setTimeout(() => {
        overlay.hidden = true;
      }, 280);
    }

    closeBtn?.addEventListener("click", closeModal);
    overlay.addEventListener("click", (event) => {
      if (event.target === overlay) closeModal();
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && overlay.classList.contains("is-visible")) {
        closeModal();
      }
    });

    window.MoodCodeCart.openAddedModal = openModal;
    window.MoodCodeCart.closeAddedModal = closeModal;
  }

  function initCartDrawer() {
    const toggle = document.getElementById("cart-toggle");
    const drawer = document.getElementById("cart-drawer");
    const overlay = document.getElementById("cart-drawer-overlay");
    const closeBtn = document.getElementById("cart-drawer-close");
    if (!toggle || !drawer || !overlay) return;

    function openDrawer() {
      drawer.classList.add("is-open");
      drawer.setAttribute("aria-hidden", "false");
      overlay.hidden = false;
      requestAnimationFrame(() => overlay.classList.add("is-visible"));
      toggle.setAttribute("aria-expanded", "true");
      document.body.classList.add("cart-drawer-open");
      refreshCartUI();
    }

    function closeDrawer() {
      drawer.classList.remove("is-open");
      drawer.setAttribute("aria-hidden", "true");
      overlay.classList.remove("is-visible");
      toggle.setAttribute("aria-expanded", "false");
      document.body.classList.remove("cart-drawer-open");
      setTimeout(() => {
        overlay.hidden = true;
      }, 300);
    }

    toggle.addEventListener("click", (e) => {
      e.preventDefault();
      if (drawer.classList.contains("is-open")) {
        closeDrawer();
      } else {
        openDrawer();
      }
    });

    closeBtn?.addEventListener("click", closeDrawer);
    overlay.addEventListener("click", closeDrawer);

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && drawer.classList.contains("is-open")) {
        closeDrawer();
      }
    });
  }

  function initAddToCartButtons() {
    document.querySelectorAll("[data-add-to-cart]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const slug = btn.dataset.addToCart;
        if (!slug || btn.disabled) return;

        btn.disabled = true;
        const qtyEl = document.querySelector("[data-product-qty]");
        const qty = qtyEl ? parseInt(qtyEl.value, 10) || 1 : 1;
        const ok = await addToCart(slug, qty);
        btn.disabled = false;

        if (ok) {
          window.MoodCodeCart?.openAddedModal?.();
        }
      });
    });
  }

  function init() {
    initCartDrawer();
    initAddToCartButtons();
    refreshCartUI();
  }

  const cartApi = {
    addToCart,
    refreshCartUI,
    updateHeaderCount,
    openAddedModal: null,
    closeAddedModal: null,
  };

  window.MoodCodeCart = cartApi;

  function bootstrap() {
    initCartModal();
    init();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bootstrap);
  } else {
    bootstrap();
  }
})();
