(() => {
  'use strict';
  const depth = parseInt(document.body.dataset.mdepth || '0', 10);
  const mPre = depth === 0 ? '' : '../';

  // ---- Shared localStorage for exam practice (compatible with Desktop!) ----
  const readPractice = () => { try { return JSON.parse(localStorage.getItem('sd5979-revision-v2') || '{}'); } catch { return {}; } };
  let savedPractice = readPractice();
  const savePractice = () => { try { localStorage.setItem('sd5979-revision-v2', JSON.stringify(savedPractice)); } catch {} };

  document.querySelectorAll('.practice').forEach(p => {
    const id = p.dataset.item;
    const state = savedPractice[id] || {};
    p.querySelectorAll('[data-choice]').forEach(b => {
      b.setAttribute('aria-pressed', String(b.dataset.choice === state.choice));
      b.addEventListener('click', () => {
        savedPractice[id] = { ...(savedPractice[id] || {}), choice: b.dataset.choice };
        savePractice();
        p.querySelectorAll('[data-choice]').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
      });
    });
    const mark = p.querySelector('.bookmark');
    if (mark) {
      const show = () => {
        const on = !!savedPractice[id]?.mistake;
        mark.setAttribute('aria-pressed', String(on));
        mark.textContent = on ? '★ 已加入错题本' : '☆ 加入错题本';
      };
      show();
      mark.addEventListener('click', () => {
        savedPractice[id] = { ...(savedPractice[id] || {}), mistake: !savedPractice[id]?.mistake };
        savePractice();
        show();
      });
    }
    const ta = p.querySelector('textarea');
    if (ta) {
      ta.value = state.text || '';
      ta.addEventListener('input', () => {
        savedPractice[id] = { ...(savedPractice[id] || {}), text: ta.value };
        savePractice();
      });
    }
  });

  // ---- Mobile exam filter ----
  const rSearch = document.querySelector('#review-search');
  if (rSearch) {
    const kind = document.querySelector('#kind-filter');
    const lec = document.querySelector('#lecture-filter');
    const mistake = document.querySelector('#mistake-filter');
    const cards = [...document.querySelectorAll('.question-card')];
    const filter = () => {
      const q = rSearch.value.trim().toLowerCase();
      let n = 0;
      cards.forEach(c => {
        const ok = c.textContent.toLowerCase().includes(q)
          && (!kind.value || c.dataset.kind === kind.value)
          && (!lec.value || c.dataset.lecture === lec.value)
          && (!mistake.checked || savedPractice[c.dataset.id]?.mistake);
        c.hidden = !ok;
        if (ok) n++;
      });
      const cnt = document.querySelector('#filter-count');
      if (cnt) cnt.textContent = `显示 ${n} / ${cards.length} 组`;
      const emp = document.querySelector('.empty-state');
      if (emp) emp.hidden = n > 0;
    };
    [rSearch, kind, lec, mistake].forEach(el => el && el.addEventListener('input', filter));
    filter();
    window.addEventListener('pageshow', () => { savedPractice = readPractice(); filter(); });
  }

  // ---- Mobile glossary quick filter ----
  const gSearch = document.querySelector('#m-glossary-q');
  if (gSearch) {
    const items = [...document.querySelectorAll('.m-gitem')];
    const gCnt = document.querySelector('#m-glossary-cnt');
    gSearch.addEventListener('input', () => {
      const q = gSearch.value.trim().toLowerCase();
      let n = 0;
      items.forEach(el => {
        const ok = !q || el.textContent.toLowerCase().includes(q);
        el.hidden = !ok;
        if (ok) n++;
      });
      if (gCnt) gCnt.textContent = `共 ${n} / ${items.length} 条`;
    });
  }

  // ---- Mobile home bilingual search ----
  const qInput = document.querySelector('#m-q');
  const qRes = document.querySelector('#m-qres');
  if (qInput && qRes && window.SD5979_SEARCH) {
    const label = { slide: '讲义', term: '术语', exam: '例题' };
    const mkHref = x => {
      if (x.k === 'term') return mPre + 'glossary.html#t-' + encodeURIComponent(x.key || x.t);
      if (x.k === 'exam') {
        const id = x.id || x.t.split(' ')[0];
        return mPre + 'exam/' + x.lid + '-exam.html#' + id;
      }
      return mPre + 'lectures/' + x.lid + '.html#' + x.lid + '-s' + x.s;
    };
    let timer = null;
    qInput.addEventListener('input', () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        const kw = qInput.value.trim().toLowerCase();
        if (!kw) { qRes.innerHTML = ''; return; }
        const hits = window.SD5979_SEARCH.filter(x =>
          (x.t || '').toLowerCase().includes(kw) || (x.lid || '').toLowerCase().includes(kw)
        ).slice(0, 40);
        if (!hits.length) { qRes.innerHTML = '<div class="qr">没有匹配结果</div>'; return; }
        qRes.innerHTML = hits.map(x =>
          `<div class="qr"><a href="${mkHref(x)}">[${label[x.k] || ''}] ${x.lid} · 第 ${x.s} 页</a><span>${(x.t || '').slice(0, 95).replace(/</g, '&lt;')}</span></div>`
        ).join('');
      }, 120);
    });
  }

  // ---- Fullscreen Image Viewer (pinch/zoom friendly) ----
  const imgDlg = document.createElement('dialog');
  imgDlg.className = 'm-img-dialog';
  imgDlg.setAttribute('aria-label', '原页大图查看');
  imgDlg.innerHTML = '<div class="m-img-bar"><span id="mi-title"></span><button type="button" id="mi-zoom">放大 2×</button><a id="mi-pdf" target="_blank" rel="noopener">PDF</a><button type="button" id="mi-close">关闭</button></div><div class="m-img-stage"><img id="mi-img" alt="课件原页"></div>';
  document.body.append(imgDlg);
  const miStage = imgDlg.querySelector('.m-img-stage');
  const miZoom = imgDlg.querySelector('#mi-zoom');
  document.addEventListener('click', e => {
    const a = e.target.closest('a[data-image]');
    if (!a) return;
    e.preventDefault();
    imgDlg.querySelector('#mi-img').src = a.dataset.image;
    imgDlg.querySelector('#mi-title').textContent = a.dataset.label || '';
    imgDlg.querySelector('#mi-pdf').href = a.dataset.pdf || a.dataset.image;
    miStage.classList.remove('zoom');
    miZoom.textContent = '放大 2×';
    imgDlg.showModal();
  });
  imgDlg.querySelector('#mi-close').addEventListener('click', () => imgDlg.close());
  miZoom.addEventListener('click', () => {
    const on = miStage.classList.toggle('zoom');
    miZoom.textContent = on ? '适应屏幕' : '放大 2×';
  });

  // ---- Tap-to-Explain Term Definition Bottom Sheet ----
  const termDlg = document.createElement('dialog');
  termDlg.className = 'm-sheet';
  termDlg.setAttribute('aria-label', '课程术语解释');
  termDlg.innerHTML = '<div class="sheet-head"><strong id="mt-title"></strong><button type="button" class="sheet-close" id="mt-close">关闭</button></div><div class="sheet-body" id="mt-body"></div>';
  document.body.append(termDlg);
  termDlg.querySelector('#mt-close').addEventListener('click', () => termDlg.close());
  termDlg.addEventListener('click', e => { if (e.target === termDlg) termDlg.close(); });

  const esc = s => String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  document.addEventListener('click', e => {
    const el = e.target.closest('[data-term]');
    if (!el) return;
    const key = el.getAttribute('data-term');
    const t = (window.SD5979_TERMS || {})[key];
    if (!t) return;
    termDlg.querySelector('#mt-title').textContent = t.term;
    const statusNote = t.status === 'occurrence_only'
      ? '<p class="note">注：本词在课件中仅出现，无独立定义句，以下为原句上下文。</p>' : '';
    const link = `${mPre}lectures/${t.lecture}.html#${t.lecture}-s${t.slide}`;
    termDlg.querySelector('#mt-body').innerHTML =
      `<h3 style="margin:0 0 8px;color:#146957">${esc(t.zh)}</h3>`
      + statusNote
      + `<div class="term-en-box">${esc(t.en)}</div>`
      + `<div class="term-zh-box">${esc(t.zhdef)}</div>`
      + `<a class="pill" href="${link}">跳转到定义原页：${esc(t.lecture)} · 第 ${t.slide} 页 ↗</a>`;
    termDlg.showModal();
  });

  // ---- Mobile Lecture Reader (Card Mode + Swipe + Scroll Mode + Jump Drawer + Progress) ----
  const slidesWrap = document.querySelector('.m-slides');
  if (slidesWrap) {
    const lid = slidesWrap.dataset.lecture;
    const slides = [...slidesWrap.querySelectorAll('.m-slide')];
    const total = slides.length;
    const progKey = 'sd5979-m-prog-' + lid;
    let cur = 1;

    const btnPrev = document.querySelector('#pg-prev');
    const btnNext = document.querySelector('#pg-next');
    const btnJump = document.querySelector('#pg-jump');
    const modeBtns = [...document.querySelectorAll('[data-mode-btn]')];
    const viewBtns = [...document.querySelectorAll('[data-view-btn]')];
    const hlBtn = document.querySelector('#m-hl-toggle');

    // Jump drawer dialog
    const jumpDlg = document.createElement('dialog');
    jumpDlg.className = 'm-sheet';
    jumpDlg.setAttribute('aria-label', '选择页码');
    jumpDlg.innerHTML = `<div class="sheet-head"><strong>${lid} · 跳转到任意页（共 ${total} 页）</strong><button type="button" class="sheet-close" id="mj-close">关闭</button></div><div class="sheet-body"><div class="jump-grid" id="mj-grid"></div></div>`;
    document.body.append(jumpDlg);
    const grid = jumpDlg.querySelector('#mj-grid');
    for (let i = 1; i <= total; i++) {
      const b = document.createElement('button');
      b.type = 'button';
      b.textContent = String(i);
      b.dataset.slide = String(i);
      b.addEventListener('click', () => {
        jumpDlg.close();
        goTo(i, true);
      });
      grid.append(b);
    }
    jumpDlg.querySelector('#mj-close').addEventListener('click', () => jumpDlg.close());
    jumpDlg.addEventListener('click', e => { if (e.target === jumpDlg) jumpDlg.close(); });

    const updatePager = () => {
      if (btnJump) btnJump.textContent = `第 ${cur} / ${total} 页 ▾`;
      if (btnPrev) btnPrev.disabled = cur <= 1;
      if (btnNext) btnNext.disabled = cur >= total;
      grid.querySelectorAll('button').forEach(b => b.classList.toggle('is-active', Number(b.dataset.slide) === cur));
    };

    const goTo = (n, scrollTop = false) => {
      n = Math.max(1, Math.min(total, n));
      cur = n;
      try { localStorage.setItem(progKey, String(cur)); } catch {}
      slides.forEach((el, idx) => el.classList.toggle('is-current', idx + 1 === cur));
      updatePager();
      if (slidesWrap.dataset.mode === 'scroll') {
        slides[cur - 1]?.scrollIntoView({ behavior: 'auto', block: 'start' });
      } else if (scrollTop) {
        window.scrollTo(0, 0);
      }
      const sw = document.querySelector('.m-switch');
      if (sw && sw.dataset.baseHref) sw.href = `${sw.dataset.baseHref}#${lid}-s${cur}`;
    };

    const setMode = mode => {
      if (!['card', 'scroll'].includes(mode)) mode = 'card';
      slidesWrap.dataset.mode = mode;
      modeBtns.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.modeBtn === mode)));
      try { localStorage.setItem('sd5979-m-mode', mode); } catch {}
      if (mode === 'scroll') {
        slides[cur - 1]?.scrollIntoView({ behavior: 'auto', block: 'start' });
      } else {
        goTo(cur, true);
      }
    };

    const setView = view => {
      if (!['both', 'zh', 'en'].includes(view)) view = 'both';
      slidesWrap.dataset.view = view;
      viewBtns.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.viewBtn === view)));
      try { localStorage.setItem('sd5979-m-view', view); } catch {}
    };

    const setHl = on => {
      slidesWrap.classList.toggle('no-hl', !on);
      if (hlBtn) hlBtn.setAttribute('aria-pressed', String(on));
      try { localStorage.setItem('sd5979-term-hl', on ? '1' : '0'); } catch {}
    };

    modeBtns.forEach(b => b.addEventListener('click', () => setMode(b.dataset.modeBtn)));
    viewBtns.forEach(b => b.addEventListener('click', () => setView(b.dataset.viewBtn)));
    if (hlBtn) hlBtn.addEventListener('click', () => setHl(slidesWrap.classList.contains('no-hl')));
    if (btnPrev) btnPrev.addEventListener('click', () => goTo(cur - 1, true));
    if (btnNext) btnNext.addEventListener('click', () => goTo(cur + 1, true));
    if (btnJump) btnJump.addEventListener('click', () => jumpDlg.showModal());

    // Touch swipe left/right in card mode (ignores horizontal table/math scrolls)
    let sx = 0, sy = 0, tracking = false;
    slidesWrap.addEventListener('touchstart', e => {
      if (slidesWrap.dataset.mode !== 'card' || e.touches.length !== 1) return;
      if (e.target.closest('.zh-table-wrap, .zh-math-block')) return;
      sx = e.touches[0].clientX;
      sy = e.touches[0].clientY;
      tracking = true;
    }, { passive: true });
    slidesWrap.addEventListener('touchend', e => {
      if (!tracking) return;
      tracking = false;
      const dx = e.changedTouches[0].clientX - sx;
      const dy = e.changedTouches[0].clientY - sy;
      if (Math.abs(dx) > 65 && Math.abs(dx) > Math.abs(dy) * 1.6) {
        if (dx < 0 && cur < total) goTo(cur + 1, true);
        if (dx > 0 && cur > 1) goTo(cur - 1, true);
      }
    }, { passive: true });

    const parseHash = () => {
      const m = location.hash.match(new RegExp('^#' + lid + '-s(\\d+)$'));
      return m ? parseInt(m[1], 10) : null;
    };
    window.addEventListener('hashchange', () => {
      const h = parseHash();
      if (h) goTo(h, true);
    });

    try {
      const savedView = localStorage.getItem('sd5979-m-view');
      if (savedView) setView(savedView);
      const savedHl = localStorage.getItem('sd5979-term-hl');
      if (savedHl === '0') setHl(false);
      const savedMode = localStorage.getItem('sd5979-m-mode') || 'card';
      const initSlide = parseHash() || parseInt(localStorage.getItem(progKey) || '1', 10) || 1;
      cur = Math.max(1, Math.min(total, initSlide));
      slidesWrap.dataset.mode = savedMode;
      modeBtns.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.modeBtn === savedMode)));
      goTo(cur, false);
    } catch {
      goTo(1, false);
    }
  }
})();
