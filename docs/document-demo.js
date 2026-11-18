/* Static search and ephemeral review state. No fetch, storage, analytics or generated text. */
(() => {
  'use strict';
  const root = document.querySelector('.di-workspace');
  if (!root) return;
  const query = root.querySelector('#di-query');
  const category = root.querySelector('#di-category');
  const state = root.querySelector('#di-status');
  const entries = [...root.querySelectorAll('[data-entry]')];
  const normalize = value => value.normalize('NFKC').toLowerCase().trim();
  const labels = {'needs-review': 'Needs review', question: 'Question for reviewer', reviewed: 'Reviewed in this session'};
  const filter = () => {
    const words = normalize(query.value).split(/\s+/).filter(Boolean);
    let shown = 0, reviewed = 0, questions = 0;
    entries.forEach(entry => {
      const value = entry.querySelector('[data-review]').value;
      const haystack = normalize(entry.dataset.search);
      entry.hidden = !words.every(word => haystack.includes(word)) ||
        Boolean(category.value && entry.dataset.category !== category.value) ||
        Boolean(state.value && value !== state.value);
      if (!entry.hidden) shown++;
      if (value === 'reviewed') reviewed++;
      if (value === 'question') questions++;
      entry.querySelector('[data-status-label]').textContent = labels[value];
      entry.dataset.reviewState = value;
    });
    root.querySelector('#di-count').textContent = `${shown} of ${entries.length} passages shown`;
    root.querySelector('#di-review-count').textContent = `${reviewed} reviewed · ${questions} with a question`;
    root.querySelector('#di-empty').hidden = shown !== 0;
  };
  const clear = () => { query.value = ''; category.value = ''; state.value = ''; filter(); };
  query.addEventListener('input', filter);
  category.addEventListener('change', filter);
  state.addEventListener('change', filter);
  entries.forEach(entry => entry.querySelector('[data-review]').addEventListener('change', () => {
    // A status filter can remove the focused card. Put focus on that filter rather than
    // abandoning keyboard users on the body or on a now-hidden select.
    const focused = entry.contains(document.activeElement);
    filter();
    if (entry.hidden && focused) state.focus();
  }));
  root.querySelector('#di-clear').addEventListener('click', () => { clear(); query.focus(); });
  root.querySelector('#di-reset').addEventListener('click', () => {
    entries.forEach(entry => { entry.querySelector('[data-review]').value = 'needs-review'; });
    state.value = '';
    filter();
  });
  root.querySelectorAll('[data-example]').forEach(button => button.addEventListener('click', () => {
    clear(); query.value = button.dataset.example; filter(); query.focus();
  }));
  root.querySelectorAll('[data-enhanced]').forEach(element => { element.hidden = false; });
  // Firefox and history restoration may restore form values. A new document deliberately
  // starts clean because this example promises no persisted review state.
  entries.forEach(entry => { entry.querySelector('[data-review]').value = 'needs-review'; });
  query.value = ''; category.value = ''; state.value = '';
  filter();
})();
