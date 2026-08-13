/**

 * 헤더 프로모 배너 — 스크롤 시 위로 숨김, 맨 위로 돌아오면 다시 표시

 */

(function () {

  "use strict";



  const promo = document.getElementById("header-promo");

  if (!promo || !document.body.classList.contains("has-header-promo")) {

    return;

  }



  const HIDE_AFTER = 20;

  let hidden = false;

  let ticking = false;



  function update() {

    ticking = false;

    const shouldHide = window.scrollY > HIDE_AFTER;

    if (shouldHide === hidden) return;

    hidden = shouldHide;

    document.body.classList.toggle("is-promo-hidden", hidden);

  }



  function onScroll() {

    if (ticking) return;

    ticking = true;

    requestAnimationFrame(update);

  }



  window.addEventListener("scroll", onScroll, { passive: true });

  update();

})();

