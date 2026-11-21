/* Live US-Mexico border waits from CBP (bwt.cbp.gov, public, allows browser requests).
   Fills every [data-port] element: data-mode="detail" gets the full card, "row" just the headline.
   Refreshes every 5 minutes. Waits over 60 minutes read as hours and minutes. */
(function () {
  var es = document.documentElement.lang === "es";
  var fr = /^fr/.test(document.documentElement.lang || "");   // Quebec pages (2026-11-21)
  // US-Canada pages: NEXUS instead of SENTRI, waits into Canada from CBSA, no "border waits in the app" claim.
  var ca = document.body && document.body.getAttribute("data-border") === "ca";
  var T = fr ? {
    cars: "Voitures", sentri: "NEXUS", ready: "Ready Lane", walk: "Piétons", walkReady: "Piétons, Ready Lane",
    lanes: function (n) { return n == 1 ? "1 voie ouverte" : n + " voies ouvertes"; },
    closed: "Fermé en ce moment", noReport: "Aucune donnée en ce moment", noWait: "Aucune attente",
    updated: "Mis à jour", hours24: "Ouvert 24 h", hours: "Heures", carsShort: "voitures", walkShort: "à pied",
    error: "Impossible de charger les temps de la CBP. Réessayez dans un instant.", h: "h",
    intoCanada: "vers le Canada", intoUS: "vers les États-Unis", appCa: "Voyez votre groupe sur une carte, appli gratuite", travellers: "Voyageurs", cbsaError: "Impossible de charger les temps de l'ASFC. Réessayez dans un instant.",
    barCa: "Voyez votre groupe sur une carte", barSubCa: "Cerqa, gratuit sur Google Play",
    fastest: "Le plus rapide en voiture", now: "en ce moment", live: "En direct", app: "Voyez votre groupe sur une carte, appli gratuite", dl: "/fr/telecharger/",
    bar: "Voyez votre groupe sur une carte", barSub: "Cerqa, gratuit sur Google Play", barGet: "Installer", close: "Fermer"
  } : es ? {
    cars: "Autos", sentri: "SENTRI", ready: "Ready Lane", walk: "Peatones", walkReady: "Peatones, Ready Lane",
    lanes: function (n) { return n == 1 ? "1 carril abierto" : n + " carriles abiertos"; },
    closed: "Cerrada ahorita", noReport: "Sin reporte ahorita", noWait: "Sin espera",
    updated: "Actualizado", hours24: "Abierta 24 horas", hours: "Horario", carsShort: "autos", walkShort: "a pie",
    error: "No pudimos cargar los tiempos de CBP. Intenta de nuevo en un momento.", h: "h",
    fastest: "Más rápido en auto", now: "ahorita", live: "Míralo en vivo", app: "Tiempos de la frontera en tu mapa, app gratis", dl: "/es/descargar/",
    bar: "Tiempos de la frontera en tu mapa", barSub: "Cerqa, gratis en Google Play", barGet: "Instalar", close: "Cerrar"
  } : {
    cars: "Cars", sentri: "SENTRI", ready: "Ready Lane", walk: "Walking", walkReady: "Walking, Ready Lane",
    lanes: function (n) { return n == 1 ? "1 lane open" : n + " lanes open"; },
    closed: "Closed now", noReport: "No report right now", noWait: "No wait",
    updated: "Updated", hours24: "Open 24 hours", hours: "Hours", carsShort: "cars", walkShort: "walking",
    error: "Couldn't load CBP wait times. Try again in a moment.", h: "hr",
    intoCanada: "into Canada", intoUS: "into the US", appCa: "See your group on one map, free app", travellers: "Travelers", cbsaError: "Couldn't load CBSA wait times. Try again in a moment.",
    barCa: "See your group on one map", barSubCa: "Cerqa, free on Google Play",
    fastest: "Fastest by car", now: "right now", live: "Live", app: "Border waits on your map, free app", dl: "/download/",
    bar: "Border waits on your map", barSub: "Cerqa, free on Google Play", barGet: "Install", close: "Close"
  };

  if (ca) T.sentri = "NEXUS";

  function minutes(lane) {
    if (!lane) return null;
    var s = (lane.operational_status || "").toLowerCase();
    if (s !== "delay" && s !== "no delay") return null;
    var m = parseInt(lane.delay_minutes, 10);
    return isNaN(m) ? null : m;
  }

  function fmt(m) {
    if (m === 0) return T.noWait;
    var h = Math.floor(m / 60), r = m % 60;
    if (h === 0) return r + " min";
    return r === 0 ? h + " " + T.h : h + " " + T.h + " " + r + " min";
  }

  function level(m) {
    if (m == null) return "none";
    return m < 20 ? "clear" : m <= 60 ? "moderate" : "heavy";
  }

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  function isOpen(p) { return (p.port_status || "").toLowerCase() === "open"; }

  function headline(p) {
    var car = minutes(p.passenger_vehicle_lanes && p.passenger_vehicle_lanes.standard_lanes);
    if (car != null) return { m: car, kind: T.carsShort };
    var ped = minutes(p.pedestrian_lanes && p.pedestrian_lanes.standard_lanes);
    if (ped != null) return { m: ped, kind: T.walkShort };
    return null;
  }

  function updated(p) {
    var lanes = [p.passenger_vehicle_lanes && p.passenger_vehicle_lanes.standard_lanes,
      p.pedestrian_lanes && p.pedestrian_lanes.standard_lanes];
    for (var i = 0; i < lanes.length; i++) {
      var u = lanes[i] && lanes[i].update_time;
      if (u) return u.replace(/^At /, "");
    }
    return "";
  }

  function hoursText(p) {
    var h = p.hours || "";
    if (/^24/.test(h)) return T.hours24;
    return h ? T.hours + ": " + h : "";
  }

  function detail(el, p) {
    if (!isOpen(p)) {
      el.innerHTML = '<div class="wait-headline"><span class="wait-big lvl-none">' + T.closed + "</span></div>" +
        '<p class="wait-meta">' + esc(hoursText(p)) + "</p>";
      return;
    }
    var hl = headline(p);
    var big = hl ? '<span class="wait-big lvl-' + level(hl.m) + '">' + fmt(hl.m) + '</span><span class="wait-label">' + hl.kind + "</span>"
      : '<span class="wait-big lvl-none" style="font-size:24px">' + T.noReport + "</span>";
    var pv = p.passenger_vehicle_lanes || {}, pd = p.pedestrian_lanes || {};
    var rows = [
      [T.cars, pv.standard_lanes], [T.sentri, pv.NEXUS_SENTRI_lanes], [T.ready, pv.ready_lanes],
      [T.walk, pd.standard_lanes], [T.walkReady, pd.ready_lanes]
    ].map(function (r) {
      var m = minutes(r[1]);
      if (m == null) return "";
      var n = parseInt(r[1].lanes_open, 10);
      return "<li><span>" + r[0] + (n > 0 ? ' <span class="lanes">· ' + T.lanes(n) + "</span>" : "") +
        '</span><span class="value lvl-' + level(m) + '">' + fmt(m) + "</span></li>";
    }).join("");
    var meta = [hoursText(p), updated(p) ? T.updated + " " + updated(p) : ""].filter(Boolean).join(" · ");
    el.innerHTML = '<div class="wait-headline">' + big + "</div>" +
      (rows ? '<ul class="wait-rows">' + rows + "</ul>" : "") +
      '<p class="wait-meta">' + esc(meta) + "</p>";
  }

  function row(el, p) {
    el.removeAttribute("data-car");
    var car = isOpen(p) ? minutes(p.passenger_vehicle_lanes && p.passenger_vehicle_lanes.standard_lanes) : null;
    if (car != null) el.setAttribute("data-car", car);
    if (!isOpen(p)) { el.innerHTML = '<span class="lvl-none">' + T.closed + "</span>"; return; }
    var hl = headline(p);
    el.innerHTML = hl ? '<span class="lvl-' + level(hl.m) + '">' + fmt(hl.m) + "</span><small>" + (ca && hl.kind === T.carsShort ? T.intoUS : hl.kind) + "</small>"
      : '<span class="lvl-none">' + T.noReport + "</span>";
  }

  // In lists marked data-fastest, badge the open crossing with the shortest general car wait.
  // Only cars are compared, so a walking-only wait never wins against a car lane.
  function markFastest() {
    document.querySelectorAll("[data-fastest]").forEach(function (list) {
      list.querySelectorAll(".fastest").forEach(function (b) { b.remove(); });
      var best = null;
      list.querySelectorAll("[data-car]").forEach(function (el) {
        var m = parseInt(el.getAttribute("data-car"), 10);
        if (best === null || m < best.m) best = { m: m, el: el, tie: false };
        else if (m === best.m) best.tie = true;
      });
      if (!best || best.tie || list.querySelectorAll("[data-car]").length < 2) return;
      var name = best.el.parentNode.querySelector(".crossing-name");
      var b = document.createElement("span");
      b.className = "fastest";
      b.textContent = T.fastest;
      name.insertBefore(b, name.querySelector(".crossing-sub"));
    });
  }

  // English page, Spanish browser: offer the Spanish page once (dismissal remembered when storage works).
  function offerSpanish() {
    if (es || !/^es\b/i.test(navigator.language || "")) return;
    var alt = document.querySelector('link[rel="alternate"][hreflang="es"]');
    if (!alt) return;
    try { if (localStorage.getItem("cerqa_es_offer") === "no") return; } catch (e) {}
    var bar = document.createElement("p");
    bar.className = "lang-offer";
    bar.innerHTML = '¿Prefieres español? <a href="' + alt.getAttribute("href").replace(/^https:\/\/cerqa\.app/, "") +
      '" hreflang="es" lang="es">Ver en español</a> <button type="button" aria-label="Cerrar">×</button>';
    bar.querySelector("button").addEventListener("click", function () {
      bar.remove();
      try { localStorage.setItem("cerqa_es_offer", "no"); } catch (e) {}
    });
    var main = document.querySelector("main");
    if (main) main.insertBefore(bar, main.firstChild);
  }

  function track(name, params) {
    try { if (window.gtag) window.gtag("event", name, Object.assign({ page: location.pathname, transport_type: "beacon" }, params)); } catch (e) {}
  }

  // WhatsApp message with the current wait, e.g. "Puente 2: 1 h 30 min autos ahorita. Míralo en vivo: <link>".
  var lastShareText = null, lastByPort = null, myCbsa = null;
  function updateShare(byPort) {
    if (byPort) lastByPort = byPort;
    byPort = lastByPort;
    if (!byPort) return;
    var a = document.querySelector(".share-wa");
    var card = document.querySelector('.wait-card[data-mode="detail"]');
    if (!a || !card) return;
    var p = byPort[card.getAttribute("data-port")];
    var hl = p && isOpen(p) ? headline(p) : null;
    var name = a.getAttribute("data-share-name"), url = a.getAttribute("data-share-url");
    // Second line lets the person who gets the message install the app (its own campaign tag in GA).
    var appUrl = "https://cerqa.app" + T.dl + "?utm_source=whatsapp&utm_medium=share&utm_campaign=border_share_app";
    var waits;
    if (ca) {
      var parts = [];
      var low = function (m) { return m === 0 ? T.noWait.toLowerCase() : fmt(m); };
      if (hl) parts.push(T.intoUS + " " + low(hl.m));
      if (myCbsa != null) parts.push(T.intoCanada + " " + low(myCbsa));
      waits = parts.length ? ": " + parts.join(", ") + " " + T.now : "";
    } else {
      waits = hl ? ": " + fmt(hl.m) + " " + hl.kind + " " + T.now : "";
    }
    lastShareText = name + waits + ". " + T.live + ": " + url + "\n" + (ca ? T.appCa : T.app) + ": " + appUrl;
    a.href = "https://wa.me/?text=" + encodeURIComponent(lastShareText);
  }

  function setupShare() {
    var a = document.querySelector(".share-wa");
    if (!a) return;
    a.addEventListener("click", function () { track("share_click", { method: "whatsapp" }); });
    var other = document.querySelector(".share-other");
    if (other && navigator.share) {
      other.hidden = false;
      other.addEventListener("click", function () {
        track("share_click", { method: "native" });
        navigator.share({ text: lastShareText || a.getAttribute("data-share-name") + ": " + a.getAttribute("data-share-url") }).catch(function () {});
      });
    }
  }

  // Android phones get no store banner from the browser (iPhone gets Apple's), so show a small bar.
  function androidBar() {
    if (!/Android/i.test(navigator.userAgent || "")) return;
    try { if (localStorage.getItem("cerqa_android_bar") === "no") return; } catch (e) {}
    var slug = (location.pathname.split("/").filter(Boolean).pop() || "hub").replace(/-/g, "_");
    var ref = "utm_source=cerqa.app&utm_medium=android_bar&utm_campaign=border_" + (ca ? "ca_" : "") + slug + "_" + (fr ? "fr" : es ? "es" : "en");
    var bar = document.createElement("div");
    bar.className = "android-bar";
    bar.innerHTML = '<button type="button" class="android-bar-x" aria-label="' + T.close + '">×</button>' +
      '<img src="/images/icon/apple-touch-icon.png" alt="" width="40" height="40">' +
      '<span class="android-bar-text"><strong>' + (ca ? T.barCa : T.bar) + "</strong><small>" + (ca ? T.barSubCa : T.barSub) + "</small></span>" +
      '<a href="https://play.google.com/store/apps/details?id=com.cerqa.app&referrer=' + encodeURIComponent(ref) + '">' + T.barGet + "</a>";
    bar.querySelector(".android-bar-x").addEventListener("click", function () {
      bar.remove();
      document.body.classList.remove("has-android-bar");
      try { localStorage.setItem("cerqa_android_bar", "no"); } catch (e) {}
    });
    document.body.appendChild(bar);
    document.body.classList.add("has-android-bar");
  }

  function load() {
    fetch("https://bwt.cbp.gov/api/bwtnew", { cache: "no-store" })
      .then(function (r) { return r.json(); })
      .then(function (list) {
        var byPort = {};
        list.forEach(function (p) { byPort[p.port_number] = p; });
        document.querySelectorAll("[data-port]").forEach(function (el) {
          var p = byPort[el.getAttribute("data-port")];
          if (!p) { el.innerHTML = '<span class="lvl-none">' + T.noReport + "</span>"; return; }
          (el.getAttribute("data-mode") === "detail" ? detail : row)(el, p);
        });
        markFastest();
        updateShare(byPort);
      })
      .catch(function () {
        document.querySelectorAll('[data-port][data-mode="detail"]').forEach(function (el) {
          el.innerHTML = '<p class="wait-loading">' + T.error + "</p>";
        });
      });
  }

  // CBSA (into Canada): cerqa.app/data/cbsa-bwt.csv is an Amplify rewrite of CBSA's open-data CSV.
  // Rows are "Office;; Location;; Last updated;; Commercial CA;; Commercial US;; Travellers CA;; Travellers US;;".
  function cbsaMinutes(v) {
    v = (v || "").trim();
    if (/^no delay$/i.test(v)) return 0;
    var m = v.match(/^(\d+)\s*minute/i);
    return m ? parseInt(m[1], 10) : null;
  }

  function cbsaUpdated(v) {
    var m = (v || "").match(/(\d{1,2}):(\d{2})\s*([A-Z]{2,4})?/);
    if (!m) return "";
    if (fr) return parseInt(m[1], 10) + " h " + m[2];
    var h = parseInt(m[1], 10), ap = h >= 12 ? "pm" : "am";
    h = h % 12 || 12;
    // CBSA's zone label can be off (PDT in November), so show the time only.
    return h + ":" + m[2] + " " + ap;
  }

  function loadCbsa() {
    if (!document.querySelector("[data-cbsa]")) return;
    fetch("/data/cbsa-bwt.csv", { cache: "no-store" })
      .then(function (r) { return r.text(); })
      .then(function (text) {
        var byName = {};
        text.split(/\r?\n/).slice(1).forEach(function (line) {
          var f = line.split(";;").map(function (x) { return x.trim(); });
          if (f.length >= 6 && f[0]) byName[f[0]] = { raw: f[5], m: cbsaMinutes(f[5]), updated: cbsaUpdated(f[2]) };
        });
        document.querySelectorAll("[data-cbsa]").forEach(function (el) {
          var r = byName[el.getAttribute("data-cbsa")];
          el.removeAttribute("data-car");
          var closed = r && /closed/i.test(r.raw);
          if (el.getAttribute("data-mode") === "detail") {
            if (!r) { el.innerHTML = '<p class="wait-loading">' + T.noReport + "</p>"; return; }
            var big = closed ? '<span class="wait-big lvl-none">' + T.closed + "</span>"
              : r.m == null ? '<span class="wait-big lvl-none" style="font-size:24px">' + T.noReport + "</span>"
              : '<span class="wait-big lvl-' + level(r.m) + '">' + fmt(r.m) + '</span><span class="wait-label">' + T.intoCanada + "</span>";
            el.innerHTML = '<div class="wait-headline">' + big + "</div>" +
              (r.m != null ? '<ul class="wait-rows"><li><span>' + T.travellers + '</span><span class="value lvl-' + level(r.m) + '">' + fmt(r.m) + "</span></li></ul>" : "") +
              '<p class="wait-meta">' + esc(r.updated ? T.updated + " " + r.updated : "") + "</p>";
          } else {
            if (r && r.m != null && !closed) el.setAttribute("data-car", r.m);
            el.innerHTML = !r ? '<span class="lvl-none">' + T.noReport + "</span>"
              : closed ? '<span class="lvl-none">' + T.closed + "</span>"
              : r.m == null ? '<span class="lvl-none">' + T.noReport + "</span>"
              : '<span class="lvl-' + level(r.m) + '">' + fmt(r.m) + "</span><small>" + T.intoCanada + "</small>";
          }
        });
        var mine = document.querySelector('.wait-card[data-cbsa]');
        var mr = mine && byName[mine.getAttribute("data-cbsa")];
        myCbsa = mr && !/closed/i.test(mr.raw) ? mr.m : null;
        markFastest();
        updateShare();
      })
      .catch(function () {
        document.querySelectorAll('[data-cbsa][data-mode="detail"]').forEach(function (el) {
          el.innerHTML = '<p class="wait-loading">' + T.cbsaError + "</p>";
        });
      });
  }

  offerSpanish();
  setupShare();
  androidBar();
  load();
  loadCbsa();
  setInterval(function () { load(); loadCbsa(); }, 5 * 60 * 1000);
})();
