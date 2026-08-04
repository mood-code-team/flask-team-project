/** 채널톡 연동 */
(function () {
  "use strict";

  const config = window.__MOOD_CHANNEL_TALK__;
  if (!config || !config.pluginKey) {
    return;
  }

  let booted = false;

  function loadScript() {
    return new Promise((resolve, reject) => {
      if (window.ChannelTalk) {
        resolve();
        return;
      }
      const existing = document.querySelector('script[data-channel-talk="true"]');
      if (existing) {
        existing.addEventListener("load", () => resolve());
        existing.addEventListener("error", () => reject(new Error("채널톡 스크립트 로드 실패")));
        return;
      }
      const script = document.createElement("script");
      script.async = true;
      script.dataset.channelTalk = "true";
      script.src = "https://cdn.channel.io/plugin/ch-plugin-web.js";
      script.onload = () => resolve();
      script.onerror = () => reject(new Error("채널톡 스크립트 로드 실패"));
      document.body.appendChild(script);
    });
  }

  function bootChannelTalk() {
    return new Promise((resolve, reject) => {
      if (booted && window.ChannelTalk) {
        resolve();
        return;
      }
      if (!window.ChannelTalk) {
        reject(new Error("ChannelTalk SDK 없음"));
        return;
      }
      window.ChannelTalk("boot", config, (error) => {
        if (error) {
          reject(error);
          return;
        }
        booted = true;
        resolve();
      });
    });
  }

  function openMessenger() {
    loadScript()
      .then(() => bootChannelTalk())
      .then(() => {
        if (window.ChannelTalk) {
          window.ChannelTalk("showMessenger");
        }
      })
      .catch(() => {
        window.location.href = "/support/";
      });
  }

  window.MoodCodeChannelTalk = {
    open: openMessenger,
    isEnabled: true,
  };

  loadScript().then(() => bootChannelTalk()).catch(() => {});

  document.querySelectorAll("[data-channel-talk-open]").forEach((el) => {
    el.addEventListener("click", (event) => {
      event.preventDefault();
      openMessenger();
    });
  });
})();
