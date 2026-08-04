/**
 * 장바구니 페이지
 */
(function () {
  "use strict";

  const FREE_SHIPPING_THRESHOLD = 300000;
  const SHIPPING_FEE = 4000;
  const PROPORTIONAL_THRESHOLD = 500000;
  const PROPORTIONAL_FEE = 80000;

  function formatPrice(value) {
    return Number(value).toLocaleString("ko-KR");
  }

  function showAlert(message) {
    const overlay = document.getElementById("shop-alert-overlay");
    const messageEl = document.getElementById("shop-alert-message");
    const okBtn = document.getElementById("shop-alert-ok");
    if (!overlay || !messageEl || !okBtn) {
      alert(message);
      return;
    }

    messageEl.textContent = message;
    overlay.hidden = false;
    overlay.setAttribute("aria-hidden", "false");
    requestAnimationFrame(() => overlay.classList.add("is-visible"));
    document.body.classList.add("shop-alert-open");
    okBtn.focus();

    function closeAlert() {
      overlay.classList.remove("is-visible");
      overlay.setAttribute("aria-hidden", "true");
      document.body.classList.remove("shop-alert-open");
      setTimeout(() => {
        overlay.hidden = true;
      }, 200);
      okBtn.removeEventListener("click", closeAlert);
      overlay.removeEventListener("click", onOverlayClick);
    }

    function onOverlayClick(event) {
      if (event.target === overlay) closeAlert();
    }

    okBtn.addEventListener("click", closeAlert);
    overlay.addEventListener("click", onOverlayClick);
  }

  function getSelectedRows() {
    return Array.from(document.querySelectorAll(".cart-page__row")).filter((row) => {
      const check = row.querySelector(".cart-item-check");
      return check && check.checked;
    });
  }

  function getSelectedIds() {
    return getSelectedRows().map((row) => row.dataset.productId);
  }

  function computeSelectedTotals() {
    const rows = getSelectedRows();
    let originalTotal = 0;
    let productTotal = 0;
    let discountTotal = 0;
    let shippingFee = 0;
    let codSeparate = false;
    let standardSubtotal = 0;

    rows.forEach((row) => {
      originalTotal += Number(row.dataset.originalSubtotal || 0);
      productTotal += Number(row.dataset.subtotal || 0);
      discountTotal += Number(row.dataset.discount || 0);
      shippingFee += Number(row.dataset.lineShipping || 0);
      if (row.dataset.codSeparate === "1") codSeparate = true;
      if (row.dataset.standardShipping === "1") {
        standardSubtotal += Number(row.dataset.subtotal || 0);
      }
    });

    if (standardSubtotal > 0 && standardSubtotal < FREE_SHIPPING_THRESHOLD) {
      shippingFee += SHIPPING_FEE;
    }

    const grandTotal = productTotal + shippingFee;

    return {
      original_total: originalTotal,
      product_total: productTotal,
      discount_total: discountTotal,
      shipping_fee: shippingFee,
      grand_total: grandTotal,
      cod_separate: codSeparate,
    };
  }

  function updateSummaryDisplay(totals) {
    const original = document.getElementById("summary-original");
    const shipping = document.getElementById("summary-shipping");
    const discount = document.getElementById("summary-discount");
    const periodDiscount = document.getElementById("summary-period-discount");
    const grand = document.getElementById("summary-grand");
    const footer = document.getElementById("cart-footer-total");
    const codNote = document.getElementById("summary-cod-note");

    if (original) original.textContent = `KRW ${formatPrice(totals.original_total)}`;
    if (shipping) shipping.textContent = `KRW ${formatPrice(totals.shipping_fee)}`;
    if (discount) discount.textContent = `KRW ${formatPrice(totals.discount_total)}`;
    if (periodDiscount) periodDiscount.textContent = `KRW ${formatPrice(totals.discount_total)}`;
    if (grand) grand.textContent = `KRW ${formatPrice(totals.grand_total)}`;

    if (footer) {
      const codText = totals.cod_separate ? " (착불 배송비 별도)" : "";
      footer.textContent =
        `[개별배송] 상품 ${formatPrice(totals.original_total)}` +
        ` − 할인금액 ${formatPrice(totals.discount_total)}` +
        ` + 배송비 ${formatPrice(totals.shipping_fee)}${codText}` +
        ` 총 ${formatPrice(totals.grand_total)}`;
    }

    if (codNote) codNote.hidden = !totals.cod_separate;
  }

  async function postJson(url, body) {
    const res = await fetch(url, {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    if (!res.ok || !data.ok) {
      throw new Error(data.message || "요청에 실패했습니다.");
    }
    return data;
  }

  function syncRowFromItem(row, item) {
    row.dataset.originalSubtotal = String(item.original_subtotal ?? item.price * item.quantity);
    row.dataset.subtotal = String(item.subtotal);
    row.dataset.discount = String(item.discount_amount);
    row.dataset.lineShipping = String(item.shipping_fee ?? 0);
    row.dataset.codSeparate = item.cod_separate ? "1" : "0";
    row.dataset.standardShipping = item.standard_shipping ? "1" : "0";

    const input = row.querySelector(".cart-page__qty-input");
    if (input) input.value = String(item.quantity);

    const shipNote = row.querySelector(".cart-page__ship-note");
    if (shipNote && item.shipping_label) shipNote.textContent = item.shipping_label;

    const lineTotal = row.querySelector(".cart-page__line-total");
    if (lineTotal) {
      const original = item.original_subtotal ?? item.price * item.quantity;
      const discountPart =
        item.discount_amount > 0 ? ` − [할인] ${formatPrice(item.discount_amount)}` : "";
      lineTotal.innerHTML = `[상품] KRW ${formatPrice(original)}${discountPart} = <strong>KRW ${formatPrice(item.subtotal)}</strong>`;
    }
  }

  function refreshSelectedSummary() {
    updateSummaryDisplay(computeSelectedTotals());
  }

  function updateSummary(data) {
    const countEl = document.querySelector(".cart-page__count");
    if (countEl) countEl.textContent = `(${data.count})`;
    window.MoodCodeCart?.updateHeaderCount?.(data.count || 0);

    data.items.forEach((item) => {
      const row = document.querySelector(`.cart-page__row[data-product-id="${item.id}"]`);
      if (row) syncRowFromItem(row, item);
    });

    refreshSelectedSummary();
  }

  function removeRow(productId) {
    document.querySelector(`.cart-page__row[data-product-id="${productId}"]`)?.remove();
    if (!document.querySelector(".cart-page__row")) {
      window.location.reload();
    } else {
      refreshSelectedSummary();
    }
  }

  async function changeQuantity(productId, quantity) {
    const data = await postJson("/api/cart/update", { product_id: productId, quantity });
    updateSummary(data);
  }

  function initSelectAll() {
    const selectAll = document.getElementById("cart-select-all");
    const checks = document.querySelectorAll(".cart-item-check");
    if (!selectAll || !checks.length) return;

    selectAll.addEventListener("change", () => {
      checks.forEach((box) => {
        box.checked = selectAll.checked;
      });
      refreshSelectedSummary();
    });

    checks.forEach((box) => {
      box.addEventListener("change", () => {
        selectAll.checked = Array.from(checks).every((item) => item.checked);
        refreshSelectedSummary();
      });
    });
  }

  function initQuantityControls() {
    document.querySelectorAll(".cart-page__qty").forEach((wrap) => {
      const productId = Number(wrap.dataset.productId);
      const input = wrap.querySelector(".cart-page__qty-input");

      wrap.querySelectorAll("[data-qty-delta]").forEach((btn) => {
        btn.addEventListener("click", async () => {
          const delta = Number(btn.dataset.qtyDelta);
          const current = Number(input.value) || 1;
          const next = current + delta;

          if (next < 1) {
            showAlert("최소 주문수량은 1개 입니다.");
            input.value = "1";
            return;
          }

          const clamped = Math.min(99, next);
          input.value = String(clamped);
          try {
            await changeQuantity(productId, clamped);
          } catch (err) {
            showAlert(err.message);
            input.value = String(current);
          }
        });
      });

      input?.addEventListener("change", async () => {
        const current = Number(input.dataset.lastValue || input.value) || 1;
        const raw = Number(input.value);

        if (!Number.isFinite(raw) || raw < 1) {
          showAlert("최소 주문수량은 1개 입니다.");
          input.value = String(current);
          return;
        }

        const next = Math.min(99, Math.max(1, raw));
        input.value = String(next);
        input.dataset.lastValue = String(next);

        try {
          await changeQuantity(productId, next);
        } catch (err) {
          showAlert(err.message);
          input.value = String(current);
        }
      });

      input?.addEventListener("focus", () => {
        input.dataset.lastValue = input.value;
      });
    });
  }

  function initRemoveButtons() {
    document.querySelectorAll("[data-remove-id]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const productId = Number(btn.dataset.removeId);
        if (!confirm("장바구니에서 삭제할까요?")) return;
        try {
          const data = await postJson("/api/cart/remove", { product_id: productId });
          updateSummary(data);
          removeRow(productId);
        } catch (err) {
          showAlert(err.message);
        }
      });
    });
  }

  function initOrderButtons() {
    const page = document.getElementById("cart-page");
    if (!page) return;
    const orderUrl = page.dataset.orderUrl || "/order";

    document.getElementById("cart-order-all")?.addEventListener("click", () => {
      window.location.href = orderUrl;
    });

    document.getElementById("cart-order-selected")?.addEventListener("click", () => {
      const ids = getSelectedIds();
      if (!ids.length) {
        showAlert("주문할 상품을 선택해 주세요.");
        return;
      }
      window.location.href = `${orderUrl}?ids=${ids.join(",")}`;
    });
  }

  function init() {
    initSelectAll();
    initQuantityControls();
    initRemoveButtons();
    initOrderButtons();
    refreshSelectedSummary();
  }

  window.MoodCodeCartPage = { showAlert, refreshSelectedSummary };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
