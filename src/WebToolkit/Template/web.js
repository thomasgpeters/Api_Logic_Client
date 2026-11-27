/*
 * web.js - Web Toolkit for FutureBasic: the browser's half
 *
 * The page is built by FutureBasic. This script sends what the user does to the FB app, asynchronously (AJAX:
 * fetch, JSON), and applies the changes the app answers with - in place, without reloading the page. Events are sent
 * one at a time, in the order they happened, so the FB code sees them as the user made them; the page stays usable
 * meanwhile. Every event carries the values of the page's fields, so FB always reads what the user sees.
 *
 * The page's lifecycle (Web Events.incl): shown (the FB app's answer to the page request), hidden / visible (tab or
 * window switched), leaving (closed or left), and a keep-alive while the page is visible. A page with unsaved changes
 * in a bound form asks before it is left, unless the form saves itself.
 *
 * Nothing here builds HTML from what a user typed: the server escapes every text, and this script sets text with
 * textContent. No framework, no inline script (the page's Content-Security-Policy allows only this file).
 *
 * MIT License. Copyright (c) 2026 Imagery Business Systems, LLC. See LICENSE.
 */
(function () {
  'use strict';

  const meta = (name) => (document.querySelector('meta[name="' + name + '"]') || {}).content || '';
  const token = meta('fb-token');
  const base = meta('fb-base') || '/';
  const eventURL = base + 'fbweb/event';
  const TYPING_PAUSE = 400;          // ms after the last key before "typed" is sent
  const KEEP_ALIVE = 4 * 60 * 1000;  // while the page is visible
  const BUSY_AFTER = 250;            // ms before the busy bar shows

  let queue = Promise.resolve();
  let pending = 0;
  let busyTimer = null;
  let expired = false;
  const typingTimers = new Map();

  const widgetOf = (el) => (el && el.closest ? el.closest('[data-fb-id]') : null);
  const byId = (id) => document.querySelector('[data-fb-id="' + CSS.escape(id) + '"]');
  const listens = (w, name) => !!w && (' ' + (w.getAttribute('data-fb-events') || '') + ' ').includes(' ' + name + ' ');
  const inputOf = (w) => (w.hasAttribute('data-fb-input') ? w : w.querySelector('[data-fb-input]'));

  // the values of every field on the page: { widgetId: value }
  function values() {
    const out = {};
    document.querySelectorAll('[data-fb-input]').forEach((el) => {
      const w = widgetOf(el);
      if (!w || el.tagName === 'BUTTON') return;
      const id = w.getAttribute('data-fb-id');
      if (el.hasAttribute('data-fb-radio')) {
        const on = el.querySelector('input[type=radio]:checked');
        out[id] = on ? on.value : '';
      } else if (el.type === 'checkbox') {
        out[id] = el.checked;
      } else {
        out[id] = el.value;
      }
    });
    return out;
  }

  function busy(on) {
    pending += on ? 1 : -1;
    if (pending > 0 && !busyTimer) {
      busyTimer = setTimeout(() => document.documentElement.classList.add('fb-is-busy'), BUSY_AFTER);
    } else if (pending <= 0) {
      pending = 0;
      clearTimeout(busyTimer);
      busyTimer = null;
      document.documentElement.classList.remove('fb-is-busy');
    }
  }

  function banner(text, role) {
    let b = document.querySelector('.fb-banner');
    if (!b) {
      b = document.createElement('div');
      b.className = 'fb-banner';
      b.setAttribute('role', 'status');
      document.body.appendChild(b);
    }
    b.textContent = text;
    b.className = 'fb-banner alert alert-' + (role || 'info');
    b.hidden = !text;
  }

  function sessionEnded() {
    if (expired) return;
    expired = true;
    banner('This page has been idle too long and starts again.', 'warning');
    setTimeout(() => window.location.reload(), 1500);
  }

  // one event, after those before it; answers with the FB app's updates applied
  function send(widget, event, value) {
    const body = JSON.stringify({ token, widget, event, value: value == null ? '' : String(value), values: values() });
    busy(true);
    queue = queue.then(() =>
      fetch(eventURL, { method: 'POST', credentials: 'same-origin', headers: { 'Content-Type': 'application/json' }, body })
        .then((r) => {
          if (!r.ok) throw new Error('HTTP ' + r.status);
          return r.json();
        })
        .then((answer) => {
          banner('');
          if (answer.expired) sessionEnded();
          else apply(answer.updates || []);
        })
        .catch(() => banner('The server did not answer. Check the connection and try again.', 'danger'))
        .finally(() => busy(false)));
    return queue;
  }
  window.fbSend = send;   // for an app's own script, if it has one

  // the lifecycle's last word: the browser does not wait for an answer
  function sendLast(event) {
    const body = JSON.stringify({ token, widget: 'page', event, value: '', values: values() });
    const blob = new Blob([body], { type: 'application/json' });
    if (!(navigator.sendBeacon && navigator.sendBeacon(eventURL, blob))) {
      fetch(eventURL, { method: 'POST', credentials: 'same-origin', headers: { 'Content-Type': 'application/json' }, body, keepalive: true }).catch(() => {});
    }
  }

  function fromHTML(html) {
    const t = document.createElement('template');
    t.innerHTML = html;
    return t.content;
  }

  function setText(w, text) {
    if (w.classList.contains('alert')) {
      w.textContent = text;
      w.classList.toggle('fb-empty', !text);
    } else if (w.matches('.fb-field, .fb-check, .fb-radio')) {
      const label = w.querySelector('label, legend');
      if (label) label.textContent = text;
    } else {
      w.textContent = text;
    }
  }

  function setValue(w, value) {
    const el = inputOf(w);
    if (!el) return;
    if (el.hasAttribute('data-fb-radio')) {
      el.querySelectorAll('input[type=radio]').forEach((r) => { r.checked = r.value === value; });
    } else if (el !== document.activeElement || el.value !== value) {
      el.value = value;
    }
  }

  function setEnabled(w, on) {
    const targets = w.matches('button, input, select, textarea') ? [w] : w.querySelectorAll('button, input, select, textarea');
    targets.forEach((el) => { el.disabled = !on; });
    w.classList.toggle('fb-disabled', !on);
  }

  function apply(updates) {
    for (const u of updates) {
      if (u.op === 'navigate') { window.location.assign(u.value); continue; }
      if (u.op === 'theme') {
        if (u.value) document.documentElement.setAttribute('data-fb-theme', u.value);
        else document.documentElement.removeAttribute('data-fb-theme');
        continue;
      }
      if (u.op === 'append') {
        const parent = byId(u.parent);
        if (parent && u.html && !byId(u.id)) {
          const box = parent.matches('.fb-field, .fb-table, .fb-list') ? parent.parentNode : parent;
          box.appendChild(fromHTML(u.html));
        }
        continue;
      }
      const w = byId(u.id);
      if (!w) continue;
      switch (u.op) {
        case 'text': setText(w, u.value == null ? '' : String(u.value)); break;
        case 'value': setValue(w, u.value == null ? '' : String(u.value)); break;
        case 'checked': { const el = inputOf(w); if (el) el.checked = !!u.value; break; }
        case 'enabled': setEnabled(w, !!u.value); break;
        case 'visible': w.hidden = !u.value; break;
        case 'dirty': w.toggleAttribute('data-fb-dirty', !!u.value); break;
        case 'remove': w.remove(); break;
        case 'focus': { const el = inputOf(w) || w; el.focus(); break; }
        case 'redraw': {
          if (!u.html) break;
          const focusedId = document.activeElement && document.activeElement.id;
          w.replaceWith(fromHTML(u.html));
          if (focusedId) { const again = document.getElementById(focusedId); if (again) again.focus(); }
          break;
        }
      }
    }
  }

  // a bound form shows its unsaved changes at once (the FB app learns of them with the next event)
  function edited(el) {
    const form = el.closest('[data-fb-bound]');
    if (form) form.setAttribute('data-fb-dirty', '');
  }

  // --- what the user does ---

  document.addEventListener('click', (e) => {
    const row = e.target.closest('[data-fb-row]');
    if (row) { chooseRow(row); return; }
    const w = widgetOf(e.target);
    if (!w) return;
    if (w.tagName === 'A' && w.getAttribute('href') === '#') e.preventDefault();
    if (w.matches('button') || w.tagName === 'A' || listens(w, 'clicked')) {
      if (listens(w, 'clicked')) send(w.getAttribute('data-fb-id'), 'clicked', '');
    }
  });

  function chooseRow(row) {
    const w = widgetOf(row);
    if (!w) return;
    w.querySelectorAll('[data-fb-row]').forEach((r) => {
      const on = r === row;
      r.classList.toggle(r.tagName === 'TR' ? 'table-active' : 'active', on);
      if (on) r.setAttribute('aria-selected', 'true'); else r.removeAttribute('aria-selected');
    });
    send(w.getAttribute('data-fb-id'), 'selected', row.getAttribute('data-fb-row'));
  }

  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Enter') return;
    const row = e.target.closest && e.target.closest('[data-fb-row]');
    if (row) { e.preventDefault(); chooseRow(row); return; }
    const w = widgetOf(e.target);
    if (w && e.target.tagName === 'INPUT' && listens(w, 'entered')) {
      e.preventDefault();
      send(w.getAttribute('data-fb-id'), 'entered', e.target.value);
    }
  });

  document.addEventListener('input', (e) => {
    edited(e.target);
    const w = widgetOf(e.target);
    if (!w || !listens(w, 'typed')) return;
    const id = w.getAttribute('data-fb-id');
    clearTimeout(typingTimers.get(id));
    typingTimers.set(id, setTimeout(() => send(id, 'typed', e.target.value), TYPING_PAUSE));
  });

  document.addEventListener('change', (e) => {
    edited(e.target);
    const w = widgetOf(e.target);
    if (!w || !listens(w, 'changed')) return;
    const v = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    send(w.getAttribute('data-fb-id'), 'changed', v);
  });

  document.addEventListener('submit', (e) => {
    e.preventDefault();
    const w = widgetOf(e.target);
    if (w && listens(w, 'submitted')) send(w.getAttribute('data-fb-id'), 'submitted', '');
  });

  // --- the page's lifecycle ---

  let keepAlive = null;
  function startKeepAlive() {
    clearInterval(keepAlive);
    keepAlive = setInterval(() => send('page', 'alive', ''), KEEP_ALIVE);
  }

  document.addEventListener('visibilitychange', () => {
    if (expired) return;
    if (document.visibilityState === 'hidden') {
      clearInterval(keepAlive);
      sendLast('hidden');
    } else {
      startKeepAlive();
      send('page', 'visible', '');
    }
  });

  window.addEventListener('pagehide', () => { if (!expired) sendLast('leaving'); });

  // unsaved changes in a form that does not save itself: the browser asks before the page is left
  window.addEventListener('beforeunload', (e) => {
    if (!expired && document.querySelector('[data-fb-bound][data-fb-dirty]:not([data-fb-autosave])')) {
      e.preventDefault();
      e.returnValue = '';
    }
  });

  startKeepAlive();
})();
