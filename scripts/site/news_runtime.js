(function () {
  'use strict';
  var chip = document.querySelector('.news-chip');
  if (!chip) return;
  var sources = JSON.parse(chip.dataset.newsSources);
  var relevance = JSON.parse(chip.dataset.newsRelevance), topic = {};
  ['texas', 'austin', 'local', 'tech', 'ai', 'junk'].forEach(function (name) {
    topic[name] = new RegExp(relevance[name], name === 'local' ? '' : 'i');
  });
  var endpoint = chip.dataset.newsFeed;
  var key = 'texas-ai-news-v2';
  var hour = 3600000, active = null, pending = false, lastAttempt = 0, editionTimer;
  var cadence = 5000, fade = 350, slides = chip.querySelector('.news-slides');
  var template = slides.firstElementChild.cloneNode(true), controls = chip.querySelector('.news-controls');
  var motion = matchMedia('(prefers-reduced-motion: reduce)');
  var paused = motion.matches, held = false, hovering = false, inView = true;
  var pool = [], index = 0, editionKey = '', shownAt = 0, cycleTimer, swapTimer, animation, revision = 0;
  chip.dataset.newsCadence = String(cadence);
  function relevant(title, group, summary) {
    var text = title + ' ' + summary;
    var texas = topic.texas.test(text) || topic.austin.test(title) ||
                (group === 'dallasinnovates' && topic.local.test(title));
    return !topic.junk.test(title) &&
      texas && (topic.ai.test(text) || topic.tech.test(title));
  }
  function validStory(story, checked, now) {
    if (!story) return false;
    var summary = story.summary === undefined ? '' : story.summary;
    if (typeof summary !== 'string' || summary.length > 1000 || /[<>]/.test(summary)) return false;
    var seen = Date.parse(story.first_seen_at);
    if (!Number.isFinite(seen) || seen > now || now - seen >= 168 * hour || seen > checked ||
        typeof story.title !== 'string' || story.title.length < 20 || story.title.length > 220 ||
        story.title.trim().split(/\s+/).length > 32) return false;
    try {
      var url = new URL(story.url);
      if (url.protocol !== 'https:' || url.username || url.password || url.port || /[\s\\]/.test(story.url)) return false;
      return Object.keys(sources).some(function (host) {
        return (url.hostname === host || url.hostname.endsWith('.' + host)) &&
          story.publisher === sources[host][0] && relevant(story.title, sources[host][1], summary);
      });
    } catch (_) { return false; }
  }
  function valid(data) {
    if (!data || data._spec !== 2 || !data.selected) return false;
    var now = Date.now(), checked = Date.parse(data.checked_at);
    if (!Number.isFinite(checked) || checked > now + 5 * 60000 || !validStory(data.selected, checked, checked)) return false;
    if (data.rotation_version === undefined) return data.carousel_version === undefined && data.editions === undefined;
    if (data.carousel_version !== undefined && data.carousel_version !== 1) return false;
    if (data.rotation_version !== 1 || !Array.isArray(data.editions) || !data.editions.length || data.editions.length > 4) return false;
    var anchor = 83 * 60000, slot = Math.floor((checked - anchor) / (6 * hour)) * 6 * hour + anchor, urls = [];
    return data.editions.every(function (entry, i) {
      if (!entry || !entry.selected) return false;
      if (data.carousel_version !== 1 && entry.stories !== undefined) return false;
      var start = Date.parse(entry.starts_at), story = entry.selected;
      if (start !== slot + i * 6 * hour || !validStory(story, checked, Math.max(start, checked)) ||
          Math.max(start, checked) - Date.parse(story.first_seen_at) >= 168 * hour ||
          (i === 0 && JSON.stringify(story) !== JSON.stringify(data.selected))) return false;
      if (data.carousel_version === 1) {
        if (!Array.isArray(entry.stories) || !entry.stories.length || entry.stories.length > 10 ||
            JSON.stringify(entry.stories[0]) !== JSON.stringify(story)) return false;
        if (i && entry.stories.length > 1 && urls[i - 1] === story.url) return false;
        var members = [];
        if (!entry.stories.every(function (candidate) {
          if (!validStory(candidate, checked, Math.max(start, checked)) ||
              Math.max(start, checked) - Date.parse(candidate.first_seen_at) >= 168 * hour ||
              members.indexOf(candidate.url) >= 0) return false;
          members.push(candidate.url);
          return true;
        })) return false;
      }
      urls.push(story.url);
      return true;
    });
  }
  function currentEdition(data) {
    var edition = {selected:data.selected, starts_at:null};
    (data.editions || []).forEach(function (entry) {
      if (Date.parse(entry.starts_at) <= Date.now()) edition = entry;
    });
    return edition;
  }
  function stop() {
    clearTimeout(cycleTimer);
    clearTimeout(swapTimer);
    revision++;
    if (animation) { animation.cancel(); animation = null; }
    slides.style.opacity = '1';
  }
  function playing() {
    return !paused && !hovering && inView && !document.hidden && pool.length > 1;
  }
  function updateControls() {
    controls.hidden = pool.length < 2;
    slides.setAttribute('aria-live', paused ? 'polite' : 'off');
    chip.dataset.newsPlaying = String(playing());
  }
  function schedule() {
    clearTimeout(cycleTimer);
    updateControls();
    if (playing()) cycleTimer = setTimeout(function () {
      transition((index + 1) % pool.length);
    }, Math.max(0, cadence - (motion.matches ? 0 : fade) - (performance.now() - shownAt)));
  }
  function dateText(value) {
    var observed = new Date(value), day = observed.getUTCDate();
    var suffix = day % 100 >= 10 && day % 100 <= 20 ? 'th' : ({1:'st', 2:'nd', 3:'rd'}[day % 10] || 'th');
    return observed.toLocaleDateString('en-US', {month:'long', timeZone:'UTC'}) +
      ' ' + day + suffix;
  }
  function select(next) {
    index = next;
    Array.from(slides.children).forEach(function (slide, i) {
      slide.setAttribute('aria-hidden', String(i !== index));
      slide.inert = i !== index;
    });
    var story = pool[index];
    var recent = Date.now() - Date.parse(story.first_seen_at) >= 72 * hour ||
                 Date.now() - Date.parse(active.checked_at) > 18 * hour ||
                 (chip.dataset.editionAt && Date.now() >= Date.parse(chip.dataset.editionAt) + 6 * hour);
    chip.dataset.newsStatus = recent ? 'recent' : 'current';
    chip.dataset.firstSeenAt = story.first_seen_at;
    chip.dataset.expiresAt = new Date(Date.parse(story.first_seen_at) + 168 * hour).toISOString();
    chip.querySelector('.news-label').textContent = recent ? 'Recent' : 'Trending';
    shownAt = performance.now();
    updateControls();
  }
  function transition(next) {
    stop();
    var ticket = revision;
    if (!motion.matches) {
      animation = slides.animate([{opacity:1}, {opacity:0}], {duration:fade, fill:'forwards', easing:'ease-in'});
    }
    // The reading cadence uses the clock, not compositor completion. A busy renderer
    // can resolve animation.finished late, which would lengthen every headline slot.
    swapTimer = setTimeout(function () {
      if (ticket !== revision) return;
      select(next);
      if (animation) animation.cancel();
      animation = motion.matches ? null : slides.animate([{opacity:0}, {opacity:1}],
        {duration:fade, fill:'forwards', easing:'ease-out'});
      schedule();
    }, motion.matches ? 0 : fade);
  }
  function install(edition) {
    stop();
    pool = edition.stories || [edition.selected];
    chip.dataset.editionAt = edition.starts_at || '';
    var fragment = document.createDocumentFragment();
    pool.forEach(function (story, i) {
      var slide = template.cloneNode(true), link = slide.querySelector('.news-link');
      slide.setAttribute('aria-label', (i + 1) + ' of ' + pool.length);
      slide.setAttribute('aria-hidden', String(i !== 0));
      slide.inert = i !== 0;
      link.href = story.url;
      slide.querySelector('.news-title').textContent = story.title;
      slide.querySelector('.news-source').textContent = story.publisher;
      var date = slide.querySelector('.news-date');
      date.dateTime = story.first_seen_at;
      date.textContent = dateText(story.first_seen_at);
      fragment.appendChild(slide);
    });
    slides.replaceChildren(fragment);
    select(0);
    schedule();
  }
  function render(data) {
    if (!valid(data) || (active && Date.parse(data.checked_at) < Date.parse(active.checked_at))) return false;
    if (active && active.rotation_version === 1 && data.rotation_version !== 1) return false;
    if (active && active.carousel_version === 1 && data.carousel_version !== 1) return false;
    var scheduled = currentEdition(data);
    var eligible = (scheduled.stories || [scheduled.selected]).filter(function (story) {
      return validStory(story, Date.parse(data.checked_at), Date.now());
    });
    if (!eligible.length) return false;
    var edition = {starts_at:scheduled.starts_at, selected:eligible[0], stories:eligible};
    active = data;
    chip.dataset.checkedAt = data.checked_at;
    var nextKey = JSON.stringify([edition.starts_at, (edition.stories || [edition.selected]).map(function (s) {
      return [s.url, s.title, s.publisher, s.first_seen_at];
    })]);
    var expired = pool.some(function (story) { return Date.now() - Date.parse(story.first_seen_at) >= 168 * hour; });
    if (editionKey !== nextKey && (!pool.length || expired || (!held && !hovering))) {
      editionKey = nextKey;
      install(edition);
    } else if (editionKey === nextKey && pool.length) {
      // Refresh the freshness label without resetting the five-second timer.
      var previousShownAt = shownAt;
      select(index);
      shownAt = previousShownAt;
    }
    clearTimeout(editionTimer);
    var next = (data.editions || []).find(function (entry) { return Date.parse(entry.starts_at) > Date.now(); });
    // Remove an expiring member at its deadline even between collections or while offline.
    var expires = Math.min.apply(null, eligible.map(function (story) { return Date.parse(story.first_seen_at) + 168 * hour; }));
    var wake = next ? Math.min(Date.parse(next.starts_at), expires) : expires;
    editionTimer = setTimeout(fallback, Math.max(0, wake - Date.now()) + 50);
    return true;
  }
  function fallback() {
    if (active && render(active)) return;
    stop();
    pool = [];
    editionKey = '';
    var slide = template.cloneNode(true);
    slide.setAttribute('aria-hidden', 'false');
    slide.inert = false;
    slide.querySelector('.news-link').href = '/articles/';
    slide.querySelector('.news-title').textContent = 'Explore the latest AI reporting';
    slide.querySelector('.news-source').textContent = '';
    slide.querySelector('.news-date').textContent = '';
    slides.replaceChildren(slide);
    chip.dataset.newsStatus = 'empty';
    chip.querySelector('.news-label').textContent = 'Trending';
    updateControls();
  }
  function pause() {
    paused = true;
    held = true;
    stop();
    updateControls();
  }
  function resume() {
    if (hovering || chip.contains(document.activeElement)) return;
    paused = motion.matches;
    held = false;
    fallback();
    shownAt = performance.now();
    schedule();
  }
  function step(direction) {
    pause();
    // Explicit navigation is also a safe point to install an awaiting six-hour edition.
    held = false;
    var before = editionKey;
    var wasHovering = hovering;
    hovering = false;
    fallback();
    hovering = wasHovering;
    held = true;
    if (pool.length && before === editionKey) select((index + direction + pool.length) % pool.length);
  }
  chip.querySelector('.news-prev').addEventListener('click', function () { step(-1); });
  chip.querySelector('.news-next').addEventListener('click', function () { step(1); });
  chip.addEventListener('pointerenter', function (event) {
    if (event.pointerType !== 'mouse') return;
    hovering = true;
    stop();
    updateControls();
  });
  chip.addEventListener('pointerleave', function (event) {
    if (event.pointerType !== 'mouse') return;
    hovering = false;
    resume();
  });
  // Focus or pressing a story freezes it before its destination can change.
  chip.addEventListener('focusin', pause);
  chip.addEventListener('focusout', function (event) {
    if (!chip.contains(event.relatedTarget)) setTimeout(resume, 0);
  });
  slides.addEventListener('pointerdown', pause);
  slides.addEventListener('pointerup', function () { setTimeout(resume, 0); });
  slides.addEventListener('pointercancel', function () { setTimeout(resume, 0); });
  motion.addEventListener('change', function () {
    if (motion.matches) {
      paused = true;
      stop();
      updateControls();
    } else resume();
  });
  if ('IntersectionObserver' in window) new IntersectionObserver(function (entries) {
    inView = entries[0].isIntersecting;
    stop();
    shownAt = performance.now();
    schedule();
  }).observe(chip);
  try { render(JSON.parse(chip.dataset.newsInitial)); } catch (_) {}
  try { render(JSON.parse(localStorage.getItem(key))); } catch (_) {}
  fallback();
  async function refresh() {
    if (pending || (lastAttempt && Date.now() - lastAttempt < 60000)) return;
    pending = true;
    lastAttempt = Date.now();
    var controller = new AbortController();
    var timer = setTimeout(function () { controller.abort(); }, 10000);
    try {
      var response = await fetch(endpoint + '?refresh=' + Math.floor(Date.now() / (5 * 60000)), {
        cache:'no-store', credentials:'omit', referrerPolicy:'no-referrer', redirect:'error', signal:controller.signal
      });
      if (!response.ok) throw new Error('News request failed');
      // The collector stores bounded headline metadata, never article bodies.
      if (Number(response.headers.get('content-length')) > 500000) throw new Error('News response too large');
      var text = await response.text();
      if (text.length > 500000) throw new Error('News response too large');
      var data = JSON.parse(text);
      if (render(data)) {
        try { localStorage.setItem(key, JSON.stringify(data)); } catch (_) {}
      }
    } catch (_) {
      // A timeout, invalid payload or offline tab keeps the dated last good headline.
    } finally {
      clearTimeout(timer);
      pending = false;
      fallback();
      chip.dataset.newsLoaded = 'true';
    }
  }
  refresh();
  setInterval(function () { if (!document.hidden) { fallback(); refresh(); } }, 15 * 60000);
  document.addEventListener('visibilitychange', function () {
    stop();
    if (!document.hidden) { fallback(); refresh(); }
    shownAt = performance.now();
    schedule();
  });
  window.addEventListener('online', refresh);
})();
