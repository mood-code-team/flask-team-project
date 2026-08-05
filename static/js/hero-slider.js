/** 메인 히어로 슬라이더 — 픽셀 기반 (Swiper 없음, HPIX 스타일) */
(function () {
  "use strict";

  const slider = document.querySelector(".hero-slider");
  if (!slider) return;

  const viewport = slider.querySelector(".hero-slider__viewport");
  const track = slider.querySelector(".hero-slider__track");
  if (!viewport || !track) return;

  const slideEls = slider.querySelectorAll(".hero-slider__slide");
  const dots = slider.querySelectorAll(".hero-slider__dot");
  const prevBtn = slider.querySelector(".hero-slider__prev");
  const nextBtn = slider.querySelector(".hero-slider__next");
  const counterCurrent = slider.querySelector(".hero-slider__counter-current");
  const headlineEl = document.querySelector("[data-hero-headline]");
  const leadEl = document.querySelector("[data-hero-lead]");
  const ctaEl = document.querySelector("[data-hero-cta]");
  const heroCopy = document.querySelector(".hero-ad__copy");
  const header = document.getElementById("site-header");

  const SLIDE_MS = 900;
  const INTERVAL = 5000;
  const EASING = "cubic-bezier(0.22, 1, 0.36, 1)";
  const total = slideEls.length;

  if (total <= 0) return;

  let current = 0;
  let timer = null;
  let animating = false;
  let dragging = false;
  let dragStartX = 0;
  let dragDelta = 0;
  let didDrag = false;
  let headerProgress = 0;
  let headerAnimating = false;

  function width() {
    return viewport.clientWidth || slider.clientWidth || 1;
  }

  function setTrack(offsetPx, animate) {
    const x = -(current * width()) + offsetPx;
    track.style.transition = animate ? `transform ${SLIDE_MS}ms ${EASING}` : "none";
    track.style.transform = `translate3d(${x}px, 0, 0)`;
  }

  function updateDots(index) {
    dots.forEach((dot, i) => {
      const on = i === index;
      dot.classList.toggle("is-active", on);
      dot.setAttribute("aria-selected", on ? "true" : "false");
    });
  }

  function updateCounter(index) {
    if (!counterCurrent) return;
    const num = String(index + 1);
    if (counterCurrent.textContent === num) return;
    counterCurrent.textContent = num;
    counterCurrent.classList.remove("is-changing");
    void counterCurrent.offsetWidth;
    counterCurrent.classList.add("is-changing");
  }

  function swapCopyText(el, text, animate) {
    if (!el || !text || el.textContent === text) return;
    if (animate) {
      el.classList.add("is-fading");
      window.setTimeout(() => {
        el.textContent = text;
        el.classList.remove("is-fading");
      }, 260);
      return;
    }
    el.textContent = text;
  }

  function updateAdCopy(index, animate) {
    const link = slideEls[index]?.querySelector(".hero-slide");
    if (!link) return;
    swapCopyText(headlineEl, link.dataset.slideHeadline, animate);
    swapCopyText(leadEl, link.dataset.slideLine, animate);
    if (ctaEl && link.href) ctaEl.href = link.href;
  }

  function goTo(index, animate) {
    if (animating && animate) return;
    current = ((index % total) + total) % total;
    dragDelta = 0;
    setTrack(0, animate !== false);
    updateDots(current);
    updateCounter(current);
    updateAdCopy(current, animate !== false);

    if (animate !== false) {
      animating = true;
      window.setTimeout(() => {
        animating = false;
      }, SLIDE_MS);
    }
  }

  function next() {
    goTo(current + 1, true);
  }

  function prev() {
    goTo(current - 1, true);
  }

  function startAuto() {
    if (total <= 1) return;
    stopAuto();
    timer = window.setInterval(next, INTERVAL);
  }

  function stopAuto() {
    if (timer) window.clearInterval(timer);
  }

  function finishDrag() {
    dragging = false;
    slider.classList.remove("is-dragging");
    const w = width();
    if (dragDelta <= -w * 0.15) {
      goTo(current + 1, true);
    } else if (dragDelta >= w * 0.15) {
      goTo(current - 1, true);
    } else {
      setTrack(0, true);
    }
    dragDelta = 0;
    startAuto();
  }

  function onDragStart(x) {
    if (animating) return;
    dragging = true;
    didDrag = false;
    dragStartX = x;
    dragDelta = 0;
    stopAuto();
    slider.classList.add("is-dragging");
    setTrack(0, false);
  }

  function onDragMove(x) {
    if (!dragging) return;
    dragDelta = x - dragStartX;
    if (Math.abs(dragDelta) > 6) didDrag = true;
    setTrack(dragDelta, false);
  }

  viewport.addEventListener("touchstart", (e) => {
    if (e.touches.length !== 1) return;
    onDragStart(e.touches[0].clientX);
  }, { passive: true });

  viewport.addEventListener("touchmove", (e) => {
    if (!dragging || e.touches.length !== 1) return;
    onDragMove(e.touches[0].clientX);
    if (didDrag) e.preventDefault();
  }, { passive: false });

  viewport.addEventListener("touchend", () => {
    if (dragging) finishDrag();
  });

  viewport.addEventListener("mousedown", (e) => {
    if (e.button !== 0) return;
    e.preventDefault();
    onDragStart(e.clientX);
    const move = (ev) => onDragMove(ev.clientX);
    const up = () => {
      document.removeEventListener("mousemove", move);
      document.removeEventListener("mouseup", up);
      if (dragging) finishDrag();
    };
    document.addEventListener("mousemove", move);
    document.addEventListener("mouseup", up);
  });

  slider.querySelectorAll(".hero-slide").forEach((link) => {
    link.addEventListener("click", (e) => {
      if (didDrag) {
        e.preventDefault();
        didDrag = false;
      }
    });
  });

  prevBtn?.addEventListener("click", () => {
    prev();
    startAuto();
  });

  nextBtn?.addEventListener("click", () => {
    next();
    startAuto();
  });

  dots.forEach((dot) => {
    dot.addEventListener("click", () => {
      goTo(parseInt(dot.dataset.slideIndex || "0", 10), true);
      startAuto();
    });
  });

  slider.addEventListener("mouseenter", stopAuto);
  slider.addEventListener("mouseleave", () => {
    if (!dragging) startAuto();
  });

  window.addEventListener("resize", () => setTrack(0, false));

  function applyHeaderProgress(value) {
    if (!header) return;
    const v = Math.min(1, Math.max(0, value));
    header.style.setProperty("--header-progress", v.toFixed(4));
    header.classList.toggle("is-solid", v > 0.94);
    document.body.classList.toggle("has-solid-header", v > 0.94);
  }

  function smoothHeaderStep() {
    const target = Math.min(1, Math.max(0, window.scrollY / 160));
    headerProgress += (target - headerProgress) * 0.11;
    if (Math.abs(target - headerProgress) < 0.004) {
      headerProgress = target;
      headerAnimating = false;
    } else {
      headerAnimating = true;
    }
    applyHeaderProgress(headerProgress);
    if (heroCopy) {
      const scrollY = window.scrollY;
      const fade = Math.min(1, scrollY / 420);
      heroCopy.style.setProperty("--hero-copy-shift", `${scrollY * 0.14}px`);
      heroCopy.style.setProperty("--hero-copy-opacity", `${1 - fade * 0.9}`);
    }
    if (headerAnimating) requestAnimationFrame(smoothHeaderStep);
  }

  window.addEventListener("scroll", () => {
    if (!headerAnimating) {
      headerAnimating = true;
      requestAnimationFrame(smoothHeaderStep);
    }
  }, { passive: true });

  goTo(0, false);
  applyHeaderProgress(0);
  startAuto();
})();
