/** Daum 우편번호 검색 — 도로명·지번 주소 팝업 */
(function () {
  "use strict";

  function loadPostcodeScript() {
    return new Promise((resolve, reject) => {
      if (window.daum && window.daum.Postcode) {
        resolve();
        return;
      }
      const existing = document.querySelector('script[data-daum-postcode="1"]');
      if (existing) {
        existing.addEventListener("load", () => resolve());
        existing.addEventListener("error", () => reject(new Error("postcode load failed")));
        return;
      }
      const script = document.createElement("script");
      script.src = "//t1.daumcdn.net/mapjsapi/bundle/postcode/prod/postcode.v2.js";
      script.async = true;
      script.dataset.daumPostcode = "1";
      script.onload = () => resolve();
      script.onerror = () => reject(new Error("postcode load failed"));
      document.head.appendChild(script);
    });
  }

  function findField(root, name) {
    return root.querySelector(`[data-address-field="${name}"]`);
  }

  function setValue(el, value) {
    if (!el) return;
    el.value = value || "";
    el.dispatchEvent(new Event("input", { bubbles: true }));
  }

  function openSearch(group) {
    loadPostcodeScript()
      .then(() => {
        new window.daum.Postcode({
          oncomplete(data) {
            const road = data.roadAddress || data.autoRoadAddress || "";
            const jibun = data.jibunAddress || data.autoJibunAddress || "";
            setValue(findField(group, "postcode"), data.zonecode);
            setValue(findField(group, "road"), road);
            setValue(findField(group, "jibun"), jibun);
            const detail = findField(group, "detail");
            detail?.focus();
            syncHidden(group);
          },
          width: "100%",
          height: "100%",
        }).open();
      })
      .catch(() => {
        window.alert("주소 검색 서비스를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.");
      });
  }

  function syncHidden(group) {
    const hidden = findField(group, "full");
    if (!hidden) return;
    const postcode = findField(group, "postcode")?.value.trim() || "";
    const road = findField(group, "road")?.value.trim() || "";
    const jibun = findField(group, "jibun")?.value.trim() || "";
    const detail = findField(group, "detail")?.value.trim() || "";

    const head = [
      postcode ? `(${postcode})` : "",
      road,
      jibun && jibun !== road ? `[지번] ${jibun}` : "",
    ]
      .filter(Boolean)
      .join(" ");

    hidden.value = detail && head ? `${head} | ${detail}` : detail || head;
  }

  function bindGroup(group) {
    group.querySelectorAll("[data-address-search]").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        openSearch(group);
      });
    });

    ["road", "jibun", "detail", "postcode"].forEach((name) => {
      const field = findField(group, name);
      field?.addEventListener("input", () => syncHidden(group));
    });

    const form = group.closest("form");
    form?.addEventListener("submit", () => syncHidden(group));

    syncHidden(group);
  }

  document.querySelectorAll("[data-address-group]").forEach(bindGroup);
})();
