/** MOOD GALLERY 카드 호버 — 페이지 전체 배경색 변경 */
(function () {
  "use strict";

  const MOODS = ["bloom", "clear", "calm", "chic"];

  function clearMoodHover() {
    MOODS.forEach(function (mood) {
      document.body.classList.remove("mood-hover-" + mood);
    });
  }

  function initGalleryMoodHover() {
    if (!document.body.classList.contains("page-home")) {
      return;
    }

    var grid = document.querySelector(".gallery-entry__grid");
    if (!grid) {
      return;
    }

    grid.addEventListener(
      "mouseover",
      function (event) {
        var item = event.target.closest("[data-mood-hover]");
        if (!item || !grid.contains(item)) {
          return;
        }

        var mood = item.getAttribute("data-mood-hover");
        if (!mood || MOODS.indexOf(mood) === -1) {
          return;
        }

        MOODS.forEach(function (name) {
          document.body.classList.toggle("mood-hover-" + name, name === mood);
        });
      },
      true
    );

    grid.addEventListener("mouseleave", clearMoodHover);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initGalleryMoodHover);
  } else {
    initGalleryMoodHover();
  }
})();
