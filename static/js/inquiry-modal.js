/**
 * 1:1 문의 모달
 */
(function () {
  "use strict";

  const overlay = document.getElementById("inquiry-modal-overlay");
  const form = document.getElementById("inquiry-form");
  if (!overlay || !form) return;

  const closeBtn = document.getElementById("inquiry-modal-close");
  const cancelBtn = document.getElementById("inquiry-cancel-btn");
  const submitBtn = document.getElementById("inquiry-submit-btn");
  const typeSelect = document.getElementById("inquiry-type");
  const orderSelect = document.getElementById("inquiry-order");
  const fileInput = document.getElementById("inquiry-files");
  const fileList = document.getElementById("inquiry-file-list");
  const errorEl = document.getElementById("inquiry-form-error");

  const isLoggedIn = document.body.dataset.userLoggedIn === "true";
  const loginUrl = document.body.dataset.loginUrl || "/auth/login";
  const metaLoaded = { value: false };

  let selectedFiles = [];

  function openModal() {
    if (!isLoggedIn) {
      const next = encodeURIComponent(window.location.pathname + window.location.search);
      window.location.href = `${loginUrl}?next=${next}`;
      return;
    }

    overlay.hidden = false;
    overlay.setAttribute("aria-hidden", "false");
    requestAnimationFrame(() => overlay.classList.add("is-visible"));
    document.body.classList.add("inquiry-modal-open");
    loadMeta();
    document.getElementById("inquiry-title")?.focus();
  }

  function closeModal() {
    overlay.classList.remove("is-visible");
    overlay.setAttribute("aria-hidden", "true");
    document.body.classList.remove("inquiry-modal-open");
    window.setTimeout(() => {
      overlay.hidden = true;
      resetForm();
    }, 250);
  }

  function resetForm() {
    form.reset();
    selectedFiles = [];
    renderFileList();
    if (errorEl) {
      errorEl.hidden = true;
      errorEl.textContent = "";
    }
    submitBtn.disabled = false;
    submitBtn.textContent = "접수하기";
  }

  async function loadMeta() {
    if (metaLoaded.value) return;
    try {
      const res = await fetch("/support/api/inquiry-meta");
      if (!res.ok) return;
      const data = await res.json();

      typeSelect.innerHTML = '<option value="">문의 유형 선택</option>';
      data.inquiry_types.forEach((item) => {
        const opt = document.createElement("option");
        opt.value = item.value;
        opt.textContent = item.label;
        typeSelect.appendChild(opt);
      });

      orderSelect.innerHTML = '<option value="">주문번호 선택</option>';
      data.orders.forEach((item) => {
        const opt = document.createElement("option");
        opt.value = item.order_number;
        opt.textContent = item.label;
        orderSelect.appendChild(opt);
      });

      metaLoaded.value = true;
    } catch {
      /* 메타 로드 실패 시 기본 폼 유지 */
    }
  }

  function renderFileList() {
    if (!fileList) return;
    fileList.innerHTML = "";
    selectedFiles.forEach((file, index) => {
      const li = document.createElement("li");
      li.className = "inquiry-attach__item";
      li.innerHTML = `
        <span>${file.name}</span>
        <button type="button" class="inquiry-attach__remove" data-index="${index}">삭제</button>
      `;
      fileList.appendChild(li);
    });
  }

  fileInput?.addEventListener("change", () => {
    const incoming = Array.from(fileInput.files || []);
    selectedFiles = selectedFiles.concat(incoming).slice(0, 5);
    fileInput.value = "";
    renderFileList();
  });

  fileList?.addEventListener("click", (event) => {
    const btn = event.target.closest(".inquiry-attach__remove");
    if (!btn) return;
    const index = Number(btn.dataset.index);
    selectedFiles.splice(index, 1);
    renderFileList();
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (errorEl) errorEl.hidden = true;

    submitBtn.disabled = true;
    submitBtn.textContent = "접수 중...";

    const formData = new FormData(form);
    formData.delete("attachments");
    selectedFiles.forEach((file) => formData.append("attachments", file));

    try {
      const res = await fetch("/support/api/inquiries", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.error || "문의 접수에 실패했습니다.");
      }
      closeModal();
      alert(data.message || "문의가 접수되었습니다.");
    } catch (err) {
      if (errorEl) {
        errorEl.textContent = err.message || "문의 접수에 실패했습니다.";
        errorEl.hidden = false;
      }
      submitBtn.disabled = false;
      submitBtn.textContent = "접수하기";
    }
  });

  closeBtn?.addEventListener("click", closeModal);
  cancelBtn?.addEventListener("click", closeModal);
  overlay.addEventListener("click", (event) => {
    if (event.target === overlay) closeModal();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !overlay.hidden) closeModal();
  });

  document.querySelectorAll("[data-inquiry-open]").forEach((el) => {
    el.addEventListener("click", (event) => {
      event.preventDefault();
      openModal();
    });
  });

  window.MoodCodeInquiry = { open: openModal, close: closeModal };
})();
