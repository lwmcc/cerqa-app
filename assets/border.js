/* Live US-Mexico border waits from CBP (bwt.cbp.gov, public, allows browser requests).
   Fills every [data-port] element: data-mode="detail" gets the full card, "row" just the headline.
   Refreshes every 5 minutes. Waits over 60 minutes read as hours and minutes. */
(function () {
  var es = document.documentElement.lang === "es";
  var T = es ? {
    cars: "Autos", sentri: "SENTRI", ready: "Ready Lane", walk: "Peatones", walkReady: "Peatones, Ready Lane",
    lanes: function (n) { return n == 1 ? "1 carril abierto" : n + " carriles abiertos"; },
    closed: "Cerrada ahorita", noReport: "Sin reporte ahorita", noWait: "Sin espera",
    updated: "Actualizado", hours24: "Abierta 24 horas", hours: "Horario", carsShort: "autos", walkShort: "a pie",
    error: "No pudimos cargar los tiempos de CBP. Intenta de nuevo en un momento.", h: "h"
  } : {
    cars: "Cars", sentri: "SENTRI", ready: "Ready Lane", walk: "Walking", walkReady: "Walking, Ready Lane",
    lanes: function (n) { return n == 1 ? "1 lane open" : n + " lanes open"; },
    closed: "Closed now", noReport: "No report right now", noWait: "No wait",
    updated: "Updated", hours24: "Open 24 hours", hours: "Hours", carsShort: "cars", walkShort: "walking",
    error: "Couldn't load CBP wait times. Try again in a moment.", h: "hr"
  };

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
    if (!isOpen(p)) { el.innerHTML = '<span class="lvl-none">' + T.closed + "</span>"; return; }
    var hl = headline(p);
    el.innerHTML = hl ? '<span class="lvl-' + level(hl.m) + '">' + fmt(hl.m) + "</span><small>" + hl.kind + "</small>"
      : '<span class="lvl-none">' + T.noReport + "</span>";
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
      })
      .catch(function () {
        document.querySelectorAll('[data-port][data-mode="detail"]').forEach(function (el) {
          el.innerHTML = '<p class="wait-loading">' + T.error + "</p>";
        });
      });
  }

  load();
  setInterval(load, 5 * 60 * 1000);
})();
