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
  var hour = 3600000, active = null, pending = false, lastAttempt = 0, rotationTimer;
  function relevant(title, group) {
    var texas = topic.texas.test(title) || topic.austin.test(title) ||
                (group === 'dallasinnovates' && topic.local.test(title));
    return !topic.junk.test(title) &&
      ((topic.ai.test(title) && relevance.global_groups.indexOf(group) >= 0) || (texas && topic.tech.test(title)));
  }
  function validStory(story, checked, now) {
    if (!story) return false;
    var seen = Date.parse(story.first_seen_at);
    if (!Number.isFinite(seen) || seen > now || now - seen >= 168 * hour || seen > checked ||
        typeof story.title !== 'string' || story.title.length < 20 || story.title.length > 220 ||
        story.title.trim().split(/\s+/).length > 32) return false;
    try {
      var url = new URL(story.url);
      if (url.protocol !== 'https:' || url.username || url.password || url.port || /[\s\\]/.test(story.url)) return false;
      return Object.keys(sources).some(function (host) {
        return (url.hostname === host || url.hostname.endsWith('.' + host)) &&
          story.publisher === sources[host][0] && relevant(story.title, sources[host][1]);
      });
    } catch (_) { return false; }
  }
  function valid(data) {
    if (!data || data._spec !== 2 || !data.selected) return false;
    var now = Date.now(), checked = Date.parse(data.checked_at);
    if (!Number.isFinite(checked) || checked > now + 5 * 60000 || !validStory(data.selected, checked, now)) return false;
    if (data.rotation_version === undefined) return true;
    if (data.rotation_version !== 1 || !Array.isArray(data.editions) || !data.editions.length || data.editions.length > 4) return false;
    var anchor = 83 * 60000, slot = Math.floor((checked - anchor) / (6 * hour)) * 6 * hour + anchor, urls = [];
    return data.editions.every(function (entry, i) {
      if (!entry || !entry.selected) return false;
      var start = Date.parse(entry.starts_at), story = entry.selected;
      if (start !== slot + i * 6 * hour || !validStory(story, checked, now) ||
          Math.max(start, checked) - Date.parse(story.first_seen_at) >= 72 * hour ||
          urls.indexOf(story.url) >= 0 || (i === 0 && JSON.stringify(story) !== JSON.stringify(data.selected))) return false;
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
  function render(data) {
    if (!valid(data) || (active && Date.parse(data.checked_at) < Date.parse(active.checked_at))) return false;
    if (active && active.rotation_version === 1 && data.rotation_version !== 1) return false;
    var edition = currentEdition(data), story = edition.selected;
    var recent = Date.now() - Date.parse(story.first_seen_at) >= 72 * hour ||
                 Date.now() - Date.parse(data.checked_at) > 18 * hour ||
                 (edition.starts_at && Date.now() >= Date.parse(edition.starts_at) + 6 * hour);
    if (active && chip.href === story.url) {
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
    chip.dataset.editionAt = edition.starts_at || '';
    chip.dataset.firstSeenAt = story.first_seen_at;
    chip.dataset.expiresAt = new Date(Date.parse(story.first_seen_at) + 168 * hour).toISOString();
    chip.querySelector('.news-label').textContent = recent ? 'Recent' : 'Trending';
    chip.querySelector('.news-title').textContent = story.title;
    chip.querySelector('.news-source').textContent = story.publisher;
    var date = chip.querySelector('.news-date');
    date.dateTime = story.first_seen_at;
    var observed = new Date(story.first_seen_at), day = observed.getUTCDate();
    var suffix = day % 100 >= 10 && day % 100 <= 20 ? 'th' : ({1:'st', 2:'nd', 3:'rd'}[day % 10] || 'th');
    date.textContent = observed.toLocaleDateString('en-US', {month:'long', timeZone:'UTC'}) +
      ' ' + day + suffix + ', ' + observed.getUTCFullYear();
    clearTimeout(rotationTimer);
    var next = (data.editions || []).find(function (entry) { return Date.parse(entry.starts_at) > Date.now(); });
    if (next) rotationTimer = setTimeout(fallback, Date.parse(next.starts_at) - Date.now() + 50);
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
