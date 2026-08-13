/**
 * 스크롤 — TOP 버튼 · 시즌 메뉴
 */
(function () {
  const SCROLL_THRESHOLD = 320;
  let animationId = null;
  let isAnimating = false;

  if ("scrollRestoration" in history) {
    history.scrollRestoration = "manual";
  }

  function getScrollY() {
    return (
      window.pageYOffset
      || document.documentElement.scrollTop
      || document.body.scrollTop
      || 0
    );
  }

  function setScrollY(y) {
    const maxY = Math.max(
      0,
      document.documentElement.scrollHeight - window.innerHeight
    );
    const top = Math.min(maxY, Math.max(0, y));
    document.documentElement.scrollTop = top;
    document.body.scrollTop = top;
  }

  function easeOutQuint(t) {
    return 1 - Math.pow(1 - t, 5);
  }

  function updateButtonVisibility() {
    const container = document.querySelector(".floating-actions");
    if (!container || isAnimating) return;
    container.classList.toggle("is-scrolled", getScrollY() > SCROLL_THRESHOLD);
  }

  function getAnchorScrollY(element) {
    const marginTop = parseFloat(window.getComputedStyle(element).scrollMarginTop) || 0;
    return getScrollY() + element.getBoundingClientRect().top - marginTop;
  }

  function smoothScrollTo(targetY, options = {}) {
    const endY = Math.max(0, targetY);
    const startY = getScrollY();

    if (Math.abs(endY - startY) < 2) {
      setScrollY(endY);
      updateButtonVisibility();
      options.onComplete?.();
      return;
    }

    if (animationId) {
      cancelAnimationFrame(animationId);
      animationId = null;
    }

    isAnimating = true;
    document.documentElement.classList.add("is-scrolling-top");

    const distance = Math.abs(endY - startY);
    const minDuration = options.minDuration ?? 2200;
    const maxDuration = options.maxDuration ?? 4500;
    const speed = options.speed ?? 2.2;
    const duration = Math.min(maxDuration, Math.max(minDuration, distance * speed));
    const startTime = performance.now();

    function finish() {
      setScrollY(endY);
      isAnimating = false;
      animationId = null;
      document.documentElement.classList.remove("is-scrolling-top");
      updateButtonVisibility();
      options.onComplete?.();
    }

    function tick(now) {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = easeOutQuint(progress);
      const nextY = startY + (endY - startY) * eased;

      setScrollY(nextY);

      if (progress < 1) {
        animationId = requestAnimationFrame(tick);
        return;
      }

      finish();
    }

    animationId = requestAnimationFrame(tick);
  }

  function smoothScrollToTop() {
    if (getScrollY() <= 0) return;
    smoothScrollTo(0);
  }

  function resolveScrollId(id) {
    const aliases = {
      "season-spring": "gallery-bloom",
      "season-summer": "gallery-clear",
      "season-autumn": "gallery-calm",
      "season-fall": "gallery-calm",
      "season-winter": "gallery-chic",
    };
    return aliases[id] || id;
  }

  function scrollToAnchor(id) {
    const target = document.getElementById(resolveScrollId(id));
    if (!target) return false;

    smoothScrollTo(getAnchorScrollY(target), {
      minDuration: 700,
      maxDuration: 1400,
      speed: 1.0,
    });
    return true;
  }

  /** 시즌 메뉴 — TOP 버튼과 동일한 커스텀 스크롤 (hash 점프 없음) */
  function initSeasonNav() {
    document.querySelectorAll(".main-nav [data-scroll-target]").forEach((link) => {
      link.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopImmediatePropagation();

        const id = link.dataset.scrollTarget;
        if (!id) return;

        if (scrollToAnchor(id)) return;

        window.location.href = `/?target=${encodeURIComponent(id)}`;
      });
    });
  }

  function initTopButton() {
    const scrollBtn = document.getElementById("scroll-top-btn");
    const container = document.querySelector(".floating-actions");

    if (!scrollBtn || !container) return;

    scrollBtn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      smoothScrollToTop();
    });

    let ticking = false;
    window.addEventListener(
      "scroll",
      () => {
        if (!ticking) {
          ticking = true;
          requestAnimationFrame(() => {
            updateButtonVisibility();
            ticking = false;
          });
        }
      },
      { passive: true }
    );

    updateButtonVisibility();
  }

  function handleInitialTarget() {
    const params = new URLSearchParams(window.location.search);
    const queryTarget = params.get("target");
    const hashTarget = window.location.hash.length > 1
      ? window.location.hash.slice(1)
      : null;
    const id = resolveScrollId(queryTarget || hashTarget || "");

    if (!id || !document.getElementById(id)) return;

    if (queryTarget) {
      const cleanUrl = window.location.pathname;
      history.replaceState(null, "", cleanUrl);
    } else if (hashTarget) {
      history.replaceState(null, "", window.location.pathname + window.location.search);
    }

    setScrollY(0);
    requestAnimationFrame(() => scrollToAnchor(id));
  }

  function init() {
    initTopButton();
    initSeasonNav();
    handleInitialTarget();
  }

  window.HspaceScrollTop = {
    init,
    smoothScrollToTop,
    smoothScrollTo,
    scrollToAnchor,
    getAnchorScrollY,
    getScrollY,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
