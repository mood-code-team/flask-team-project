/**
 * 인증 페이지 — 아이디 저장, 인증 방식 토글, 약관 전체 동의
 */
(function () {
  "use strict";

  const STORAGE_KEY = "moodcode_saved_login_id";

  function initRememberLoginId() {
    const input = document.getElementById("login-id");
    const checkbox = document.querySelector(".auth-remember input[name='remember']");
    const form = document.querySelector(".auth-form");
    if (!input || !checkbox || !form) return;

    const saved = localStorage.getItem(STORAGE_KEY);
    const nextParam = new URLSearchParams(window.location.search).get("next") || "";
    const isAdminLogin = nextParam.startsWith("/admin");
    if (saved && !isAdminLogin) {
      input.value = saved;
      checkbox.checked = true;
    }

    form.addEventListener("submit", () => {
      if (checkbox.checked) {
        localStorage.setItem(STORAGE_KEY, input.value.trim());
      } else {
        localStorage.removeItem(STORAGE_KEY);
      }
    });
  }

  function initVerifyToggle() {
    const form = document.querySelector(".auth-form");
    if (!form) return;

    const radios = form.querySelectorAll("[data-verify-toggle]");
    const contactInput = form.querySelector("[name='contact']");
    const contactLabel = form.querySelector("[data-contact-label]");
    if (!radios.length || !contactInput || !contactLabel) return;

    const presets = {
      email: { label: "이메일", placeholder: "이메일을 입력하세요", type: "email" },
      phone: { label: "휴대폰 번호", placeholder: "010-0000-0000", type: "tel" },
    };

    function apply(method) {
      const preset = presets[method] || presets.email;
      contactLabel.textContent = preset.label;
      contactInput.placeholder = preset.placeholder;
      contactInput.type = preset.type;
    }

    radios.forEach((radio) => {
      radio.addEventListener("change", () => {
        if (radio.checked) apply(radio.value);
      });
    });

    const checked = form.querySelector("[data-verify-toggle]:checked");
    apply(checked ? checked.value : "email");
  }

  function initAgreeAll() {
    const agreeAll = document.getElementById("agree-all");
    const agreementSection = document.getElementById("register-agreements");
    if (!agreeAll || !agreementSection) return;

    const checks = agreementSection.querySelectorAll(".auth-check input[type='checkbox']");
    agreeAll.addEventListener("change", () => {
      checks.forEach((box) => {
        box.checked = agreeAll.checked;
      });
    });

    checks.forEach((box) => {
      box.addEventListener("change", () => {
        agreeAll.checked = Array.from(checks).every((item) => item.checked);
      });
    });
  }

  function initRegisterForm() {
    const form = document.getElementById("register-form");
    const usernameInput = document.getElementById("reg-username");
    const emailInput = document.getElementById("reg-email");
    if (!form || !usernameInput) return;

    usernameInput.addEventListener("input", () => {
      usernameInput.value = usernameInput.value.toLowerCase().replace(/[^a-z0-9_]/g, "");
    });

    form.addEventListener("submit", () => {
        usernameInput.value = usernameInput.value.trim().toLowerCase();
      if (emailInput) {
        emailInput.value = emailInput.value.trim().toLowerCase();
      }
    });
  }

  function initFindPasswordUsername() {
    const usernameInput = document.getElementById("find-pw-username");
    if (!usernameInput) return;
    usernameInput.addEventListener("blur", () => {
      usernameInput.value = usernameInput.value.trim().toLowerCase();
    });
  }

  function init() {
    initRememberLoginId();
    initVerifyToggle();
    initAgreeAll();
    initRegisterForm();
    initFindPasswordUsername();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
