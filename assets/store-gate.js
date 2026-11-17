// Store buttons outside the countries where Cerqa is in the stores (2026-11-16).
// The App Store and Google Play only say "not available in your country", with no word from us.
// Here, a visitor whose time zone is outside the US, Canada, Mexico, Colombia and Chile gets a
// short note first, with a link to open the store anyway (travelers, VPNs, wrong guesses).
// Only the browser's own time zone is read. Nothing is sent or stored.
(function () {
  "use strict";
  var AVAILABLE = /^(America\/(New_York|Detroit|Kentucky\/.+|Indiana\/.+|Chicago|Menominee|North_Dakota\/.+|Denver|Boise|Phoenix|Los_Angeles|Anchorage|Juneau|Sitka|Metlakatla|Yakutat|Nome|Adak|Puerto_Rico|Toronto|Montreal|Vancouver|Edmonton|Winnipeg|Halifax|St_Johns|Regina|Moncton|Glace_Bay|Goose_Bay|Whitehorse|Dawson|Dawson_Creek|Fort_Nelson|Creston|Iqaluit|Rankin_Inlet|Resolute|Cambridge_Bay|Inuvik|Swift_Current|Atikokan|Blanc-Sablon|Nipigon|Thunder_Bay|Rainy_River|Yellowknife|Pangnirtung|Mexico_City|Cancun|Merida|Monterrey|Matamoros|Chihuahua|Ciudad_Juarez|Ojinaga|Mazatlan|Bahia_Banderas|Hermosillo|Tijuana|Ensenada|Bogota|Santiago|Punta_Arenas)|Pacific\/(Honolulu|Easter)|US\/.+|Canada\/.+|Mexico\/.+|Chile\/.+)$/;

  var zone = "";
  try { zone = Intl.DateTimeFormat().resolvedOptions().timeZone || ""; } catch (e) {}
  // Unknown or generic zones (UTC, Etc/...) get the store as before.
  if (!zone || zone.indexOf("/") < 0 || zone.indexOf("Etc/") === 0 || AVAILABLE.test(zone)) return;

  var es = (document.documentElement.lang || "").toLowerCase().indexOf("es") === 0;
  var T = es ? {
    title: "Cerqa todav\u00eda no est\u00e1 en tu pa\u00eds",
    body: "La app de Cerqa est\u00e1 en la App Store y Google Play de Estados Unidos, Canad\u00e1, M\u00e9xico, Colombia y Chile. En tu pa\u00eds la tienda dir\u00e1 que no est\u00e1 disponible.",
    web: "Mientras tanto, puedes planear viajes en la web en ride.cerqa.app.",
    webCta: "Abrir ride.cerqa.app",
    anyway: "Abrir la tienda de todos modos",
    close: "Cerrar"
  } : {
    title: "Cerqa isn't in your country yet",
    body: "The Cerqa app is in the App Store and Google Play in the United States, Canada, Mexico, Colombia and Chile. In your country the store will say it isn't available.",
    web: "In the meantime, you can plan trips on the web at ride.cerqa.app.",
    webCta: "Open ride.cerqa.app",
    anyway: "Open the store anyway",
    close: "Close"
  };

  function isStoreLink(a) {
    var h = a && a.getAttribute && a.getAttribute("href");
    return !!h && (h.indexOf("apps.apple.com/") >= 0 || h.indexOf("play.google.com/store/apps") >= 0);
  }

  var css = "" +
    ".cq-sg-back{box-sizing:border-box;position:fixed;inset:0;background:rgba(15,23,42,.55);display:flex;align-items:center;justify-content:center;padding:16px;z-index:2147483000}" +
    ".cq-sg{box-sizing:border-box;background:#fff;color:#1f2937;max-width:420px;width:100%;border-radius:16px;padding:24px;box-shadow:0 20px 50px rgba(0,0,0,.25);font:16px/1.5 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif}" +
    ".cq-sg h2{margin:0 0 8px;font-size:20px;line-height:1.3}" +
    ".cq-sg p{margin:0 0 12px}" +
    ".cq-sg .cq-sg-web{display:block;text-align:center;background:#4a6fa5;color:#fff;text-decoration:none;border-radius:10px;padding:12px 16px;font-weight:600;margin:16px 0 10px}" +
    ".cq-sg .cq-sg-row{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}" +
    ".cq-sg .cq-sg-row a,.cq-sg .cq-sg-row button{background:none;border:0;padding:8px 0;color:#4a6fa5;font:inherit;font-size:15px;cursor:pointer;text-decoration:underline}" +
    "@media (prefers-color-scheme:dark){.cq-sg{background:#1f2937;color:#e5e7eb}.cq-sg .cq-sg-row a,.cq-sg .cq-sg-row button{color:#9db8e0}}";

  function show(href) {
    if (!document.getElementById("cq-sg-style")) {
      var st = document.createElement("style");
      st.id = "cq-sg-style";
      st.textContent = css;
      document.head.appendChild(st);
    }
    var back = document.createElement("div");
    back.className = "cq-sg-back";
    back.innerHTML =
      '<div class="cq-sg" role="dialog" aria-modal="true" aria-labelledby="cq-sg-t">' +
      '<h2 id="cq-sg-t"></h2><p class="cq-sg-b"></p><p class="cq-sg-w"></p>' +
      '<a class="cq-sg-web" href="https://ride.cerqa.app/" target="_blank" rel="noopener"></a>' +
      '<div class="cq-sg-row"><a class="cq-sg-any" target="_blank" rel="noopener"></a><button type="button" class="cq-sg-x"></button></div>' +
      "</div>";
    back.querySelector("#cq-sg-t").textContent = T.title;
    back.querySelector(".cq-sg-b").textContent = T.body;
    back.querySelector(".cq-sg-w").textContent = T.web;
    back.querySelector(".cq-sg-web").textContent = T.webCta;
    var any = back.querySelector(".cq-sg-any");
    any.textContent = T.anyway;
    any.setAttribute("href", href);
    var x = back.querySelector(".cq-sg-x");
    x.textContent = T.close;
    function close() { back.remove(); document.removeEventListener("keydown", onKey); }
    function onKey(e) { if (e.key === "Escape") close(); }
    x.addEventListener("click", close);
    any.addEventListener("click", function () { setTimeout(close, 0); });
    back.addEventListener("click", function (e) { if (e.target === back) close(); });
    document.addEventListener("keydown", onKey);
    document.body.appendChild(back);
    x.focus();
  }

  document.addEventListener("click", function (e) {
    var a = e.target && e.target.closest ? e.target.closest("a") : null;
    if (!a || !isStoreLink(a) || a.classList.contains("cq-sg-any")) return;
    e.preventDefault();
    show(a.getAttribute("href"));
  }, true);
})();
