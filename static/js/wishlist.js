/**
 * Mood Code — 위시리스트 담기, 확인 모달, 헤더·메뉴 카운트
 */
(function () {
  "use strict";

  function isLoggedIn() {
    return document.body.dataset.userLoggedIn === "true";
  }

  function currentPathQuery() {
    return window.location.pathname + window.location.search;
  }

  function registerUrl() {
    const base = document.body.dataset.registerUrl || "/register";
    return `${base}?next=${encodeURIComponent(currentPathQuery())}`;
  }

  function updateHeaderCount(count) {
    document.querySelectorAll(".util-wishlist__count").forEach((el) => {
      el.textContent = String(count);
    });
    document.querySelectorAll(".util-wishlist").forEach((link) => {
      link.classList.toggle("has-items", count > 0);
      link.setAttribute("aria-label", `위시리스트 ${count}개`);
    });
    document.querySelectorAll(".side-menu__wishlist-count").forEach((el) => {
      el.textContent = String(count);
    });
  }

  function updateToggleButtons(productId, inWishlist) {
    document.querySelectorAll(`[data-wishlist-toggle="${productId}"]`).forEach((btn) => {
      btn.classList.toggle("is-active", inWishlist);
      btn.setAttribute("aria-pressed", inWishlist ? "true" : "false");
      if (btn.dataset.labelAdd && btn.dataset.labelRemove) {
        btn.textContent = inWishlist ? btn.dataset.labelRemove : btn.dataset.labelAdd;
      } else if (btn.textContent.includes("위시리스트")) {
        btn.textContent = inWishlist ? "위시리스트 해제" : "위시리스트";
      }
    });
    document.querySelectorAll(`[data-wishlist-add="${productId}"]`).forEach((btn) => {
      btn.classList.toggle("is-active", inWishlist);
      btn.setAttribute("aria-pressed", inWishlist ? "true" : "false");
    });
  }

  async function fetchWishlist() {
    const res = await fetch("/api/wishlist", { credentials: "same-origin" });
    if (res.status === 401) return null;
    if (!res.ok) return null;
    return res.json();
  }

  async function refreshWishlistUI() {
    if (!isLoggedIn()) return;
    const data = await fetchWishlist();
    if (!data || !data.ok) return;
    updateHeaderCount(data.count || 0);
    (data.items || []).forEach((item) => updateToggleButtons(item.id, true));
  }

  function bindModal(overlay, closeBtn, onOpen) {
    if (!overlay) return { open: () => {}, close: () => {} };

    function openModal() {
      overlay.hidden = false;
      overlay.setAttribute("aria-hidden", "false");
      requestAnimationFrame(() => overlay.classList.add("is-visible"));
      document.body.classList.add("wishlist-modal-open");
      closeBtn?.focus();
      onOpen?.();
    }

    function closeModal() {
      overlay.classList.remove("is-visible");
      overlay.setAttribute("aria-hidden", "true");
      document.body.classList.remove("wishlist-modal-open");
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

    return { open: openModal, close: closeModal };
  }

  function initWishlistModal() {
    const overlay = document.getElementById("wishlist-modal-overlay");
    const closeBtn = document.getElementById("wishlist-modal-close");
    const modal = bindModal(overlay, closeBtn);
    window.MoodCodeWishlist = window.MoodCodeWishlist || {};
    window.MoodCodeWishlist.openAddedModal = modal.open;
    window.MoodCodeWishlist.closeAddedModal = modal.close;
  }

  function initWishlistSignupModal() {
    const overlay = document.getElementById("wishlist-signup-overlay");
    const closeBtn = document.getElementById("wishlist-signup-close");
    const registerLink = document.getElementById("wishlist-signup-register");
    const loginLink = document.getElementById("wishlist-signup-login");
    const modal = bindModal(overlay, closeBtn, () => {
      const next = encodeURIComponent(currentPathQuery());
      if (registerLink) registerLink.href = `${document.body.dataset.registerUrl || "/register"}?next=${next}`;
      if (loginLink) loginLink.href = `${document.body.dataset.loginUrl || "/login"}?next=${next}`;
    });

    document.querySelectorAll("[data-wishlist-guest]").forEach((el) => {
      el.addEventListener("click", (event) => {
        event.preventDefault();
        modal.open();
      });
    });

    window.MoodCodeWishlist = window.MoodCodeWishlist || {};
    window.MoodCodeWishlist.openSignupModal = modal.open;
  }

  function promptSignupForWishlist() {
    if (window.MoodCodeWishlist?.openSignupModal) {
      window.MoodCodeWishlist.openSignupModal();
      return true;
    }
    window.location.href = registerUrl();
    return true;
  }

  async function toggleWishlist(productId) {
    if (!isLoggedIn()) {
      promptSignupForWishlist();
      return null;
    }

    const res = await fetch("/api/wishlist/toggle", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: Number(productId) }),
    });
    const data = await res.json();

    if (res.status === 401) {
      promptSignupForWishlist();
      return null;
    }
    if (!res.ok || !data.ok) {
      alert(data.message || "위시리스트 처리에 실패했습니다.");
      return null;
    }

    updateHeaderCount(data.count || 0);
    updateToggleButtons(productId, data.in_wishlist);
    return data;
  }

  async function addToWishlist(productId) {
    if (!isLoggedIn()) {
      promptSignupForWishlist();
      return null;
    }

    const res = await fetch("/api/wishlist/add", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: Number(productId) }),
    });
    const data = await res.json();

    if (res.status === 401) {
      promptSignupForWishlist();
      return null;
    }
    if (!res.ok || !data.ok) {
      alert(data.message || "위시리스트에 담지 못했습니다.");
      return null;
    }

    updateHeaderCount(data.count || 0);
    updateToggleButtons(productId, true);
    return data;
  }

  function initWishlistButtons() {
    document.querySelectorAll("[data-wishlist-toggle]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const productId = btn.dataset.wishlistToggle;
        if (!productId || btn.disabled) return;

        btn.disabled = true;
        const data = await toggleWishlist(productId);
        btn.disabled = false;

        if (data?.in_wishlist) {
          window.MoodCodeWishlist?.openAddedModal?.();
        }
      });
    });

    document.querySelectorAll("[data-wishlist-add]").forEach((btn) => {
      btn.addEventListener("click", async (event) => {
        event.preventDefault();
        event.stopPropagation();

        const productId = btn.dataset.wishlistAdd;
        if (!productId || btn.disabled) return;

        if (!isLoggedIn()) {
          promptSignupForWishlist();
          return;
        }

        if (btn.classList.contains("is-active")) {
          const data = await toggleWishlist(productId);
          if (data && !data.in_wishlist) return;
          return;
        }

        btn.disabled = true;
        const data = await addToWishlist(productId);
        btn.disabled = false;

        if (data?.added !== false) {
          window.MoodCodeWishlist?.openAddedModal?.();
        }
      });
    });
  }

  function init() {
    initWishlistModal();
    initWishlistSignupModal();
    initWishlistButtons();
    refreshWishlistUI();
  }

  window.MoodCodeWishlist = {
    addToWishlist,
    toggleWishlist,
    refreshWishlistUI,
    updateHeaderCount,
    openAddedModal: null,
    closeAddedModal: null,
    openSignupModal: null,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
