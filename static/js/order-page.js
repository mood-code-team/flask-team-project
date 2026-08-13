/**
 * 주문 페이지 — 무신사 스타일 쿠폰 선택 + 결제 예정 실시간 갱신
 */
(function () {
  "use strict";

  function formatPrice(value) {
    return Number(value || 0).toLocaleString("ko-KR");
  }

  function setRowVisible(row, visible) {
    if (!row) return;
    row.hidden = !visible;
  }

  function setBenefitError(message) {
    const el = document.getElementById("order-benefit-error");
    if (!el) return;
    const text = (message || "").trim();
    if (!text) {
      el.textContent = "";
      el.classList.add("is-hidden");
      return;
    }
    el.textContent = text;
    el.classList.remove("is-hidden");
  }

  function updateCouponSummary(hiddenInput, summaryEl, couponTitle, couponDiscountTotal) {
    if (!summaryEl) return;
    if (!hiddenInput?.value) {
      summaryEl.textContent = "사용 가능 쿠폰 선택";
      return;
    }
    if (couponTitle) {
      summaryEl.textContent =
        couponDiscountTotal > 0
          ? `${couponTitle} (−${formatPrice(couponDiscountTotal)}원)`
          : couponTitle;
      return;
    }
    const selected = document.querySelector('input[name="order_coupon_choice"]:checked');
    const title = selected?.dataset.title || "쿠폰 적용됨";
    const estimated = Number(selected?.dataset.estimated || 0);
    summaryEl.textContent =
      estimated > 0 ? `${title} (−${formatPrice(estimated)}원)` : title;
  }

  function updateSummary(data) {
    const originalEl = document.getElementById("order-summary-original");
    const couponRow = document.getElementById("order-summary-coupon-row");
    const couponLabel = document.getElementById("order-summary-coupon-label");
    const couponEl = document.getElementById("order-summary-coupon");
    const pointRow = document.getElementById("order-summary-point-row");
    const pointEl = document.getElementById("order-summary-point");
    const shippingEl = document.getElementById("order-summary-shipping");
    const discountRow = document.getElementById("order-summary-discount-row");
    const discountEl = document.getElementById("order-summary-discount");
    const grandEl = document.getElementById("order-summary-grand");
    const hiddenCoupon = document.getElementById("user-coupon");
    const summaryTrigger = document.getElementById("order-coupon-summary");

    const originalTotal = Number(data.original_total || data.product_total || 0);
    if (originalEl) originalEl.textContent = `KRW ${formatPrice(originalTotal)}`;

    const discountTotal = Number(data.discount_total || 0);
    setRowVisible(discountRow, discountTotal > 0);
    if (discountEl) discountEl.textContent = `− KRW ${formatPrice(discountTotal)}`;

    const productCoupon = Number(data.coupon_discount || 0);
    const shippingCoupon = Number(data.shipping_discount || 0);
    const couponDiscountTotal = Number(
      data.coupon_discount_total ?? productCoupon + shippingCoupon
    );
    setRowVisible(couponRow, couponDiscountTotal > 0);
    if (couponLabel) {
      couponLabel.textContent =
        shippingCoupon > 0 && productCoupon === 0 ? "배송비 쿠폰" : "쿠폰 할인";
    }
    if (couponEl) couponEl.textContent = `− KRW ${formatPrice(couponDiscountTotal)}`;

    const pointUsed = Number(data.point_used || 0);
    setRowVisible(pointRow, pointUsed > 0);
    if (pointEl) pointEl.textContent = `− KRW ${formatPrice(pointUsed)}`;

    const shippingFee = Number(data.shipping_fee || 0);
    if (shippingEl) {
      shippingEl.textContent = shippingFee === 0 ? "무료" : `KRW ${formatPrice(shippingFee)}`;
    }

    if (grandEl) grandEl.textContent = `KRW ${formatPrice(data.grand_total)}`;
    setBenefitError(data.benefit_error || "");
    updateCouponSummary(hiddenCoupon, summaryTrigger, data.coupon_title, couponDiscountTotal);
  }

  async function previewBenefits(form) {
    const hiddenCoupon = form.querySelector("#user-coupon");
    const pointInput = form.querySelector("#point-used");
    if (!hiddenCoupon) return;

    const payload = {
      ids: form.dataset.selectedIds || "",
      user_coupon_id: hiddenCoupon.value || "",
      point_used: pointInput ? pointInput.value || 0 : 0,
    };

    const res = await fetch("/api/order/preview", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok || !data.ok) {
      throw new Error(data.message || "금액 계산에 실패했습니다.");
    }
    updateSummary(data);
  }

  function initCouponModal(form, schedulePreview) {
    const modal = document.getElementById("order-coupon-modal");
    const openBtn = document.getElementById("order-coupon-open");
    const applyBtn = document.getElementById("order-coupon-apply");
    const hiddenCoupon = document.getElementById("user-coupon");
    if (!modal || !openBtn || !hiddenCoupon) return;

    let pendingValue = hiddenCoupon.value || "";

    function syncSelectedCard() {
      document.querySelectorAll(".order-coupon-card").forEach((card) => {
        const radio = card.querySelector(".order-coupon-card__radio");
        card.classList.toggle("is-selected", Boolean(radio?.checked));
      });
    }

    function openModal() {
      pendingValue = hiddenCoupon.value || "";
      document.querySelectorAll('input[name="order_coupon_choice"]').forEach((radio) => {
        radio.checked = radio.value === pendingValue;
      });
      syncSelectedCard();
      modal.hidden = false;
      modal.setAttribute("aria-hidden", "false");
      document.body.classList.add("order-coupon-open");
    }

    function closeModal() {
      modal.hidden = true;
      modal.setAttribute("aria-hidden", "true");
      document.body.classList.remove("order-coupon-open");
    }

    openBtn.addEventListener("click", openModal);
    modal.querySelectorAll("[data-coupon-close]").forEach((el) => {
      el.addEventListener("click", closeModal);
    });

    modal.querySelectorAll('input[name="order_coupon_choice"]').forEach((radio) => {
      radio.addEventListener("change", () => {
        pendingValue = radio.value;
        syncSelectedCard();
      });
    });

    applyBtn?.addEventListener("click", () => {
      hiddenCoupon.value = pendingValue;
      closeModal();
      schedulePreview();
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && !modal.hidden) closeModal();
    });
  }

  function initPointMax(form, schedulePreview) {
    const maxBtn = document.getElementById("order-point-max");
    const pointInput = document.getElementById("point-used");
    if (!maxBtn || !pointInput) return;

    maxBtn.addEventListener("click", () => {
      const max = Number(pointInput.max || 0);
      pointInput.value = String(max);
      schedulePreview();
    });
  }

  function initOrderBenefits() {
    const form = document.getElementById("order-form");
    const hiddenCoupon = document.getElementById("user-coupon");
    const pointInput = document.getElementById("point-used");
    if (!form) return;

    let timer = null;
    const schedulePreview = () => {
      window.clearTimeout(timer);
      timer = window.setTimeout(() => {
        previewBenefits(form).catch((err) => setBenefitError(err.message));
      }, 180);
    };

    initCouponModal(form, schedulePreview);
    initPointMax(form, schedulePreview);

    pointInput?.addEventListener("input", schedulePreview);
    pointInput?.addEventListener("change", schedulePreview);

    if (hiddenCoupon?.value || Number(pointInput?.value || 0) > 0) {
      schedulePreview();
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initOrderBenefits);
  } else {
    initOrderBenefits();
  }
})();
