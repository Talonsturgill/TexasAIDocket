/* Browser-managed speech recognition. No recorder, audio storage or automatic submission.
   The browser's speech service handles audio only after the reader presses the microphone. */
(function () {
  'use strict';
  var Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  var active = null;
  var icon = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">' +
    '<g class="voice-mic"><rect x="9" y="3" width="6" height="11" rx="3"/>' +
    '<path d="M5 10v1a7 7 0 0 0 14 0v-1M12 18v3M9 21h6"/></g>' +
    '<rect class="voice-stop" x="7" y="7" width="10" height="10" rx="2"/>' +
    '<path class="voice-off" d="m3 3 18 18"/></svg>';
  var errors = {
    'not-allowed': 'Microphone access is blocked. Allow it in the browser to dictate.',
    'service-not-allowed': 'Dictation is unavailable in this browser. You can keep typing.',
    'audio-capture': 'No microphone is available. Check the microphone and try again.',
    'no-speech': 'No speech was detected. Try again when ready.',
    'network': 'Dictation lost its connection. Try again when connected.',
    'language-not-supported': 'Dictation is unavailable for this language. You can keep typing.'
  };

  function cancel() {
    if (active) active.cancel();
  }

  document.querySelectorAll('input, textarea').forEach(function (field) {
    if (field.tagName !== 'TEXTAREA' && !/^(text|search|email|tel)$/.test(field.type)) return;
    // Website, booking and careers URLs are pasted rather than dictated.
    if (field.inputMode === 'url' || field.autocomplete === 'url') return;
    if (field.hidden || field.style.display === 'none' || field.name === '_honey' ||
        field.getAttribute('aria-hidden') === 'true' || field.dataset.voice === 'off') return;

    var label = field.getAttribute('aria-label') ||
      (field.labels && field.labels.length ? field.labels[0].textContent.trim() : '') ||
      field.placeholder || 'this field';
    var idleLabel = 'Dictate ' + label.charAt(0).toLowerCase() + label.slice(1);
    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'voice-input-button';
    button.innerHTML = icon;
    button.setAttribute('aria-controls', field.id);
    var status = document.createElement('span');
    status.className = 'voice-status';
    status.setAttribute('role', 'status');
    status.setAttribute('aria-live', 'polite');
    status.setAttribute('aria-atomic', 'true');
    if (field.parentElement.classList.contains('composer')) {
      field.after(button, status);
    } else {
      var wrap = document.createElement('span');
      wrap.className = 'voice-field' + (field.tagName === 'TEXTAREA' ? ' multiline' : '');
      field.classList.add('voice-text');
      if (field.parentElement.tagName === 'LABEL') {
        // Keep the microphone and announcements outside the input's label.
        var fieldLabel = field.parentElement;
        wrap.classList.add('labelled');
        if (fieldLabel.classList.contains('rfind')) wrap.classList.add('rfind');
        fieldLabel.before(wrap);
        wrap.append(fieldLabel, button, status);
      } else {
        field.before(wrap);
        wrap.append(field, button, status);
      }
    }

    function state(name, message) {
      button.dataset.state = name;
      button.setAttribute('aria-pressed', String(name === 'starting' || name === 'listening' || name === 'stopping'));
      var description = message || idleLabel;
      button.setAttribute('aria-label', description);
      status.textContent = message || '';
    }
    function availability() {
      button.disabled = !Recognition || !window.isSecureContext || field.disabled || field.readOnly;
      if (button.disabled && active && active.field === field) cancel();
      if (!Recognition || !window.isSecureContext) {
        state('unavailable', 'Dictation is unavailable in this browser. You can keep typing.');
      }
    }
    state('idle');
    availability();
    new MutationObserver(availability).observe(field, { attributes: true,
      attributeFilter: ['disabled', 'readonly'] });

    button.addEventListener('click', function (event) {
      event.preventDefault(); // A microphone inside a label must not reopen the phone keyboard.
      if (active && active.field === field) { active.stop(); return; }
      cancel();
      if (button.disabled) return;
      var recognition;
      try { recognition = new Recognition(); }
      catch (_) { state('error', errors['service-not-allowed']); return; }
      var start = field.selectionStart;
      var end = field.selectionEnd;
      if (start === null || start === undefined) start = field.value.length;
      if (end === null || end === undefined) end = start;
      var before = field.value.slice(0, start), after = field.value.slice(end);
      var lastValue = field.value, changed = false, writing = false, finished = false;
      var timer, stopTimer;
      var session = { field: field, button: button, cancel: abort, stop: stop };
      active = session;

      function finish(message) {
        if (finished) return;
        finished = true;
        clearTimeout(timer);
        clearTimeout(stopTimer);
        field.removeEventListener('input', edited);
        field.removeEventListener('beforeinput', edited);
        if (active === session) active = null;
        state(message ? 'error' : 'idle', message ||
          (changed ? 'Dictation ready. Edit the text before submitting.' : ''));
        // Keep the accessible action name stable after a successful recording.
        if (!message) button.setAttribute('aria-label', idleLabel);
      }
      function abort() {
        finish(); // Late results from an aborted session must never overwrite an edit.
        try { recognition.abort(); } catch (_) {}
      }
      function stop() {
        if (finished || button.dataset.state === 'stopping') return;
        state('stopping', 'Finishing dictation');
        try { recognition.stop(); } catch (_) { abort(); return; }
        stopTimer = setTimeout(abort, 3000);
      }
      function edited() { if (!writing) abort(); }
      field.addEventListener('beforeinput', edited);
      field.addEventListener('input', edited);
      recognition.lang = field.lang || document.documentElement.lang || navigator.language || 'en-US';
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.maxAlternatives = 1;
      recognition.onstart = function () {
        if (finished) { try { recognition.abort(); } catch (_) {} return; }
        clearTimeout(timer);
        if (button.dataset.state !== 'stopping') state('listening', 'Stop dictation');
        timer = setTimeout(stop, 60000);
      };
      recognition.onresult = function (event) {
        if (finished) return;
        if (field.value !== lastValue || field.disabled || field.readOnly) { abort(); return; }
        // Results replace the current session's draft, so interim revisions never duplicate words.
        var words = Array.from(event.results, function (result) { return result[0].transcript; }).join(' ').trim();
        if (!words) return;
        var left = before && !/\s$/.test(before) && !/^[.,!?;:]/.test(words) ? ' ' : '';
        var right = after && !/^\s|^[.,!?;:]/.test(after) ? ' ' : '';
        var spoken = left + words + right;
        if (field.maxLength >= 0) spoken = spoken.slice(0, Math.max(0, field.maxLength - before.length - after.length));
        lastValue = before + spoken + after;
        field.value = lastValue;
        changed = true;
        try { field.setSelectionRange(before.length + spoken.length, before.length + spoken.length); } catch (_) {}
        writing = true;
        field.dispatchEvent(new Event('input', { bubbles: true }));
        writing = false;
      };
      recognition.onerror = function (event) {
        if (finished) return;
        finish(event.error === 'aborted' ? '' :
          (errors[event.error] || 'Dictation stopped. You can edit the text or try again.'));
        try { recognition.abort(); } catch (_) {}
      };
      recognition.onend = function () { finish(changed ? '' : errors['no-speech']); };
      state('starting', 'Stop dictation');
      // Some browsers expose the API without a working speech service. Never leave a stuck mic.
      timer = setTimeout(function () {
        finish(errors['service-not-allowed']);
        try { recognition.abort(); } catch (_) {}
      }, 60000);
      try { recognition.start(); }
      catch (_) { finish(errors['service-not-allowed']); }
    });
  });

  document.addEventListener('submit', cancel, true);
  document.addEventListener('reset', cancel, true);
  document.addEventListener('close', cancel, true);
  document.addEventListener('pointerdown', function (event) {
    if (active && !active.button.contains(event.target) && event.target !== active.field) cancel();
  }, true);
  document.addEventListener('focusin', function (event) {
    if (active && !active.button.contains(event.target) && event.target !== active.field) cancel();
  });
  document.addEventListener('keydown', function (event) {
    if (active && event.key === 'Escape') { event.preventDefault(); cancel(); }
  }, true);
  document.addEventListener('visibilitychange', function () { if (document.hidden) cancel(); });
  window.addEventListener('pagehide', cancel);
})();
