/* ============================================================
   Andreas Lindeman portfolio script
   - Loads timeline entries from projects_data/manifest.json
   - Single-lane swimlane (desktop) with seeded-random vertical
     placement so categories share a row, distinguished by colour
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
  const LIST_QUIET_THRESHOLD = 50; // mobile list: dim+shrink entries below this
  const DENSE_YEAR_MIN_ENTRIES = 3; // mobile list: years before the first
                                    // year with ≥ this many entries collapse
                                    // into a single "earlier timeline" toggle.
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
      // hideOnMobile: opt-in flag for biographical / life-stage entries that
      // give useful context on the desktop swimlane but just take up scroll
      // space in the vertical list. Hidden in the mobile list view only;
      // still rendered on the desktop swimlane.
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
  // Render: decide swimlane vs list
  // ----------------------------------------------------------
  function render() {
    const isMobile = window.innerWidth < MOBILE_BREAK;
    if (isMobile) {
      $swim.classList.add('hidden');
      $list.classList.add('is-active');
      $swim.setAttribute('aria-hidden', 'true');
      $list.setAttribute('aria-hidden', 'false');
      // renderList filters internally; no separate applyFilter pass needed.
      renderList();
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

    // Row assignment: importance-aware, collision-free.
    //
    // - Process heaviest first so they get their preferred slot.
    // - Each entry has a "preferred band" of rows. Heavier entries are biased
    //   toward the centre rows so the eye lands on them; lighter entries
    //   drift toward the edges. The hash provides deterministic jitter so the
    //   layout looks organic, not striped by importance.
    // - For each row, we track the time-intervals already taken (with label
    //   padding) and never place two entries on the same row in overlapping
    //   time. If we can't find a free row, we widen the search and finally
    //   accept the least-bad slot.
    const rowUsage = []; // rowUsage[i] = array of {start, end}
    for (let i = 0; i < LANE_ROWS; i++) rowUsage.push([]);

    const center = (LANE_ROWS - 1) / 2;
    const placement = entries.slice().sort((a, b) => b.importance - a.importance);

    placement.forEach(entry => {
      const start = entry.startVal;
      const end   = entry.isRange ? entry.endVal : start;
      // padding around the entry; accounts for the label/bar visually
      // extending past the marker. Heavier entries reserve more horizontal
      // space because their labels are larger.
      const basePad = entry.isRange ? 0.04 : 0.18;
      const labelPad = basePad + entry.importanceNorm * 0.5;
      const reqStart = start - labelPad;
      const reqEnd   = end + labelPad;

      // Hash-driven jitter for the preferred row within the band.
      const seed = hash01(entry.id || entry.title);
      // Heavier → narrower band around centre (offset ∈ [-1, 1] × bandHalf).
      // Lighter → wider band that reaches the edges.
      const bandHalf = (LANE_ROWS / 2) * (1.05 - entry.importanceNorm * 0.55);
      const direction = seed < 0.5 ? -1 : 1;
      const intoBand  = ((seed * 2) % 1);              // 0..1
      let preferred = Math.round(center + direction * intoBand * bandHalf);
      preferred = Math.max(0, Math.min(LANE_ROWS - 1, preferred));

      // Walk outward from preferred row, alternating sides, until a free row
      // is found.
      let chosen = -1;
      outer: for (let offset = 0; offset < LANE_ROWS; offset++) {
        const candidates = offset === 0 ? [0] : [offset, -offset];
        for (const d of candidates) {
          const r = preferred + d;
          if (r < 0 || r >= LANE_ROWS) continue;
          const overlaps = rowUsage[r].some(u => !(reqEnd < u.start || reqStart > u.end));
          if (!overlaps) { chosen = r; break outer; }
        }
      }
      if (chosen === -1) {
        // Every row collides at this time-range. Pick the row with the
        // smallest overlap so the visual damage is minimal.
        let best = preferred, bestOverlap = Infinity;
        for (let r = 0; r < LANE_ROWS; r++) {
          const ov = rowUsage[r].reduce((acc, u) => {
            const o = Math.max(0, Math.min(reqEnd, u.end) - Math.max(reqStart, u.start));
            return acc + o;
          }, 0);
          if (ov < bestOverlap) { bestOverlap = ov; best = r; }
        }
        chosen = best;
      }

      rowUsage[chosen].push({ start: reqStart, end: reqEnd });
      entry._row = chosen;
    });

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
    const top = TOP_PAD + entry._row * ROW_HEIGHT;

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
  // Mobile: list view
  // ----------------------------------------------------------
  function renderList() {
    $list.innerHTML = '';

    // Mobile filter behaviour: re-render the list from the filtered subset so
    // years that drop out (no matching entries) physically disappear, and the
    // backward-merge + earlier-timeline logic re-runs to collapse what's left
    // into a clean grouping. Beats fading individual entries in place; the
    // resulting list has no empty year headers or stranded "+0 more" toggles.
    // Also drop entries explicitly flagged hideOnMobile, since those exist for
    // biographical context on the desktop timeline only.
    const visible = entries.filter(e => !e.hideOnMobile && entryMatchesActiveFilter(e));

    if (!visible.length) {
      const empty = el('p', 'list-empty');
      empty.textContent = 'Nothing matches this filter.';
      $list.appendChild(empty);
      return;
    }

    const byYear = {};
    visible.forEach(e => {
      const y = Math.floor(e.startVal);
      (byYear[y] = byYear[y] || []).push(e);
    });
    const years = Object.keys(byYear).map(Number).sort((a, b) => a - b);

    // Build groups, folding minor-only years into the nearest year-with-major
    // so a lone "+1 more" never sits under an empty year header.
    //
    // Direction:
    //   - prefer backward: fold into the most recent emitted group, so the
    //     anchor major reads first (e.g. 2016's minor-only entry merges into
    //     the 2015 group → header becomes "2015–2016").
    //   - if there is no emitted group yet (start of timeline, before the
    //     first major), accumulate forward into "pending" and merge those
    //     into the first major year we hit (e.g. 2002 / 2009 / 2011 all roll
    //     into the 2014 group → header becomes "2002–2014").
    const groups = [];
    let pendingMinors = [];
    let pendingStartYear = null;

    years.forEach((y, idx) => {
      const yearEntries = byYear[y];
      // Heavier entries float to the top within their year-bucket
      yearEntries.sort((a, b) => b.importance - a.importance);
      const major = yearEntries.filter(e => e.importance >= LIST_QUIET_THRESHOLD);
      const minor = yearEntries.filter(e => e.importance <  LIST_QUIET_THRESHOLD);

      if (major.length === 0) {
        if (groups.length) {
          // Fold backward: extend the previous group's end-year and append.
          const tail = groups[groups.length - 1];
          tail.endYear = y;
          tail.minors.push(...minor);
        } else {
          // No prior anchor yet, so accumulate until the first major lands.
          if (pendingStartYear === null) pendingStartYear = y;
          pendingMinors.push(...minor);
        }
        return;
      }

      groups.push({
        startYear: pendingStartYear !== null ? pendingStartYear : y,
        endYear: y,
        majors: major,
        minors: [...pendingMinors, ...minor],
      });
      pendingMinors = [];
      pendingStartYear = null;
    });

    // Edge: the entire timeline is minor-only (no anchor was ever found).
    // Render the orphan accumulator as its own group so the entries don't
    // silently vanish.
    if (pendingMinors.length) {
      groups.push({
        startYear: pendingStartYear,
        endYear: years[years.length - 1],
        majors: [],
        minors: pendingMinors,
      });
    }

    // Find when the timeline becomes "dense": the first year that has
    // ≥ DENSE_YEAR_MIN_ENTRIES on its own. Everything before that collapses
    // into a single "earlier timeline" toggle at the top of the list.
    //
    // Only applied to the *unfiltered* view. With a filter active, the user
    // has already narrowed the timeline themselves, so hiding more entries
    // behind another toggle would mean a filter like "school" buries the
    // entries that match it just because the matches sit in early years.
    // Falls back to no collapsing if the entire timeline is sparse.
    const firstDenseYear = activeFilter === 'all'
      ? (years.find(y => byYear[y].length >= DENSE_YEAR_MIN_ENTRIES) ?? null)
      : null;
    const earlyGroups = firstDenseYear === null
      ? []
      : groups.filter(g => g.endYear < firstDenseYear);
    const mainGroups  = firstDenseYear === null
      ? groups
      : groups.filter(g => g.endYear >= firstDenseYear);

    if (earlyGroups.length) {
      const wrap = document.createElement('details');
      wrap.className = 'earlier-timeline';
      const summary = document.createElement('summary');
      const startYear = earlyGroups[0].startYear;
      const endYear   = earlyGroups[earlyGroups.length - 1].endYear;
      const total = earlyGroups.reduce((n, g) => n + g.majors.length + g.minors.length, 0);
      summary.innerHTML =
        `<span class="et-label">Earlier projects</span>` +
        `<span class="et-meta">${startYear}–${endYear} · ${total}</span>`;
      wrap.appendChild(summary);
      const inner = el('div', 'earlier-timeline-content');
      earlyGroups.forEach(g => inner.appendChild(buildYearGroup(g)));
      wrap.appendChild(inner);
      $list.appendChild(wrap);
    }

    mainGroups.forEach(g => $list.appendChild(buildYearGroup(g)));
  }

  function buildYearGroup(g) {
    const group = el('div', 'year-group');
    const header = el('div', 'year-header');
    header.textContent = g.startYear === g.endYear
      ? String(g.startYear)
      : `${g.startYear}–${g.endYear}`;
    group.appendChild(header);

    const wrap = el('div', 'year-entries');
    g.majors.forEach(entry => wrap.appendChild(buildListEntry(entry)));

    if (g.minors.length) {
      const details = document.createElement('details');
      details.className = 'year-more';
      const summary = document.createElement('summary');
      summary.textContent = `${g.minors.length} more`;
      details.appendChild(summary);
      const minorWrap = el('div', 'year-minor-entries');
      g.minors.forEach(entry => minorWrap.appendChild(buildListEntry(entry)));
      details.appendChild(minorWrap);
      wrap.appendChild(details);
    }

    group.appendChild(wrap);
    return group;
  }

  function buildListEntry(entry) {
    const node = el('button', 'list-entry');
    node.style.setProperty('--cat-color', `var(--${entry.category})`);
    node.style.setProperty('--importance', entry.importanceNorm.toFixed(3));
    node.dataset.id  = entry.id;
    node.dataset.cat = entry.category;
    node.dataset.isProject = String(entry.isProject);
    node.dataset.types = (entry.types || []).join('|');
    if (entry.isClickable) node.classList.add('is-clickable');
    if (entry.importance < LIST_QUIET_THRESHOLD) node.classList.add('is-quiet');

    const meta = el('div', 'le-meta');
    const sw = el('span', 'le-cat-swatch');
    meta.appendChild(sw);
    meta.appendChild(textSpan(entry.category));
    meta.appendChild(textSpan('·'));
    meta.appendChild(textSpan(formatDateRange(entry)));
    node.appendChild(meta);

    const title = el('h3', 'le-title');
    title.textContent = entry.title;
    node.appendChild(title);

    if (entry.shortDescription) {
      const desc = el('p', 'le-desc');
      desc.textContent = entry.shortDescription;
      node.appendChild(desc);
    }

    if (entry.status) {
      const status = el('span', 'le-status ' + entry.status);
      status.textContent = statusLabel(entry.status);
      node.appendChild(status);
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
      handleEntryClick(entry);
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
  // Tooltip
  // ----------------------------------------------------------
  function showTooltip(entry, e) {
    if (window.innerWidth < MOBILE_BREAK) return;
    $tooltip.innerHTML = '';

    const cat = el('div', 'tt-cat');
    const sw = el('span', 'tt-cat-swatch');
    sw.style.background = `var(--${entry.category})`;
    cat.appendChild(sw);
    cat.appendChild(textSpan(entry.category + (entry.isProject ? ' · project' : '')));
    $tooltip.appendChild(cat);

    const title = el('h4', 'tt-title');
    title.textContent = entry.title;
    $tooltip.appendChild(title);

    const date = el('div', 'tt-date');
    date.textContent = formatDateRange(entry);
    $tooltip.appendChild(date);

    if (entry.shortDescription) {
      const d = el('p', 'tt-desc');
      d.textContent = entry.shortDescription;
      $tooltip.appendChild(d);
    }

    if (entry.status) {
      const st = el('span', 'tt-status ' + entry.status);
      st.textContent = statusLabel(entry.status);
      $tooltip.appendChild(st);
      if (entry.statusNote) {
        const n = el('span', 'tt-status-note');
        n.style.fontSize = '11px';
        n.style.color = 'var(--text-mute)';
        n.textContent = entry.statusNote;
        $tooltip.appendChild(n);
      }
    }

    if (entry.tags && entry.tags.length) {
      const tags = el('div', 'tt-tags');
      entry.tags.forEach(t => {
        const tag = el('span', 'tt-tag');
        tag.textContent = t;
        tags.appendChild(tag);
      });
      $tooltip.appendChild(tags);
    }

    if (entry.projectPage) {
      const c = el('div', 'tt-cta');
      c.textContent = '↗  Click for project deep-dive';
      $tooltip.appendChild(c);
    }

    positionTooltip(e);
    $tooltip.classList.add('is-visible');
    $tooltip.setAttribute('aria-hidden', 'false');
  }

  function positionTooltip(e) {
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
    $tooltip.classList.remove('is-visible');
    $tooltip.setAttribute('aria-hidden', 'true');
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

  function entryMatchesActiveFilter(entry) {
    if (activeFilter === 'all')             return true;
    if (activeFilter === 'project')         return entry.isProject;
    if (CATEGORY_FILTERS.has(activeFilter)) return entry.category === activeFilter;
    return (entry.types || []).includes(activeFilter); // type/tag filter
  }

  function applyFilter() {
    // Mobile list view: rebuild from the filtered subset so empty years
    // physically drop out and adjacent visible years re-group via the same
    // backward-merge + earlier-timeline logic used on first render.
    if (window.innerWidth < MOBILE_BREAK) {
      renderList();
      return;
    }
    // Desktop swimlane: fade non-matching entries in place; positions stay
    // anchored to the year axis so the user can see what's filtered out.
    $swim.querySelectorAll('.entry').forEach(node => {
      const cat = node.dataset.cat;
      const isProject = node.dataset.isProject === 'true';
      const types = (node.dataset.types || '').split('|').filter(Boolean);
      let show = true;
      if (activeFilter === 'all') show = true;
      else if (activeFilter === 'project') show = isProject;
      else if (CATEGORY_FILTERS.has(activeFilter)) show = cat === activeFilter;
      else show = types.includes(activeFilter);
      node.classList.toggle('is-faded', !show);
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
