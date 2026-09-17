(function () {
  'use strict';
  var chip = document.querySelector('.news-chip');
  if (!chip) return;
  var sources = JSON.parse(chip.dataset.newsSources);
  var endpoint = chip.dataset.newsFeed;
  var key = 'texas-ai-news-v2';
  var hour = 3600000, active = null, pending = false, lastAttempt = 0;
  function valid(data) {
    if (!data || data._spec !== 2 || !data.selected) return false;
    var story = data.selected, now = Date.now();
    var checked = Date.parse(data.checked_at), seen = Date.parse(story.first_seen_at);
    if (!Number.isFinite(checked) || !Number.isFinite(seen) || checked > now + 5 * 60000 ||
        seen > now || now - seen >= 168 * hour || seen > checked ||
        typeof story.title !== 'string' || story.title.length < 20 || story.title.length > 220) return false;
    try {
      var url = new URL(story.url);
      if (url.protocol !== 'https:' || url.username || url.password || url.port || /[\s\\]/.test(story.url)) return false;
      return Object.keys(sources).some(function (host) {
        return (url.hostname === host || url.hostname.endsWith('.' + host)) && story.publisher === sources[host][0];
      });
    } catch (_) { return false; }
  }
  function render(data) {
    if (!valid(data) || (active && Date.parse(data.checked_at) < Date.parse(active.checked_at))) return false;
    var story = data.selected;
    var recent = Date.now() - Date.parse(story.first_seen_at) >= 72 * hour ||
                 Date.now() - Date.parse(data.checked_at) > 18 * hour;
    if (active && active.selected.url === story.url) {
      if (chip.dataset.newsStatus !== (recent ? 'recent' : 'current'))
        chip.style.minHeight = chip.getBoundingClientRect().height + 'px';
    } else {
      chip.style.minHeight = '';
    }
    active = data;
    chip.href = story.url;
    chip.target = '_blank';
    chip.rel = 'noopener noreferrer';
    chip.dataset.newsStatus = recent ? 'recent' : 'current';
    chip.dataset.checkedAt = data.checked_at;
    chip.dataset.firstSeenAt = story.first_seen_at;
    chip.dataset.expiresAt = new Date(Date.parse(story.first_seen_at) + 168 * hour).toISOString();
    chip.querySelector('.news-label').textContent = recent ? 'Recent' : 'Trending';
    chip.querySelector('.news-title').textContent = story.title;
    chip.querySelector('.news-source').textContent = story.publisher;
    var date = chip.querySelector('.news-date');
    date.dateTime = story.first_seen_at;
    date.textContent = new Date(story.first_seen_at).toLocaleDateString('en-US', {month:'short', day:'numeric', timeZone:'UTC'});
    return true;
  }
  function fallback() {
    if (active && render(active)) return;
    chip.href = '/articles/';
    chip.dataset.newsStatus = 'empty';
    chip.querySelector('.news-label').textContent = 'Trending';
    chip.querySelector('.news-title').textContent = 'Explore the latest AI reporting';
    chip.querySelector('.news-source').textContent = '';
    chip.querySelector('.news-date').textContent = '';
  }
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
  document.addEventListener('visibilitychange', function () { if (!document.hidden) { fallback(); refresh(); } });
  window.addEventListener('online', refresh);
})();
