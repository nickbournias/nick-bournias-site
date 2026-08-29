(() => {
  const onReady = (fn) => {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn, { once: true });
    } else {
      fn();
    }
  };

  onReady(async () => {
    const typedTextEl = document.getElementById("typedText");
    const cursorEl = document.getElementById("cursor");
    const learnMoreEl = document.getElementById("learnMore");

    if (!typedTextEl || !learnMoreEl) return;

    // ---------- helpers ----------
    function getSearchText(str) {
      const parts = str.split(/[-–—]/);
      if (parts.length < 2) return str.trim();
      return parts.slice(1).join("-").trim();
    }

    function blinkCursor(times = 4, interval = 450) {
      if (!cursorEl) return;
      let count = 0;
      cursorEl.style.display = "inline-block";
      cursorEl.style.opacity = "1";

      const blink = setInterval(() => {
        cursorEl.style.opacity =
          cursorEl.style.opacity === "0" ? "1" : "0";
        count++;
        if (count >= times * 3) {
          clearInterval(blink);
          cursorEl.style.opacity = "0";
        }
      }, interval);
    }

    function typeWriter(text, speed = 60) { // <-- slower typing here
      typedTextEl.textContent = "";
      if (cursorEl) {
        cursorEl.textContent = "▌";
        cursorEl.style.opacity = "1";
      }

      let i = 0;
      const tick = () => {
        typedTextEl.textContent += text.charAt(i);
        i++;
        if (i < text.length) {
          setTimeout(tick, speed);
        } else {
          // typing finished → blink cursor 3 times
          blinkCursor(3);
        }
      };
      if (text.length) tick();
    }

    // ---------- fetch quote (cache-safe) ----------
    const quoteUrl =
      "/wp-content/uploads/daily_quote/today_quote.txt?v=" + Date.now();

    let quoteText = "";
    try {
      const res = await fetch(quoteUrl, {
        cache: "no-store",
        headers: { "Cache-Control": "no-cache" }
      });
      if (!res.ok) throw new Error("HTTP " + res.status);
      quoteText = (await res.text()).trim();
    } catch (err) {
      console.error("Quote fetch failed:", err);
      quoteText = "Couldn’t load today’s quote.";
      if (cursorEl) cursorEl.style.display = "none";
    }

    // ---------- render ----------
    typeWriter(quoteText, 60);

    // ---------- learn more ----------
    learnMoreEl.addEventListener("click", (e) => {
      e.preventDefault();
      const current = typedTextEl.textContent.trim();
      const searchText = getSearchText(current);
      if (!searchText) return;

      const url =
        "https://www.google.com/search?q=" +
        encodeURIComponent(searchText);
      window.open(url, "_blank", "noopener");
    });
  });
})();
