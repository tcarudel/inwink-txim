/*! txim v0.1.0 | JS optionnel : mode apparition, repli Firefox, survols Inclinaison et Projecteur | https://github.com/tcarudel/inwink-txim */
/* txim : JS optionnel.
   - Mode « joué à l'apparition » (classe txim-apparition) : pose data-txim-arme puis data-txim-vu.
   - Navigateurs sans animation-timeline (Firefox) : bascule aussi les blocs « défilement » en apparition.
   - Survols Inclinaison et Projecteur : pose --txim-px / --txim-py / --txim-src.
   Ne modifie jamais className ni la structure : uniquement des attributs data-* et des variables CSS.
   Surveille le DOM (inwink est une application React : les blocs arrivent sans rechargement). */
(function () {
  "use strict";
  if (window.TXIM) return;
  var CW = ".content-wrapper";
  var ENTREE = '[class*="txim-i-"],[class*="txim-t-"]';
  var POINTEUR = ".txim-h-inclinaison,.txim-h-projecteur";
  var supporte = !!(window.CSS && CSS.supports && CSS.supports("animation-timeline", "view()"));
  var armes = new Map(), suivis = new Map(), ios = {};

  function blocs(sel) {                      // .content-wrapper concernés, classe posée sur #ct ou sur le wrapper
    var s = new Set();
    document.querySelectorAll(sel).forEach(function (el) {
      if (el.matches(CW)) s.add(el); else el.querySelectorAll(CW).forEach(function (c) { s.add(c); });
    });
    return s;
  }
  function seuil(cw) {
    var v = parseFloat(getComputedStyle(cw).getPropertyValue("--txim-seuil"));
    return isNaN(v) ? 25 : v;
  }
  function observateur(m) {                  // un IntersectionObserver par hauteur de déclenchement
    return ios[m] || (ios[m] = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting || e.boundingClientRect.bottom <= 0) e.target.setAttribute("data-txim-vu", "");
      });
    }, { rootMargin: "0px 0px -" + m + "% 0px" }));
  }
  function rejouer(cw) {                     // remet à zéro (le bloc est ressorti par le bas)
    cw.removeAttribute("data-txim-vu");
    cw.setAttribute("data-txim-reset", "");
    requestAnimationFrame(function () { requestAnimationFrame(function () { cw.removeAttribute("data-txim-reset"); }); });
  }
  var sortie = new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      if (!e.isIntersecting && e.boundingClientRect.top > 0 && e.target.hasAttribute("data-txim-vu")) rejouer(e.target);
    });
  });
  function armer(cw) {
    var m = seuil(cw), a = armes.get(cw);
    if (a && a.m === m) return;
    if (a) a.io.unobserve(cw); else sortie.observe(cw);
    cw.setAttribute("data-txim-arme", "");
    var io = observateur(m); io.observe(cw);
    armes.set(cw, { io: io, m: m });
  }
  function desarmer(cw) {
    var a = armes.get(cw);
    a.io.unobserve(cw); sortie.unobserve(cw);
    ["data-txim-arme", "data-txim-vu", "data-txim-reset"].forEach(function (n) { cw.removeAttribute(n); });
    armes.delete(cw);
  }
  function suivre(cw) {
    var box = cw.querySelector(".picture-wrapper");
    if (!box) return;
    var img = box.querySelector("img");
    function src() { if (img) box.style.setProperty("--txim-src", 'url("' + (img.currentSrc || img.src).replace(/"/g, "%22") + '")'); }
    function bouge(e) {
      var r = box.getBoundingClientRect();
      box.style.setProperty("--txim-px", ((e.clientX - r.left) / r.width).toFixed(3));
      box.style.setProperty("--txim-py", ((e.clientY - r.top) / r.height).toFixed(3));
    }
    function quitte() { box.style.setProperty("--txim-px", ".5"); box.style.setProperty("--txim-py", ".5"); }
    src();
    if (img) img.addEventListener("load", src);
    cw.addEventListener("pointermove", bouge);
    cw.addEventListener("pointerleave", quitte);
    cw.setAttribute("data-txim-pointeur", "");
    suivis.set(cw, function () {
      if (img) img.removeEventListener("load", src);
      cw.removeEventListener("pointermove", bouge);
      cw.removeEventListener("pointerleave", quitte);
      cw.removeAttribute("data-txim-pointeur");
      ["--txim-src", "--txim-px", "--txim-py"].forEach(function (p) { box.style.removeProperty(p); });
    });
  }
  function scan() {
    var a = blocs(".txim-apparition");
    if (!supporte) blocs(ENTREE).forEach(function (c) { a.add(c); });
    armes.forEach(function (_, cw) { if (!a.has(cw) || !cw.isConnected) desarmer(cw); });
    a.forEach(armer);
    var p = blocs(POINTEUR);
    suivis.forEach(function (stop, cw) { if (!p.has(cw) || !cw.isConnected) { stop(); suivis.delete(cw); } });
    p.forEach(function (cw) { if (!suivis.has(cw)) suivre(cw); });
  }
  var prevu = 0;
  function planifier() { if (!prevu) prevu = requestAnimationFrame(function () { prevu = 0; scan(); }); }
  new MutationObserver(planifier).observe(document.documentElement,
    { childList: true, subtree: true, attributes: true, attributeFilter: ["class"] });
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", scan); else scan();

  window.TXIM = {
    version: "0.1.0",
    scan: scan,
    rejouer: function () {                   // relance les blocs en mode apparition (utile pour tester)
      armes.forEach(function (a, cw) { rejouer(cw); a.io.unobserve(cw); a.io.observe(cw); });
    }
  };
})();
