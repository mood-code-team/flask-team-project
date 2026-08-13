/** Mood Code 공통 JS */
/** 검색 패널 열기/닫기, 사이드 메뉴, 뉴스레터, 1:1 상담 버튼 */

function bootMain() {
  document.querySelectorAll(".flash").forEach((el) => {
    setTimeout(() => {
      el.style.opacity = "0";
      el.style.transform = "translateX(100%)";
      setTimeout(() => el.remove(), 300);
    }, 4000);
  });

  initSearchPanel();
  initSideMenu();
  initFooterNewsletter();
  initFloatingActions();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", bootMain);
} else {
  bootMain();
}

/** 푸터 뉴스레터 — UI만 (백엔드 연동 전) */
function initFooterNewsletter() {
  const form = document.getElementById("footer-newsletter-form");
  if (!form) return;

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const email = form.querySelector('input[type="email"]');
    if (!email?.value.trim()) {
      email?.focus();
      return;
    }
    alert("구독 신청이 접수되었습니다. (데모)");
    form.reset();
  });
}

/** 검색 패널 */
function initSearchPanel() {
  const toggle = document.getElementById("search-toggle");
  const panel = document.getElementById("search-panel");
  const overlay = document.getElementById("search-panel-overlay");
  const closeBtn = document.getElementById("search-panel-close");
  const input = document.getElementById("search-input");
  const chips = document.querySelectorAll(".search-chip");

  if (!toggle || !panel || !overlay || !input) return;

  function openSearch() {
    panel.classList.add("is-open");
    panel.setAttribute("aria-hidden", "false");
    overlay.hidden = false;
    requestAnimationFrame(() => overlay.classList.add("is-visible"));
    toggle.setAttribute("aria-expanded", "true");
    document.body.classList.add("search-panel-open");
    setTimeout(() => input.focus(), 350);
  }

  function closeSearch() {
    panel.classList.remove("is-open");
    panel.setAttribute("aria-hidden", "true");
    overlay.classList.remove("is-visible");
    toggle.setAttribute("aria-expanded", "false");
    document.body.classList.remove("search-panel-open");
    setTimeout(() => { overlay.hidden = true; }, 300);
  }

  toggle.addEventListener("click", () => {
    if (panel.classList.contains("is-open")) {
      closeSearch();
    } else {
      openSearch();
    }
  });

  closeBtn?.addEventListener("click", closeSearch);
  overlay.addEventListener("click", closeSearch);

  chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      const keyword = chip.dataset.keyword || "";
      input.value = keyword;
      if (keyword && input.form) {
        input.form.submit();
      } else {
        input.focus();
      }
    });
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && panel.classList.contains("is-open")) {
      closeSearch();
    }
  });
}

/** 사이드 메뉴 (햄버거) */
function initSideMenu() {
  const menuToggle = document.querySelector(".menu-toggle");
  const menuClose = document.getElementById("side-menu-close");
  const sideMenu = document.getElementById("side-menu");
  const overlay = document.getElementById("side-menu-overlay");

  if (!menuToggle || !sideMenu || !overlay) return;

  function openMenu() {
    sideMenu.classList.add("is-open");
    sideMenu.setAttribute("aria-hidden", "false");
    overlay.hidden = false;
    requestAnimationFrame(() => overlay.classList.add("is-visible"));
    menuToggle.setAttribute("aria-expanded", "true");
    document.body.classList.add("side-menu-open");
  }

  function closeMenu() {
    sideMenu.classList.remove("is-open");
    sideMenu.setAttribute("aria-hidden", "true");
    overlay.classList.remove("is-visible");
    menuToggle.setAttribute("aria-expanded", "false");
    document.body.classList.remove("side-menu-open");
    setTimeout(() => { overlay.hidden = true; }, 300);
  }

  menuToggle.addEventListener("click", openMenu);
  menuClose?.addEventListener("click", closeMenu);
  overlay.addEventListener("click", closeMenu);

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && sideMenu.classList.contains("is-open")) {
      closeMenu();
    }
  });
}

/** 플로팅 버튼 — 고객센터 (TOP 스크롤은 scroll-top.js) */
function initFloatingActions() {
  const chatBtn = document.getElementById("chat-launcher-btn");

  chatBtn?.addEventListener("click", () => {
    const centerUrl = chatBtn.dataset.chatUrl;
    if (centerUrl) {
      window.location.href = centerUrl;
    }
  });
}


/* 메인페이지 — 스크롤하면 상단 회원가입 프로모션 숨김 */
(function () {
  "use strict";

  function initHomePromoScroll() {
    const body = document.body;

    // 메인페이지에서만 실행
    if (!body.classList.contains("page-home")) {
      return;
    }

    function updatePromo() {
      if (window.scrollY > 20) {
        body.classList.add("is-promo-hidden");
      } else {
        body.classList.remove("is-promo-hidden");
      }
    }

    window.addEventListener("scroll", updatePromo, { passive: true });

    updatePromo();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initHomePromoScroll);
  } else {
    initHomePromoScroll();
  }
})();