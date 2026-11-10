// Studybook unit page behaviour: tabs, one audio engine, hide-to-recall, play all, the desktop
// stage (platform display), focus mode on phones, and where-you-left-off memory for the homepage.
(function () {
  'use strict';
  var body = document.body;
  var slug = body.dataset.unit;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return [].slice.call((r || document).querySelectorAll(s)); };
  function get(k, d) { try { var v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (e) { return d; } }
  function put(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  var desk = window.matchMedia('(min-width: 960px)');
  // A control's label: Korean in Korean mode, English in English and Lyric (see assets/line.css).
  function L(ko, en) { return '<span class="ui-ko">' + ko + '</span><span class="ui-en">' + en + '</span>'; }

  // ---- remember this unit for the homepage ----
  put('sb:last', slug);
  var seen = get('sb:seen', []);
  if (seen.indexOf(slug) === -1) { seen.push(slug); put('sb:seen', seen); }
  var cards = $$('.cards .card');
  function savePos(i) { put('sb:pos:' + slug, { i: i, n: cards.length }); }

  // sticky header height, so the desktop stage sits right under it
  var hdr = $('.usign');
  function setHdr() { document.documentElement.style.setProperty('--hdr', hdr.offsetHeight + 'px'); }
  setHdr(); window.addEventListener('resize', setHdr);

  // ---- audio engine: one clip at a time; the owner shows progress ----
  var audio = null, playingBtn = null, owner = null, seq = null;
  function mark(btn, on) {
    if (!btn) return;
    btn.classList.toggle('playing', on);
    var label = btn.querySelector('span');
    if (label) {
      if (on) { if (!btn.dataset.l) btn.dataset.l = label.innerHTML; label.innerHTML = L('재생 중', 'Playing'); }
      else if (btn.dataset.l) label.innerHTML = btn.dataset.l;
    }
  }
  function setOwner(el) {
    if (owner) { owner.classList.remove('speaking'); var i = $('.prog i', owner); if (i) i.style.width = '0'; }
    owner = el; if (owner) owner.classList.add('speaking');
  }
  function stop() { if (audio) audio.pause(); mark(playingBtn, false); setOwner(null); audio = null; playingBtn = null; }
  function play(btn, done, ownerEl) {
    stop();
    audio = new Audio(btn.dataset.au); playingBtn = btn; mark(btn, true);
    setOwner(ownerEl || btn.closest('.card'));
    var bar = owner ? $('.prog i', owner) : null;
    audio.ontimeupdate = function () { if (bar && audio && audio.duration) bar.style.width = (audio.currentTime / audio.duration * 100) + '%'; };
    audio.onended = function () { mark(btn, false); setOwner(null); if (done) done(); };
    audio.play().catch(function () { mark(btn, false); setOwner(null); if (done) done(); });
  }

  // ---- tabs ----
  var tabs = $$('.tabs [role="tab"]');
  function show(name, fromHash) {
    stopSeq(); stop();
    tabs.forEach(function (t) {
      var on = t.dataset.tab === name;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      t.tabIndex = on ? 0 : -1;
      $('#p-' + t.dataset.tab).classList.toggle('on', on);
      $('#a-' + t.dataset.tab).hidden = !on;
    });
    if (!fromHash) history.replaceState(null, '', '#' + name);
    window.scrollTo({ top: 0 });
  }
  tabs.forEach(function (t, i) {
    t.addEventListener('click', function () { show(t.dataset.tab); });
    t.addEventListener('keydown', function (e) {
      var d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
      if (!d) return;
      e.stopPropagation();
      var n = tabs[(i + d + tabs.length) % tabs.length]; n.focus(); show(n.dataset.tab);
    });
  });
  var start = (location.hash || '').slice(1);
  show(tabs.some(function (t) { return t.dataset.tab === start; }) ? start : 'cards', true);
  function onCards() { return $('#p-cards').classList.contains('on'); }

  // ---- desktop stage: the line now on the platform ----
  var stage = $('#stage'), sel = 0;
  var sImg = stage && $('.pic img', stage), sPic = stage && $('.pic', stage), sTop = stage && $('.ctop', stage),
    sKo = stage && $('.st-ko', stage), sEn = stage && $('.st-en', stage), sPlay = $('#stPlay'), sPrev = $('#stPrev'),
    sNext = $('#stNext'), sCount = stage && $('.st-count', stage);
  function stageReveal() { if (sKo) { sKo.classList.remove('hidden'); sKo.classList.add('shown'); sKo.removeAttribute('role'); } }
  function select(i, keepAudio, noScroll) {
    if (!stage || !cards.length) return;
    sel = Math.max(0, Math.min(cards.length - 1, i));
    if (!keepAudio && owner === stage) stop();
    var c = cards[sel], img = $('.pic img', c);
    cards.forEach(function (x, j) { x.classList.toggle('sel', j === sel); x.setAttribute('aria-current', j === sel ? 'true' : 'false'); });
    stage.style.setProperty('--lc', c.style.getPropertyValue('--lc'));
    sPic.className = $('.pic', c).className;
    sImg.src = img.getAttribute('src'); sImg.alt = img.alt;
    sTop.innerHTML = $('.ctop', c).innerHTML;
    sKo.innerHTML = $('.ko', c).innerHTML; sEn.innerHTML = $('.en', c).innerHTML;
    if (body.classList.contains('hide-ko')) { sKo.classList.add('hidden'); sKo.classList.remove('shown'); sKo.setAttribute('role', 'button'); } else stageReveal();
    sCount.textContent = (sel + 1) + ' / ' + cards.length;
    sPrev.disabled = sel === 0; sNext.disabled = sel === cards.length - 1;
    mapOn(c.dataset.sec); savePos(sel);
    if (desk.matches && !noScroll) {
      var r = c.getBoundingClientRect();
      if (r.top < (hdr.offsetHeight + 10) || r.bottom > window.innerHeight) c.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }
  }
  function stagePlay() {
    var b = $('.rplay', cards[sel]); if (!b) return;
    if (owner === stage && audio && !audio.paused) { stop(); return; }
    stageReveal(); play(b, null, stage); mark(sPlay, true);
    var a = audio; a.addEventListener('ended', function () { mark(sPlay, false); });
  }
  if (stage) {
    sPlay.addEventListener('click', function () { stopSeq(); stagePlay(); });
    sPrev.addEventListener('click', function () { stopSeq(); select(sel - 1); });
    sNext.addEventListener('click', function () { stopSeq(); select(sel + 1); });
    sKo.addEventListener('click', stageReveal);
    cards.forEach(function (c, i) {
      c.addEventListener('click', function (e) {
        if (!desk.matches || e.target.closest('[data-au]')) return;
        stopSeq(); select(i);
      });
    });
  }

  // ---- play all ----
  var playAll = $('#playAll');
  function setNow(i) {
    cards.forEach(function (c, j) { c.classList.toggle('now', j === i); });
    if (i >= 0) { mapOn(cards[i].dataset.sec); savePos(i); }
  }
  function stopSeq() {
    if (seq === null) return;
    seq = null; stop(); setNow(-1); mark(sPlay, false);
    playAll.setAttribute('aria-pressed', 'false'); $('span', playAll).innerHTML = L('전체 듣기', 'Play all');
  }
  function step() {
    if (seq === null) return;
    if (seq >= cards.length) { stopSeq(); return; }
    var c = cards[seq];
    if (desk.matches) {
      select(seq, true); stageReveal();
      play($('.rplay', c), next, stage); mark(sPlay, true);
    } else {
      setNow(seq); c.scrollIntoView({ block: 'center', behavior: 'smooth' });
      play($('.cplay', c), next);
    }
    function next() { if (seq !== null) { seq++; setTimeout(step, 450); } }
  }
  if (playAll) playAll.addEventListener('click', function () {
    if (seq !== null) { stopSeq(); return; }
    seq = desk.matches ? sel : 0; playAll.setAttribute('aria-pressed', 'true'); $('span', playAll).innerHTML = L('멈추기', 'Stop'); step();
  });

  // ---- clicks: audio, reveal, Q&A ----
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-au]');
    if (b && !b.closest('.focus')) {
      e.stopPropagation(); stopSeq();
      if (playingBtn === b && audio && !audio.ended) { stop(); return; }
      var c = b.closest('.card');
      if (c && desk.matches) { select(cards.indexOf(c), true); stageReveal(); play(b, function () { mark(sPlay, false); }, stage); mark(sPlay, true); return; }
      play(b); return;
    }
    var q = e.target.closest('.qa .q');
    if (q) { var qa = q.closest('.qa'); qa.classList.toggle('open'); q.setAttribute('aria-expanded', qa.classList.contains('open')); return; }
    var hid = e.target.closest('.ko, .vko, .ven');
    if (hid && !hid.closest('.focus') && !hid.closest('.stage') && !(desk.matches && hid.closest('.card'))) hid.classList.toggle('shown');
  });

  // ---- keyboard on desktop cards ----
  document.addEventListener('keydown', function (e) {
    if (!desk.matches || !onCards() || !stage || e.altKey || e.ctrlKey || e.metaKey) return;
    if (e.target.closest('input, textarea, [role="tab"]')) return;
    if (e.key === ' ' && !e.target.closest('button')) { e.preventDefault(); stopSeq(); stagePlay(); }
    else if (e.key === 'ArrowRight' || e.key === 'ArrowDown') { e.preventDefault(); stopSeq(); select(sel + 1); }
    else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') { e.preventDefault(); stopSeq(); select(sel - 1); }
    else if (e.key === 'k' || e.key === 'K') stageReveal();
  });

  // ---- toggles ----
  $$('[data-toggle]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var cls = btn.dataset.toggle, on = body.classList.toggle(cls);
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
      if (!on) $$('.shown').forEach(function (x) { x.classList.remove('shown'); });
      if (cls === 'hide-ko' && stage) {
        if (on) { sKo.classList.add('hidden'); sKo.classList.remove('shown'); sKo.setAttribute('role', 'button'); } else stageReveal();
      }
    });
  });
  var pr = $('#printFull'); if (pr) pr.addEventListener('click', function () { window.print(); });

  // ---- line map: jump to a section, follow the scroll ----
  var mapItems = $$('.map li');
  function mapOn(sec) { mapItems.forEach(function (li) { li.classList.toggle('on', li.dataset.sec === sec); }); }
  mapItems.forEach(function (li) {
    $('button', li).addEventListener('click', function () {
      var c = $('.card[data-sec="' + li.dataset.sec + '"]');
      if (!c) return;
      if (desk.matches) { stopSeq(); select(cards.indexOf(c)); }
      else c.scrollIntoView({ block: 'start', behavior: 'smooth' });
    });
  });
  if ('IntersectionObserver' in window && cards.length) {
    var io = new IntersectionObserver(function (es) {
      if (desk.matches) return;
      es.forEach(function (en) {
        if (en.isIntersecting && seq === null) {
          var i = cards.indexOf(en.target); mapOn(en.target.dataset.sec); savePos(i);
        }
      });
    }, { rootMargin: '-45% 0px -45% 0px' });
    cards.forEach(function (c) { io.observe(c); });
  }
  var pos = get('sb:pos:' + slug, null);
  var startAt = pos && pos.i < cards.length ? pos.i : 0;
  if (cards.length) { mapOn(cards[startAt].dataset.sec); if (stage) select(startAt, false, true); }

  // ---- focus mode (phones) ----
  var focus = $('#focus');
  if (focus && cards.length) {
    var fi = 0, fAudio = null;
    var track = $('.f-track', focus), dot = $('.f-dot', focus);
    cards.forEach(function (c) {
      var i = document.createElement('i'); i.style.setProperty('--lc', c.style.getPropertyValue('--lc')); track.insertBefore(i, dot);
    });
    var segs = $$('i', track);
    var fPic = $('.pic img', focus), fPicBox = $('.pic', focus), fTop = $('.ctop', focus), fKo = $('.ko', focus), fEn = $('.en', focus),
      fHint = $('.f-hint', focus), fListen = $('#fListen'), fPrev = $('#fPrev'), fNext = $('#fNext'), fCount = $('.f-count', focus);
    function fStop() { if (fAudio) fAudio.pause(); fAudio = null; fListen.classList.remove('playing'); }
    function reveal() { fKo.classList.remove('hidden'); fKo.removeAttribute('role'); fKo.removeAttribute('tabindex'); fHint.hidden = true; }
    function render(i) {
      fStop(); fi = Math.max(0, Math.min(cards.length - 1, i)); savePos(fi);
      var c = cards[fi], img = $('.pic img', c);
      focus.style.setProperty('--lc', c.style.getPropertyValue('--lc'));
      fPic.src = img.getAttribute('src'); fPic.alt = img.alt;
      fPicBox.className = $('.pic', c).className;
      fTop.innerHTML = $('.ctop', c).innerHTML;
      fKo.innerHTML = $('.ko', c).innerHTML; fEn.innerHTML = $('.en', c).innerHTML;
      fKo.classList.add('hidden'); fKo.setAttribute('role', 'button'); fKo.setAttribute('tabindex', '0');
      fKo.setAttribute('aria-label', 'Reveal the text'); fHint.hidden = false;
      fCount.textContent = (fi + 1) + ' / ' + cards.length;
      segs.forEach(function (s, j) { s.classList.toggle('done', j <= fi); });
      dot.style.left = ((fi + 0.5) / cards.length * 100) + '%';
      fPrev.disabled = fi === 0; $('span', fNext).innerHTML = fi === cards.length - 1 ? L('끝 · Done', 'Done') : L('다음 · Next', 'Next');
    }
    function open() {
      stopSeq(); stop();
      var p = get('sb:pos:' + slug, null);
      render(p && p.i < cards.length ? p.i : 0);
      focus.hidden = false; body.style.overflow = 'hidden'; $('.f-close', focus).focus();
    }
    function close() {
      fStop(); focus.hidden = true; body.style.overflow = '';
      cards[fi].scrollIntoView({ block: 'center' }); setNow(-1); mapOn(cards[fi].dataset.sec); $('#openFocus').focus();
    }
    $('#openFocus').addEventListener('click', open);
    $('.f-close', focus).addEventListener('click', close);
    fKo.addEventListener('click', reveal);
    fKo.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); reveal(); } });
    fListen.addEventListener('click', function () {
      if (fAudio && !fAudio.paused) { fStop(); return; }
      reveal(); fAudio = new Audio($('[data-au]', cards[fi]).dataset.au); fListen.classList.add('playing');
      fAudio.onended = function () { fListen.classList.remove('playing'); };
      fAudio.play().catch(function () { fListen.classList.remove('playing'); });
    });
    fPrev.addEventListener('click', function () { render(fi - 1); });
    fNext.addEventListener('click', function () { if (fi === cards.length - 1) close(); else render(fi + 1); });
    document.addEventListener('keydown', function (e) {
      if (focus.hidden) return;
      if (e.key === 'Escape') close();
      else if (e.key === 'ArrowRight') render(fi + 1);
      else if (e.key === 'ArrowLeft') render(fi - 1);
    });
    var x0 = null, y0 = null;
    focus.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; }, { passive: true });
    focus.addEventListener('touchend', function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0, dy = e.changedTouches[0].clientY - y0; x0 = null;
      if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy) * 1.5) render(fi + (dx < 0 ? 1 : -1));
    });
  }

  if ('serviceWorker' in navigator) navigator.serviceWorker.register('../sw.js', { scope: '../' }).catch(function () {});
})();
