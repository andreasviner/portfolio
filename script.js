/* ============================================================
   Andreas Lindeman portfolio script
   - Loads timeline entries from projects_data/manifest.json
   - Single-lane swimlane (desktop) with seeded-random vertical
     placement so categories share a row, distinguished by color
   - Mobile list view
   - Filters, tooltip, typewriter, navigation
   ============================================================ */

(() => {
  'use strict';

  // ----------------------------------------------------------
  // Config
  // ----------------------------------------------------------
  const MANIFEST_URL = 'projects_data/manifest.json';
  const DATA_DIR     = 'projects_data/';
  const MOBILE_BREAK = 900;       // px – below this, switch to list view
  const PX_PER_YEAR  = 180;       // desktop: min horizontal pixels per year
  const LANE_ROWS    = 12;        // discrete vertical slots in the single lane
  const ROW_HEIGHT   = 42;        // px per slot; larger to fit importance-scaled bars
  const TOP_PAD      = 24;        // px from axis to first slot
  // mobile vertical swimlane: time runs down the Y axis, projects packed into a
  // few horizontal lanes (see assignSlots + renderVerticalSwimlane).
  const PX_PER_YEAR_V = 150;      // mobile: vertical pixels per year
  const V_TOP_PAD     = 18;       // mobile: px above the newest year
  const V_AXIS_W      = 30;       // mobile: left gutter reserved for year labels
  const V_SLOT_PAD    = 0.5;      // mobile: scale on the lane-packing time pad
                                  //         (desktop uses 1; compact nodes < 1)
  const CATEGORY_FILTERS = new Set(['work', 'school', 'hobby']);
  let firstRender = true;

  // ----------------------------------------------------------
  // State
  // ----------------------------------------------------------
  let entries = [];
  let activeFilter = 'all';
  let minYear = null;
  let maxYear = null;      // last integer year shown on the axis
  let rawMaxYear = null;   // fractional right-edge of the timeline (today + buffer)
  let currentYear = new Date().getFullYear();

  // ----------------------------------------------------------
  // DOM
  // ----------------------------------------------------------
  const $loading  = document.getElementById('timeline-loading');
  const $swim     = document.getElementById('swimlane');
  const $list     = document.getElementById('timeline-list');
  const $tooltip  = document.getElementById('tooltip');
  const $filters  = document.querySelectorAll('.filter-chip');
  const $year     = document.getElementById('year');
  const $yearsCoding = document.getElementById('years-coding');

  // Backdrop behind the mobile detail sheet (tap to dismiss). closeSheet is a
  // hoisted function declaration, so referencing it here is fine.
  const $backdrop = document.createElement('div');
  $backdrop.className = 'sheet-backdrop';
  $backdrop.setAttribute('aria-hidden', 'true');
  document.body.appendChild($backdrop);
  $backdrop.addEventListener('click', closeSheet);
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && $tooltip.classList.contains('is-sheet')) closeSheet();
  });

  if ($year) $year.textContent = currentYear;
  if ($yearsCoding) $yearsCoding.textContent = currentYear - 2012;

  // ----------------------------------------------------------
  // Typewriter (hero rotating phrase)
  // ----------------------------------------------------------
  const TYPE_PHRASES = [
    'complete production projects.',
    'machine learning algorithms.',
    'complete AI frameworks.',
    'RC cars with infinite range.',
    'self-improving algorithms.',
    'accurate and robust neural networks.',
    'FPGA filters from scratch.',
    'custom analog ADC circuits.',
    '3D printers from the chassis up.',
    'vision systems on tiny chips.',
    'voice assistants from scratch.',
    'robots that draw.',
    'embedded systems that learn.',
    'tools nobody else wrote yet.',
    'models that run on a single board.',
    'audio gear from discrete parts.',
    'data pipelines at scale.',
    'control loops that tune themselves.',
    'PCBs that route around the rules.',
  ];

  function startTypewriter() {
    const $tw = document.getElementById('typewriter');
    if (!$tw) return;

    let phraseIdx = 0;
    let charIdx = 0;
    let typing = true;

    const TYPE_MS  = 55;
    const ERASE_MS = 28;
    const HOLD_MS  = 1800;

    function tick() {
      const phrase = TYPE_PHRASES[phraseIdx];
      if (typing) {
        charIdx++;
        $tw.textContent = phrase.slice(0, charIdx);
        if (charIdx >= phrase.length) {
          typing = false;
          setTimeout(tick, HOLD_MS);
          return;
        }
        setTimeout(tick, TYPE_MS);
      } else {
        charIdx--;
        $tw.textContent = phrase.slice(0, charIdx);
        if (charIdx <= 0) {
          typing = true;
          phraseIdx = (phraseIdx + 1) % TYPE_PHRASES.length;
        }
        setTimeout(tick, ERASE_MS);
      }
    }
    tick();
  }
  startTypewriter();

  // ----------------------------------------------------------
  // Load data
  // ----------------------------------------------------------
  async function loadData() {
    try {
      const manifestRes = await fetch(MANIFEST_URL);
      if (!manifestRes.ok) throw new Error(`manifest ${manifestRes.status}`);
      const manifest = await manifestRes.json();

      // each manifest item is a folder name; the entry data lives at
      // projects_data/<folder>/info.json. Extra assets (images, etc.)
      // can live alongside it in the same folder.
      const fetches = manifest.entries.map(folder =>
        fetch(`${DATA_DIR}${folder}/info.json`)
          .then(r => {
            if (!r.ok) throw new Error(`${folder} ${r.status}`);
            return r.json();
          })
          .then(data => ({ ...data, _folder: `${DATA_DIR}${folder}` }))
          .catch(err => {
            console.warn('Skipping bad entry', folder, err);
            return null;
          })
      );

      const results = await Promise.all(fetches);
      entries = results.filter(Boolean).map(normalizeEntry);

      entries.sort((a, b) => a.startVal - b.startVal);

      const startYears = entries.map(e => Math.floor(e.startVal));
      const endValues  = entries.map(e => e.endVal);
      minYear = Math.min(...startYears);
      // Right edge of the timeline: roughly "today + 1 month", extended only
      // if some entry actually runs past that. Avoids the dead year-and-a-bit
      // of empty space that Math.ceil(presentVal) creates.
      const todayVal = currentYear + new Date().getMonth() / 12;
      rawMaxYear = Math.max(todayVal + 1 / 12, ...endValues);
      maxYear = Math.floor(rawMaxYear);

      $loading.classList.add('hidden');
      render();
      window.addEventListener('resize', debounce(render, 150));
    } catch (err) {
      console.error('Failed to load timeline', err);
      $loading.innerHTML = '<p style="color:var(--nda)">Couldn\'t load timeline data. Check the console.</p>';
      // Degrade to the real, semantic project list (normally hidden for JS
      // users by CSS). Inline style beats the stylesheet's display:none.
      const fb = document.querySelector('.seo-fallback');
      if (fb) fb.style.display = 'block';
    }
  }

  // ----------------------------------------------------------
  // Normalize an entry
  // ----------------------------------------------------------
  function normalizeEntry(e) {
    const startVal = toYearVal(e.start);
    let endVal;
    if (!e.end || e.end === e.start) {
      endVal = startVal;
    } else if (e.end === 'present') {
      endVal = currentYear + (new Date().getMonth() / 12);
    } else {
      endVal = toYearVal(e.end, true);
    }

    const isRange = endVal - startVal >= 0.25;

    // importance: clamp to 1..100, default to 40
    const impRaw = typeof e.importance === 'number' ? e.importance : 40;
    const importance = Math.max(1, Math.min(100, impRaw));

    return {
      ...e,
      startVal,
      endVal,
      isRange,
      isProject: !!e.isProject,
      types: Array.isArray(e.types) ? e.types : [],
      importance,
      importanceNorm: importance / 100, // 0..1
      isClickable: !!e.projectPage,
      // hideOnMobile: legacy flag from the old mobile list (which hid
      // biographical entries to save scroll space). The vertical swimlane packs
      // them into lanes instead, so every entry now renders in both views; the
      // flag is preserved on the object but no longer suppresses anything.
      hideOnMobile: !!e.hideOnMobile,
    };
  }

  function toYearVal(s, isEnd = false) {
    if (typeof s === 'number') return s;
    if (!s) return null;
    const parts = s.split('-');
    const y = parseInt(parts[0], 10);
    if (parts.length === 1) {
      return isEnd ? y + 0.999 : y;
    }
    const m = parseInt(parts[1], 10);
    return y + (m - 1) / 12;
  }

  // ----------------------------------------------------------
  // Seeded hash → [0, 1). Used so each entry has a stable
  // pseudo-random vertical position across reloads.
  // ----------------------------------------------------------
  function hash01(str) {
    let h = 2166136261;
    for (let i = 0; i < str.length; i++) {
      h ^= str.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    // mix
    h ^= h >>> 13;
    h = Math.imul(h, 1274126177);
    h ^= h >>> 16;
    return ((h >>> 0) % 100000) / 100000;
  }

  // ----------------------------------------------------------
  // Importance-aware, collision-free slot assignment.
  //
  // Shared by the desktop swimlane (slots = vertical rows, time on the X axis)
  // and the mobile vertical swimlane (slots = horizontal lanes, time on the Y
  // axis). Heaviest entries are placed first and biased toward the centre band
  // so the eye lands on them; lighter ones drift toward the edges, with
  // deterministic hash jitter so the layout looks organic rather than striped.
  // Within a slot, two entries never overlap in time — a per-entry pad reserves
  // room for the label/bar. If every slot collides at a given time, the
  // least-bad slot is chosen. Sets entry._slot ∈ [0, slotCount).
  //
  // padScale scales the time-pad: 1 on desktop (wide horizontal labels reserve
  // a lot of time-width); < 1 on mobile, where compact nodes need less
  // time-separation to read cleanly, which packs more projects per band.
  // ----------------------------------------------------------
  function assignSlots(list, slotCount, padScale) {
    const usage = []; // usage[i] = array of {start, end} intervals already taken
    for (let i = 0; i < slotCount; i++) usage.push([]);

    const center = (slotCount - 1) / 2;
    const ordered = list.slice().sort((a, b) => b.importance - a.importance);

    ordered.forEach(entry => {
      const start = entry.startVal;
      const end   = entry.isRange ? entry.endVal : start;
      const basePad = entry.isRange ? 0.04 : 0.18;
      const labelPad = (basePad + entry.importanceNorm * 0.5) * padScale;
      const reqStart = start - labelPad;
      const reqEnd   = end + labelPad;

      // Hash-driven jitter for the preferred slot within the band.
      const seed = hash01(entry.id || entry.title);
      // Heavier → narrower band around centre; lighter → wider band to the edges.
      const bandHalf = (slotCount / 2) * (1.05 - entry.importanceNorm * 0.55);
      const direction = seed < 0.5 ? -1 : 1;
      const intoBand  = ((seed * 2) % 1);              // 0..1
      let preferred = Math.round(center + direction * intoBand * bandHalf);
      preferred = Math.max(0, Math.min(slotCount - 1, preferred));

      // Walk outward from the preferred slot, alternating sides, until free.
      let chosen = -1;
      outer: for (let offset = 0; offset < slotCount; offset++) {
        const candidates = offset === 0 ? [0] : [offset, -offset];
        for (const d of candidates) {
          const r = preferred + d;
          if (r < 0 || r >= slotCount) continue;
          const overlaps = usage[r].some(u => !(reqEnd < u.start || reqStart > u.end));
          if (!overlaps) { chosen = r; break outer; }
        }
      }
      if (chosen === -1) {
        // Every slot collides here. Pick the one with the smallest overlap.
        let best = preferred, bestOverlap = Infinity;
        for (let r = 0; r < slotCount; r++) {
          const ov = usage[r].reduce((acc, u) => {
            const o = Math.max(0, Math.min(reqEnd, u.end) - Math.max(reqStart, u.start));
            return acc + o;
          }, 0);
          if (ov < bestOverlap) { bestOverlap = ov; best = r; }
        }
        chosen = best;
      }

      usage[chosen].push({ start: reqStart, end: reqEnd });
      entry._slot = chosen;
    });
  }

  // Mobile lane count scales with viewport width so narrow phones aren't
  // crammed; busy years still pack ~5 projects across the same time-band.
  function mobileLaneCount() {
    const w = window.innerWidth;
    if (w < 400) return 4;
    if (w < 600) return 5;
    return 6;
  }

  // ----------------------------------------------------------
  // Render: decide swimlane vs list
  // ----------------------------------------------------------
  function render() {
    const isMobile = window.innerWidth < MOBILE_BREAK;
    if (isMobile) {
      $swim.classList.add('hidden');
      $list.classList.add('is-active');
      $swim.setAttribute('aria-hidden', 'true');
      $list.setAttribute('aria-hidden', 'false');
      // Rendered with every entry; applyFilter fades the non-matching ones.
      renderVerticalSwimlane();
      applyFilter();
    } else {
      $swim.classList.remove('hidden');
      $list.classList.remove('is-active');
      $swim.setAttribute('aria-hidden', 'false');
      $list.setAttribute('aria-hidden', 'true');
      renderSwimlane();
      // Swimlane is rendered with every entry; applyFilter fades the
      // non-matching ones and recomputes label collision visibility.
      applyFilter();
    }
  }

  // ----------------------------------------------------------
  // Desktop: single-lane swimlane with seeded-random heights
  // ----------------------------------------------------------
  function renderSwimlane() {
    $swim.innerHTML = '';

    const years = [];
    for (let y = minYear; y <= maxYear; y++) years.push(y);
    const numYears = years.length;
    // totalSpan is the fractional year-distance the timeline covers
    // (e.g. 12.417 means "12 full years + 5 months").
    const totalSpan = Math.max(rawMaxYear - minYear, 1);
    const lastFrac  = rawMaxYear - maxYear; // 0..1, width of the trailing partial year
    const totalWidth = Math.max($swim.clientWidth - 40, totalSpan * PX_PER_YEAR);
    // Empty scroll buffer past today+1mo so the right edge doesn't feel
    // cramped. The grid itself still ends at totalWidth (so today+1mo lands
    // at the right wall on first render); the user can scroll past it to
    // reveal this extra air.
    const breathingRoom = Math.round(PX_PER_YEAR * 1.5);

    // CSS grid columns: full year columns are 1fr each, last column is a
    // fraction of that, so the right wall lands at "today + 1 month".
    const gridCols = lastFrac > 0.001 && numYears > 1
      ? `repeat(${numYears - 1}, 1fr) ${lastFrac.toFixed(4)}fr`
      : `repeat(${numYears}, 1fr)`;

    const scrollWrap = el('div', 'swimlane-scroll');
    const inner      = el('div', 'swimlane-inner');
    // inner is widened by `breathingRoom`; axis and lane keep the original
    // `totalWidth` so the year ticks and entry positions stay aligned.
    inner.style.width = (totalWidth + breathingRoom) + 'px';

    // year axis
    const axis = el('div', 'year-axis');
    axis.style.gridTemplateColumns = gridCols;
    axis.style.width = totalWidth + 'px';
    years.forEach(y => {
      const t = el('div', 'year-tick');
      if (y === currentYear) t.classList.add('current');
      t.textContent = y;
      axis.appendChild(t);
    });
    inner.appendChild(axis);

    // one lane to rule them all
    const lane = el('div', 'lane unified');
    lane.style.width = totalWidth + 'px';

    // vertical year guides
    const guides = el('div', 'year-guides');
    guides.style.gridTemplateColumns = gridCols;
    for (let i = 0; i < numYears; i++) guides.appendChild(el('div', 'year-guide'));
    lane.appendChild(guides);

    // Importance-aware, collision-free row assignment (shared with the mobile
    // vertical swimlane). Sets entry._slot ∈ [0, LANE_ROWS); heaviest first,
    // biased toward the centre rows. padScale = 1: desktop labels are wide.
    assignSlots(entries, LANE_ROWS, 1);

    lane.style.minHeight = (TOP_PAD + LANE_ROWS * ROW_HEIGHT + 16) + 'px';

    entries.forEach(entry => {
      const node = buildSwimlaneEntry(entry, totalWidth, totalSpan);
      lane.appendChild(node);
    });

    inner.appendChild(lane);
    scrollWrap.appendChild(inner);
    $swim.appendChild(scrollWrap);

    // On first render, scroll so today+1mo (i.e. the end of the timeline grid,
    // at `totalWidth`) sits at the viewport's right edge. The user can still
    // scroll further right to reveal `breathingRoom` of empty space.
    // Re-renders triggered by resize keep the current scroll.
    if (firstRender) {
      requestAnimationFrame(() => {
        const viewportW = scrollWrap.clientWidth;
        scrollWrap.scrollLeft = Math.max(0, totalWidth - viewportW);
      });
      firstRender = false;
    }
  }

  function buildSwimlaneEntry(entry, totalWidth, totalSpan) {
    const pxPerYear = totalWidth / totalSpan;
    const startPx = (entry.startVal - minYear) * pxPerYear;
    const top = TOP_PAD + entry._slot * ROW_HEIGHT;

    const node = document.createElement('button');
    node.className = 'entry';
    node.classList.add(entry.isRange ? 'range' : 'point');
    if (entry.isProject) node.classList.add('is-project');
    if (entry.isClickable) node.classList.add('is-clickable');
    node.style.left = startPx + 'px';
    node.style.top  = top + 'px';
    node.style.setProperty('--cat-color', `var(--${entry.category})`);
    node.style.setProperty('--importance', entry.importanceNorm.toFixed(3));
    node.dataset.id  = entry.id;
    node.dataset.cat = entry.category;
    node.dataset.isProject = String(entry.isProject);
    node.dataset.types = (entry.types || []).join('|');
    node.dataset.importance = entry.importance;

    if (entry.isRange) {
      const widthYears = entry.endVal - entry.startVal;
      node.style.width = Math.max(pxPerYear * widthYears, 60) + 'px';
      const bar = el('div', 'bar');
      bar.textContent = entry.title;

      if (entry.status === 'ongoing' || entry.end === 'present') {
        const arrow = el('div', 'ongoing-arrow');
        node.appendChild(arrow);
      }
      node.appendChild(bar);
    } else {
      const marker = el('div', 'marker');
      const lbl = el('div', 'label');
      lbl.textContent = entry.title;
      if (entry.status) {
        const dot = el('div', 'status-dot ' + entry.status);
        lbl.prepend(dot);
      }
      node.appendChild(marker);
      node.appendChild(lbl);
    }

    attachEntryHandlers(node, entry);
    return node;
  }

  // ----------------------------------------------------------
  // Mobile: vertical swimlane (the desktop swimlane, rotated 90°)
  //
  // Time runs down the Y axis (newest at the top, like a reverse-chron feed);
  // projects pack into a few horizontal lanes via assignSlots() so busy years
  // show several side-by-side. Importance scales node size/prominence through
  // the shared --importance custom property, exactly like the desktop entries.
  // Every entry is rendered (including biographical context) — nothing is
  // hidden behind a collapse — and filters fade non-matching nodes in place.
  // ----------------------------------------------------------
  function renderVerticalSwimlane() {
    $list.innerHTML = '';
    if (!entries.length) return;

    const laneCount = mobileLaneCount();
    assignSlots(entries, laneCount, V_SLOT_PAD);

    const containerW = $list.clientWidth || window.innerWidth;
    const usableW = Math.max(containerW - V_AXIS_W - 4, 200);
    const laneW = usableW / laneCount;
    const totalSpan = Math.max(rawMaxYear - minYear, 1);

    const inner = el('div', 'vswim-inner');
    inner.style.height = (V_TOP_PAD + totalSpan * PX_PER_YEAR_V + 40) + 'px';

    // y position for a fractional year value — newest year sits at the top.
    const yFor = val => V_TOP_PAD + (rawMaxYear - val) * PX_PER_YEAR_V;

    // year guide lines + labels down the left gutter
    const guides = el('div', 'vswim-guides');
    for (let y = minYear; y <= maxYear; y++) {
      const yTop = yFor(y);
      const line = el('div', 'vyear-line');
      line.style.top = yTop + 'px';
      line.style.left = V_AXIS_W + 'px';
      const lab = el('div', 'vyear-label');
      lab.style.top = yTop + 'px';
      lab.textContent = y;
      if (y === currentYear) { line.classList.add('current'); lab.classList.add('current'); }
      guides.appendChild(line);
      guides.appendChild(lab);
    }
    inner.appendChild(guides);

    const geom = { laneW, yFor };
    entries.forEach(entry => inner.appendChild(buildVerticalEntry(entry, geom)));

    $list.appendChild(inner);
  }

  function buildVerticalEntry(entry, geom) {
    const left = V_AXIS_W + entry._slot * geom.laneW;

    const node = document.createElement('button');
    node.className = 'ventry';
    node.classList.add(entry.isRange ? 'range' : 'point');
    if (entry.isProject)   node.classList.add('is-project');
    if (entry.isClickable) node.classList.add('is-clickable');
    node.style.left  = left + 'px';
    node.style.width = (geom.laneW - 6) + 'px';
    node.style.setProperty('--cat-color', `var(--${entry.category})`);
    node.style.setProperty('--importance', entry.importanceNorm.toFixed(3));
    node.dataset.id  = entry.id;
    node.dataset.cat = entry.category;
    node.dataset.isProject = String(entry.isProject);
    node.dataset.types = (entry.types || []).join('|');
    node.dataset.importance = entry.importance;

    if (entry.isRange) {
      // vertical bar spanning the entry's time range in its lane
      node.style.top = geom.yFor(entry.endVal) + 'px';
      node.style.height =
        Math.max((entry.endVal - entry.startVal) * PX_PER_YEAR_V, 30) + 'px';
      const bar = el('div', 'vbar');
      const t = el('span', 'vbar-title');
      t.textContent = entry.title;
      bar.appendChild(t);
      if (entry.status === 'ongoing' || entry.end === 'present') {
        bar.appendChild(el('div', 'vongoing-arrow'));
      }
      node.appendChild(bar);
    } else {
      // point: marker + label, vertically centred on its year position (the
      // translateY(-50%) lives in CSS so the marker sits on the time line)
      node.style.top = geom.yFor(entry.startVal) + 'px';
      const marker = el('div', 'vmarker');
      const lbl = el('div', 'vlabel');
      if (entry.status) lbl.appendChild(el('span', 'vstatus-dot ' + entry.status));
      lbl.appendChild(textSpan(entry.title));
      node.appendChild(marker);
      node.appendChild(lbl);
    }

    attachEntryHandlers(node, entry);
    return node;
  }

  // ----------------------------------------------------------
  // Hover tooltip + click handler shared by both views
  // ----------------------------------------------------------
  function attachEntryHandlers(node, entry) {
    node.addEventListener('mouseenter', e => showTooltip(entry, e));
    node.addEventListener('mousemove',  e => positionTooltip(e));
    node.addEventListener('mouseleave', hideTooltip);
    node.addEventListener('focus', () => {
      const r = node.getBoundingClientRect();
      showTooltip(entry, { clientX: r.left + r.width / 2, clientY: r.top });
    });
    node.addEventListener('blur', hideTooltip);
    node.addEventListener('click', e => {
      e.preventDefault();
      // No hover on touch: a tap opens the detail sheet (with the deep-dive
      // link inside it) rather than navigating straight away.
      if (window.innerWidth < MOBILE_BREAK) openSheet(entry);
      else handleEntryClick(entry);
    });
  }

  function handleEntryClick(entry) {
    // Click only does anything when there is a deep-dive page.
    // External links live inside the deep-dive (as inline embeds), not as the click target.
    if (entry.projectPage) {
      window.location.href = entry.projectPage;
    }
  }

  // ----------------------------------------------------------
  // Entry detail (shared by the desktop hover tooltip and the mobile sheet)
  // ----------------------------------------------------------
  function buildEntryDetail(entry, interactive) {
    const frag = document.createDocumentFragment();

    const cat = el('div', 'tt-cat');
    const sw = el('span', 'tt-cat-swatch');
    sw.style.background = `var(--${entry.category})`;
    cat.appendChild(sw);
    cat.appendChild(textSpan(entry.category + (entry.isProject ? ' · project' : '')));
    frag.appendChild(cat);

    const title = el('h4', 'tt-title');
    title.textContent = entry.title;
    frag.appendChild(title);

    const date = el('div', 'tt-date');
    date.textContent = formatDateRange(entry);
    frag.appendChild(date);

    if (entry.shortDescription) {
      const d = el('p', 'tt-desc');
      d.textContent = entry.shortDescription;
      frag.appendChild(d);
    }

    if (entry.status) {
      const st = el('span', 'tt-status ' + entry.status);
      st.textContent = statusLabel(entry.status);
      frag.appendChild(st);
      if (entry.statusNote) {
        const n = el('span', 'tt-status-note');
        n.textContent = entry.statusNote;
        frag.appendChild(n);
      }
    }

    if (entry.tags && entry.tags.length) {
      const tags = el('div', 'tt-tags');
      entry.tags.forEach(t => {
        const tag = el('span', 'tt-tag');
        tag.textContent = t;
        tags.appendChild(tag);
      });
      frag.appendChild(tags);
    }

    if (entry.projectPage) {
      // Desktop tooltip is non-interactive (pointer-events:none), so a plain
      // line reads as the cue. The mobile sheet needs a real, tappable link.
      if (interactive) {
        const a = document.createElement('a');
        a.className = 'tt-cta';
        a.href = entry.projectPage;
        a.textContent = '↗  Open project deep-dive';
        frag.appendChild(a);
      } else {
        const c = el('div', 'tt-cta');
        c.textContent = '↗  Click for project deep-dive';
        frag.appendChild(c);
      }
    }
    return frag;
  }

  // ----------------------------------------------------------
  // Tooltip (desktop hover)
  // ----------------------------------------------------------
  function showTooltip(entry, e) {
    if (window.innerWidth < MOBILE_BREAK) return;
    $tooltip.classList.remove('is-sheet');
    $tooltip.innerHTML = '';
    $tooltip.appendChild(buildEntryDetail(entry, false));
    positionTooltip(e);
    $tooltip.classList.add('is-visible');
    $tooltip.setAttribute('aria-hidden', 'false');
  }

  function positionTooltip(e) {
    if ($tooltip.classList.contains('is-sheet')) return; // sheet is CSS-positioned
    const pad = 16;
    const w = $tooltip.offsetWidth || 320;
    const h = $tooltip.offsetHeight || 200;
    let x = e.clientX + pad;
    let y = e.clientY + pad;
    if (x + w > window.innerWidth - 12)  x = e.clientX - w - pad;
    if (y + h > window.innerHeight - 12) y = e.clientY - h - pad;
    if (x < 12) x = 12;
    if (y < 12) y = 12;
    $tooltip.style.left = x + 'px';
    $tooltip.style.top  = y + 'px';
  }

  function hideTooltip() {
    if ($tooltip.classList.contains('is-sheet')) return; // don't fight the sheet
    $tooltip.classList.remove('is-visible');
    $tooltip.setAttribute('aria-hidden', 'true');
  }

  // ----------------------------------------------------------
  // Detail sheet (mobile tap) — reuses #tooltip, restyled as a bottom sheet
  // ----------------------------------------------------------
  function openSheet(entry) {
    $tooltip.innerHTML = '';
    $tooltip.appendChild(buildEntryDetail(entry, true));
    $tooltip.style.left = '';
    $tooltip.style.top  = '';
    $tooltip.classList.add('is-sheet', 'is-visible');
    $tooltip.setAttribute('aria-hidden', 'false');
    $backdrop.classList.add('is-visible');
  }

  function closeSheet() {
    $tooltip.classList.remove('is-sheet', 'is-visible');
    $tooltip.setAttribute('aria-hidden', 'true');
    $backdrop.classList.remove('is-visible');
  }

  // ----------------------------------------------------------
  // Filters
  // ----------------------------------------------------------
  $filters.forEach(btn => {
    btn.addEventListener('click', () => {
      $filters.forEach(b => b.classList.remove('is-active'));
      btn.classList.add('is-active');
      activeFilter = btn.dataset.filter;
      applyFilter();
    });
  });

  // Does a rendered entry node (either view) match the active filter? Reads the
  // data-* attributes that buildSwimlaneEntry and buildVerticalEntry both stamp.
  function nodeMatches(node) {
    const cat = node.dataset.cat;
    const isProject = node.dataset.isProject === 'true';
    const types = (node.dataset.types || '').split('|').filter(Boolean);
    if (activeFilter === 'all')             return true;
    if (activeFilter === 'project')         return isProject;
    if (CATEGORY_FILTERS.has(activeFilter)) return cat === activeFilter;
    return types.includes(activeFilter); // type filter
  }

  function applyFilter() {
    // Mobile vertical swimlane: fade non-matching nodes in place; positions
    // stay anchored to the time axis so the user sees what's filtered out
    // (mirrors the desktop behaviour rather than rebuilding the layout).
    if (window.innerWidth < MOBILE_BREAK) {
      $list.querySelectorAll('.ventry').forEach(node => {
        node.classList.toggle('is-faded', !nodeMatches(node));
      });
      return;
    }
    // Desktop swimlane: fade non-matching entries in place; positions stay
    // anchored to the year axis so the user can see what's filtered out.
    $swim.querySelectorAll('.entry').forEach(node => {
      node.classList.toggle('is-faded', !nodeMatches(node));
    });
    // Labels in the swimlane are layout-sensitive: recompute which ones can
    // be shown without colliding with another node's marker / another visible
    // label / a range bar. Defer to the next frame so the browser has applied
    // .is-faded before we measure rects.
    requestAnimationFrame(updateLabelVisibility);
  }

  // ----------------------------------------------------------
  // Smart label visibility (desktop swimlane only)
  //
  // Goal: keep every node (marker) visible, but only show a point entry's
  // text label when it wouldn't visually cover another marker or another
  // already-shown label. Range bars always render their text, since they're the
  // bar itself, not a separate label.
  //
  // Most-important entries claim their label-space first, so the eye lands
  // on the heaviest projects. When a filter narrows the field, collisions
  // disappear naturally and most/all labels become visible.
  // ----------------------------------------------------------
  function updateLabelVisibility() {
    if (window.innerWidth < MOBILE_BREAK) return;
    const lane = $swim.querySelector('.lane');
    if (!lane) return;

    const allPoints = lane.querySelectorAll('.entry.point');
    // Reset state. Every label is a candidate again.
    allPoints.forEach(n => n.classList.remove('label-hidden'));

    const visiblePoints = Array.from(allPoints).filter(n => !n.classList.contains('is-faded'));
    if (!visiblePoints.length) return;

    // Measure each visible point's marker rect and its label's natural rect.
    // Labels have no max-width-0 collapse anymore, so getBoundingClientRect
    // returns the rect at which the label would actually paint.
    const pointData = visiblePoints.map(node => {
      const marker = node.querySelector('.marker');
      const label  = node.querySelector('.label');
      const importance = parseFloat(node.dataset.importance) || 0;
      return {
        node,
        markerRect: marker.getBoundingClientRect(),
        labelRect:  label.getBoundingClientRect(),
        importance,
      };
    });

    // Visible range bars are always-on text, so treat them as obstacles too.
    const rangeRects = [];
    lane.querySelectorAll('.entry.range').forEach(n => {
      if (n.classList.contains('is-faded')) return;
      const bar = n.querySelector('.bar');
      if (bar) rangeRects.push(bar.getBoundingClientRect());
    });

    // Heaviest first so important projects keep their label.
    pointData.sort((a, b) => b.importance - a.importance);

    const shownLabelRects = [];
    pointData.forEach(d => {
      const hitsMarker = pointData.some(o => o !== d && rectsOverlap(d.labelRect, o.markerRect));
      const hitsRange  = rangeRects.some(r => rectsOverlap(d.labelRect, r));
      const hitsLabel  = shownLabelRects.some(r => rectsOverlap(d.labelRect, r));
      if (hitsMarker || hitsRange || hitsLabel) {
        d.node.classList.add('label-hidden');
      } else {
        shownLabelRects.push(d.labelRect);
      }
    });
  }

  function rectsOverlap(a, b) {
    return !(a.right  < b.left
          || a.left   > b.right
          || a.bottom < b.top
          || a.top    > b.bottom);
  }

  // ----------------------------------------------------------
  // Reveal on scroll
  // ----------------------------------------------------------
  const observer = new IntersectionObserver((items) => {
    items.forEach(i => {
      if (i.isIntersecting) {
        i.target.classList.add('is-revealed');
        observer.unobserve(i.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

  document.querySelectorAll('section, .hero-inner').forEach(el => {
    el.classList.add('fade-in');
    observer.observe(el);
  });

  // ----------------------------------------------------------
  // Utility helpers
  // ----------------------------------------------------------
  function el(tag, cls) {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    return node;
  }
  function textSpan(text) {
    const s = document.createElement('span');
    s.textContent = text;
    return s;
  }
  function debounce(fn, ms) {
    let t;
    return (...args) => {
      clearTimeout(t);
      t = setTimeout(() => fn(...args), ms);
    };
  }
  function statusLabel(s) {
    switch (s) {
      case 'nda':     return 'NDA';
      case 'lost':    return 'Lost to time';
      case 'ongoing': return 'Ongoing';
      default:        return s;
    }
  }
  function formatDateRange(entry) {
    const fmt = (val, raw) => {
      if (raw === 'present') return 'present';
      if (Number.isInteger(val)) return String(val);
      const y = Math.floor(val);
      const m = Math.round((val - y) * 12) + 1;
      const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
      return months[Math.min(m - 1, 11)] + ' ' + y;
    };
    const startStr = fmt(entry.startVal, entry.start);
    if (!entry.isRange) return startStr;
    const endStr = fmt(entry.endVal, entry.end);
    return startStr + ' → ' + endStr;
  }

  loadData();
})();
