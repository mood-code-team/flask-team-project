/**
 * 마이페이지 — 주문 취소 확인
 */
(function () {
  "use strict";

  function initCancelForms() {
    document.querySelectorAll(".mypage__cancel-form[data-confirm]").forEach((form) => {
      form.addEventListener("submit", (event) => {
        const message = form.dataset.confirm;
        if (!window.confirm(message)) {
          event.preventDefault();
        }
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initCancelForms);
  } else {
    initCancelForms();
  }
})();
