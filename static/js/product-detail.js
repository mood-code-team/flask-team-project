/**
 * Mood Code — 상품 상세 (수량, sticky buybox, 모바일 결제 dock)
 */
(function () {
  "use strict";

  const MOBILE_MQ = window.matchMedia("(max-width: 768px)");

  function getPageRoot() {
    return document.querySelector(".product-detail--hpix");
  }

  function getQtyInput(root) {
    return root?.querySelector("[data-product-qty]") || document.querySelector("[data-product-qty]");
  }

  function getQty(root) {
    const input = getQtyInput(root);
    if (!input) return 1;
    const value = parseInt(input.value, 10);
    return Number.isFinite(value) && value > 0 ? value : 1;
  }

  function updateTotal(root) {
    const unit = parseInt(root?.dataset.unitPrice || getPageRoot()?.querySelector("[data-product-detail]")?.dataset.unitPrice, 10);
    if (!unit) return;
    const total = unit * getQty(root);
    const formatted = total.toLocaleString("ko-KR");
    root?.querySelectorAll("[data-detail-total]").forEach((el) => {
      el.textContent = formatted;
    });
    document.querySelectorAll("[data-mobile-total]").forEach((el) => {
      el.textContent = formatted;
    });
  }

  function setQty(root, next) {
    const input = getQtyInput(root);
    if (!input) return;
    const max = parseInt(input.max, 10) || 99;
    const clamped = Math.min(Math.max(next, 1), max);
    input.value = String(clamped);
    updateTotal(root);
  }

  function initQuantity(root) {
    root.querySelectorAll("[data-qty-minus]").forEach((btn) => {
      btn.addEventListener("click", () => setQty(root, getQty(root) - 1));
    });
    root.querySelectorAll("[data-qty-plus]").forEach((btn) => {
      btn.addEventListener("click", () => setQty(root, getQty(root) + 1));
    });
    const input = getQtyInput(root);
    input?.addEventListener("change", () => setQty(root, getQty(root)));
    updateTotal(root);
  }

  async function buyNow(slug, productId, quantity) {
    const ok = await window.MoodCodeCart?.addToCart?.(slug, quantity);
    if (!ok) return;
    window.location.href = `/order?ids=${productId}`;
  }

  function bindActions(page, shell) {
    const slug = shell.dataset.productSlug;
    const productId = shell.dataset.productId;

    page.querySelectorAll("[data-add-to-cart]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        if (btn.disabled || !slug) return;
        btn.disabled = true;
        const ok = await window.MoodCodeCart.addToCart(slug, getQty(shell));
        btn.disabled = false;
        if (ok) window.MoodCodeCart.openAddedModal?.();
      });
    });

    page.querySelectorAll("[data-buy-now]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        if (btn.disabled || !slug || !productId) return;
        btn.disabled = true;
        await buyNow(slug, productId, getQty(shell));
        btn.disabled = false;
      });
    });
  }

  function initMobileDock(page) {
    const bar = page.querySelector(".product-detail__mobile-bar");
    const sentinel = page.querySelector("[data-buybox-sentinel]");
    if (!bar || !sentinel || !MOBILE_MQ.matches) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        const show = !entry.isIntersecting;
        bar.classList.toggle("is-visible", show);
        bar.setAttribute("aria-hidden", show ? "false" : "true");
        page.classList.toggle("has-mobile-dock", show);
      },
      { root: null, threshold: 0, rootMargin: "0px 0px -72px 0px" }
    );

    observer.observe(sentinel);

    const onResize = () => {
      if (!MOBILE_MQ.matches) {
        bar.classList.remove("is-visible");
        bar.setAttribute("aria-hidden", "true");
        page.classList.remove("has-mobile-dock");
        observer.disconnect();
        window.removeEventListener("resize", onResize);
      }
    };
    window.addEventListener("resize", onResize);
  }

  function initSectionNav() {
    const links = document.querySelectorAll("[data-detail-nav]");
    const sections = document.querySelectorAll(".product-detail__panel[id]");
    if (!links.length || !sections.length) return;

    const headerOffset = () => {
      const nav = document.querySelector(".product-detail__nav");
      const header = parseInt(getComputedStyle(document.documentElement).getPropertyValue("--header-height"), 10) || 60;
      return header + (nav?.offsetHeight || 0) + 8;
    };

    links.forEach((link) => {
      link.addEventListener("click", (e) => {
        e.preventDefault();
        const target = document.getElementById(link.getAttribute("href").slice(1));
        if (!target) return;
        const top = target.getBoundingClientRect().top + window.scrollY - headerOffset();
        window.scrollTo({ top, behavior: "smooth" });
        links.forEach((l) => l.classList.remove("is-active"));
        link.classList.add("is-active");
      });
    });

    const spy = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          const id = entry.target.id;
          links.forEach((link) => {
            link.classList.toggle("is-active", link.getAttribute("href") === `#${id}`);
          });
        });
      },
      { rootMargin: `-${headerOffset()}px 0px -55% 0px`, threshold: 0 }
    );

    sections.forEach((section) => spy.observe(section));
  }

  function init() {
    const page = getPageRoot();
    const shell = page?.querySelector("[data-product-detail]");
    if (!page || !shell) return;

    initQuantity(shell);
    bindActions(page, shell);
    initMobileDock(page);
    initSectionNav();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
