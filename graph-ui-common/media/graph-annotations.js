/* Immutable spotlights exchange messages; one editable per-view set owns all rings. */
(() => {
  function create({ restored, snapshot, cards, save, send, frame }) {
    const $ = id => document.getElementById(id);
    let shots = [], loaded = false, error, draft, creating = false;
    let open = Boolean(restored.annotationPanelOpen);
    const fresh = new Set(), highlights = new Map();
    const inks = ['#e65e66', '#5c9eff', '#58ba7a', '#aa79df', '#35bdbe', '#dfc24d'];
    for (const member of Array.isArray(restored.annotationHighlights) ? restored.annotationHighlights : []) {
      if (member && typeof member.id === 'string' && /^[0-9a-f]{40}(?:[0-9a-f]{24})?$/.test(member.blob) && /^#[0-9a-f]{6}$/i.test(member.color))
        highlights.set(member.id, { id: member.id, blob: member.blob, color: member.color.toLowerCase() });
    }
    const message = shot => [...new Set(shot.groups.map(group => group.text))].join(' · ');
    function resolution(member) {
      const state = snapshot();
      if (!state) return 'unavailable';
      const target = state.snapshot.nodes.some(n => n.id === member.id);
      const base = !target && state.diff?.base.nodes.some(n => n.id === member.id);
      if (!target && !base) return 'absent';
      const versions = (target ? state.node_blobs : state.base_node_blobs)?.[member.id];
      if (!Array.isArray(versions)) return 'unavailable';
      return versions.includes(member.blob) ? 'exact' : 'changed';
    }
    function paint() {
      for (const card of cards().children) {
        const member = highlights.get(card.dataset.nodeId);
        if (member && resolution(member) === 'exact') {
          card.dataset.annotationLabel = 'highlight';
          card.style.setProperty('--annotation-ink', member.color);
          card.setAttribute('aria-description', 'Node highlight. Exact captured node version. Shift-click cycles color; Ctrl/Command+Shift-click clears.');
        } else {
          delete card.dataset.annotationLabel; card.style.removeProperty('--annotation-ink'); card.removeAttribute('aria-description');
        }
      }
    }
    function position() {
      if (!open) return;
      const panel = $('annotations-panel'), anchor = $('annotations-toggle').getBoundingClientRect();
      const width = Math.min(370, Math.max(0, window.innerWidth - 16));
      const top = Math.min(anchor.bottom + 4, Math.max(8, window.innerHeight - 100));
      panel.style.left = `${Math.max(8, Math.min(anchor.left, window.innerWidth - width - 8))}px`;
      panel.style.top = `${top}px`;
      panel.style.maxHeight = `${Math.max(80, window.innerHeight - top - 8)}px`;
    }
    const menuItems = () => [...$('annotations-panel').querySelectorAll('button:not(:disabled)')];
    function toggle(value, focus = true) {
      open = value;
      if (open) fresh.clear();
      render(); save();
      if (focus) (open ? menuItems()[0] : $('annotations-toggle'))?.focus({ preventScroll: true });
    }
    function element(tag, className, text) {
      const item = document.createElement(tag);
      if (className) item.className = className;
      if (text !== undefined) item.textContent = text;
      return item;
    }
    function counts(shot) {
      const totals = { exact: 0, changed: 0, absent: 0, unavailable: 0 };
      const members = new Map();
      for (const group of shot.groups) for (const member of group.nodes) members.set(member.id, member);
      members.forEach(member => totals[resolution(member)]++);
      return Object.entries(totals).filter(([, count]) => count).map(([kind, count]) => `${count} ${kind === 'changed' ? 'different version' : kind === 'absent' ? 'not in view' : kind}`).join(' · ');
    }
    function render() {
      const count = fresh.size;
      $('spotlights-count').textContent = count ? String(count) : '';
      $('spotlights-count').hidden = !count;
      $('annotations-toggle').setAttribute('aria-label', `Spotlights${count ? `, ${count} new` : ''}${error ? ', list out of date' : ''}`);
      $('annotations-toggle').title = error ? `Spotlights: ${error}` : 'Show retained spotlights';
      $('annotations-toggle').setAttribute('aria-expanded', String(open));
      $('annotations-panel').hidden = !open;
      $('annotation-error').hidden = !error; $('annotation-error').textContent = error ? `List out of date: ${error}` : '';
      $('annotation-clear').disabled = !highlights.size;
      $('annotation-create').disabled = !highlights.size || creating;
      $('annotation-create').textContent = `Create spotlight from highlights${highlights.size ? ` (${highlights.size})` : ''}…`;
      $('annotation-flush').disabled = !shots.length;
      const list = $('annotation-list'), scroll = list.scrollTop;
      const focus = list.contains(document.activeElement) ? document.activeElement.dataset.annotationFocus : undefined;
      const top = list.getBoundingClientRect().top;
      const anchor = [...list.children].find(item => item.getBoundingClientRect().bottom > top);
      const anchorId = anchor?.dataset.shotId, anchorTop = anchor?.getBoundingClientRect().top;
      list.replaceChildren();
      for (const shot of shots) {
        const button = element('button', 'annotation-label'); button.type = 'button';
        button.dataset.shotId = shot.id; button.dataset.annotationFocus = shot.id;
        button.setAttribute('role', 'menuitem');
        const text = element('span', 'annotation-label-text', message(shot));
        text.append(element('small', '', `${new Date(shot.created_at).toLocaleString()} · ${counts(shot)}`));
        button.append(text);
        if (fresh.has(shot.id)) button.append(element('strong', 'annotation-new', 'New'));
        button.addEventListener('click', () => {
          highlights.clear();
          for (const group of shot.groups) for (const member of group.nodes) {
            if (resolution(member) === 'exact') highlights.set(member.id, { id: member.id, blob: member.blob, color: group.color });
          }
          paint();
          const ids = [...highlights.keys()];
          toggle(false); // Close before framing: the whole canvas is available.
          frame(ids);
        });
        list.append(button);
      }
      $('annotation-list-summary').textContent = shots.length ? `${shots.length} spotlight${shots.length === 1 ? '' : 's'}` : 'No local spotlights. Use specspec spotlight add.';
      list.scrollTop = scroll;
      const newAnchor = anchorId && [...list.children].find(item => item.dataset.shotId === anchorId);
      if (newAnchor && anchorTop !== undefined) list.scrollTop += newAnchor.getBoundingClientRect().top - anchorTop;
      if (focus) [...list.children].find(item => item.dataset.annotationFocus === focus)?.focus({ preventScroll: true });
      position();
    }
    $('annotations-toggle').addEventListener('click', () => toggle(!open));
    $('annotations-toggle').addEventListener('keydown', event => {
      if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
        event.preventDefault(); toggle(true);
        if (event.key === 'ArrowUp') menuItems().at(-1)?.focus();
      }
    });
    $('viewport').addEventListener('click', event => {
      if (!event.shiftKey || event.altKey || event.button !== 0) return;
      if (event.target.closest?.('input, textarea, select, a, label, [contenteditable]:not([contenteditable="false"]), button:not(.card)')) return;
      const card = event.target.closest?.('.card'), id = card?.dataset.nodeId;
      if (card?.parentElement !== cards() || !id || id === '__draft__') return;
      event.preventDefault(); event.stopImmediatePropagation();
      if (event.ctrlKey || event.metaKey) highlights.delete(id);
      else {
        const state = snapshot(), target = state?.snapshot.nodes.some(n => n.id === id);
        const blob = (target ? state?.node_blobs : state?.base_node_blobs)?.[id]?.[0];
        if (!blob) { $('annotation-live').textContent = 'This node has no exact version available for highlighting. Refresh and retry.'; return; }
        const previous = highlights.get(id);
        const index = previous && resolution(previous) === 'exact' ? inks.indexOf(previous.color.toLowerCase()) : -1;
        if (index === inks.length - 1) highlights.delete(id);
        else highlights.set(id, { id, blob, color: inks[index + 1] });
      }
      paint(); render(); save();
    }, true);
    $('annotation-clear').addEventListener('click', () => { highlights.clear(); paint(); toggle(false); });
    const dialog = $('annotation-compose');
    function closeCompose() {
      if (dialog.close) dialog.close(); else dialog.removeAttribute('open');
      $('annotations-toggle').focus({ preventScroll: true });
    }
    $('annotation-create').addEventListener('click', () => {
      draft = [...highlights.values()].map(member => ({ ...member }));
      toggle(false);
      $('annotation-message').value = ''; $('annotation-compose-error').textContent = '';
      if (dialog.showModal) dialog.showModal(); else dialog.setAttribute('open', '');
      $('annotation-message').focus();
    });
    $('annotation-compose-cancel').addEventListener('click', closeCompose);
    dialog.addEventListener('cancel', event => { event.preventDefault(); if (!creating) closeCompose(); });
    $('annotation-compose-form').addEventListener('submit', event => {
      event.preventDefault();
      const text = $('annotation-message').value.trim();
      if (creating) return;
      if (!text || [...text].length > 500 || !draft?.length) { $('annotation-compose-error').textContent = 'Provide a message of 1–500 characters and at least one highlight.'; return; }
      const groups = [];
      for (const member of draft) {
        let group = groups.find(group => group.color === member.color);
        if (!group) { group = { text, color: member.color, nodes: [] }; groups.push(group); }
        group.nodes.push({ id: member.id, blob: member.blob });
      }
      creating = true; $('annotation-compose-save').disabled = true; $('annotation-compose-cancel').disabled = true;
      $('annotation-compose-error').textContent = 'Creating spotlight…';
      send({ type: 'annotation-create', groups });
    });
    $('annotation-flush').addEventListener('click', () => { toggle(false); send({ type: 'annotation-flush' }); });
    $('annotations-panel').addEventListener('keydown', event => {
      const items = menuItems(), index = items.indexOf(document.activeElement);
      if (event.key === 'Escape') { event.preventDefault(); event.stopPropagation(); toggle(false); }
      else if (['ArrowDown', 'ArrowUp', 'Home', 'End'].includes(event.key)) {
        event.preventDefault();
        const next = event.key === 'Home' ? 0 : event.key === 'End' ? items.length - 1 : (index + (event.key === 'ArrowDown' ? 1 : -1) + items.length) % items.length;
        items[next]?.focus();
      }
    });
    document.addEventListener('pointerdown', event => {
      if (open && !$('annotations-panel').contains(event.target) && !$('annotations-toggle').contains(event.target)) toggle(false, false);
    });
    document.addEventListener('focusin', event => {
      if (open && !$('annotations-panel').contains(event.target) && !$('annotations-toggle').contains(event.target)) toggle(false, false);
    });
    window.addEventListener('resize', position);
    render();
    return {
      presentation: () => ({ annotationPanelOpen: open, annotationHighlights: [...highlights.values()].map(member => ({ ...member })) }),
      created(message) {
        creating = false; $('annotation-compose-save').disabled = false; $('annotation-compose-cancel').disabled = false;
        if (message) $('annotation-compose-error').textContent = message;
        else { closeCompose(); $('annotation-live').textContent = 'Spotlight created. The agent can read it with specspec spotlight show.'; }
        render();
      },
      changed() { render(); paint(); },
      receive(value) {
        const previous = new Set(shots.map(shot => shot.id));
        const arrivals = loaded ? value.filter(shot => !previous.has(shot.id)) : [];
        shots = value; error = undefined; loaded = true;
        const present = new Set(shots.map(shot => shot.id));
        for (const id of fresh) if (!present.has(id)) fresh.delete(id);
        arrivals.forEach(shot => fresh.add(shot.id));
        if (arrivals.length) $('annotation-live').textContent = `${fresh.size} new spotlight${fresh.size === 1 ? '' : 's'}. Open Spotlights to inspect the retained list.`;
        render(); paint(); save();
      },
      error(message) { error = message; render(); $('annotation-live').textContent = `Local spotlight list could not be refreshed. ${message}`; },
    };
  }
  window.SpecSpecAnnotations = { create };
})();
