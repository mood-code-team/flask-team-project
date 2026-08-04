/**
 * 토스페이먼츠 v2 — 카드 결제창 호출
 */
(function () {
  "use strict";

  function normalizePhone(value) {
    return String(value || "").replace(/\D/g, "");
  }

  async function initPayment() {
    const page = document.getElementById("payment-page");
    const button = document.getElementById("toss-pay-button");
    if (!page || !button || typeof TossPayments === "undefined") return;

    const clientKey = page.dataset.clientKey;
    const orderId = page.dataset.orderId;
    const orderName = page.dataset.orderName;
    const amount = Number(page.dataset.amount);
    const customerName = page.dataset.customerName;
    const customerPhone = normalizePhone(page.dataset.customerPhone);
    const successUrl = page.dataset.successUrl;
    const failUrl = page.dataset.failUrl;

    if (!clientKey || !orderId || !amount) return;

    const tossPayments = TossPayments(clientKey);
    const payment = tossPayments.payment({ customerKey: TossPayments.ANONYMOUS });

    button.addEventListener("click", async () => {
      button.disabled = true;
      button.textContent = "결제창 여는 중…";

      try {
        await payment.requestPayment({
          method: "CARD",
          amount: {
            currency: "KRW",
            value: amount,
          },
          orderId,
          orderName,
          successUrl,
          failUrl: `${failUrl}?orderId=${encodeURIComponent(orderId)}`,
          customerName,
          customerMobilePhone: customerPhone,
        });
      } catch (error) {
        if (error.code === "USER_CANCEL") {
          button.disabled = false;
          button.textContent = `KRW ${amount.toLocaleString("ko-KR")} 결제하기`;
          return;
        }
        const params = new URLSearchParams({
          orderId,
          code: error.code || "PAYMENT_ERROR",
          message: error.message || "결제 중 오류가 발생했습니다.",
        });
        window.location.href = `${failUrl}?${params.toString()}`;
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initPayment);
  } else {
    initPayment();
  }
})();
