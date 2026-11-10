// The text switch: English, Korean or Lyric (Korean in English letters). Loaded in <head> so the
// page paints in the chosen mode, and shared by the homepage and every unit. The choice is remembered.
(function () {
  'use strict';
  var KEY = 'sb:script', root = document.documentElement, mode = 'ko';
  try { var v = localStorage.getItem(KEY); if (v === 'en' || v === 'ko' || v === 'ro') mode = v; } catch (e) {}
  root.setAttribute('data-script', mode);
  function sync() {
    [].forEach.call(document.querySelectorAll('.script [data-set]'), function (b) {
      b.setAttribute('aria-pressed', b.getAttribute('data-set') === mode ? 'true' : 'false');
    });
  }
  document.addEventListener('DOMContentLoaded', sync);
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('.script [data-set]');
    if (!b) return;
    e.stopPropagation();
    mode = b.getAttribute('data-set');
    root.setAttribute('data-script', mode);
    try { localStorage.setItem(KEY, mode); } catch (err) {}
    sync();
    window.dispatchEvent(new Event('resize'));  // sticky header and the homepage marker re-measure
  }, true);
})();
