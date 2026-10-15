/* Immutable spotlight data is separate from per-view selection and session-only arrivals. */
(() => {
  function create({ restored, snapshot, cards, save, send, frame }) {
    const $ = id => document.getElementById(id);
    let shots = [], loaded = false, error, active = restored.activeAnnotation;
    let open = Boolean(restored.annotationPanelOpen);
    const fresh = new Set();
    const activeShot = () => shots.find(shot => shot.id === active);
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
    function matches(shot) {
      const result = new Map();
      for (const group of shot?.groups || []) for (const member of group.nodes)
        if (resolution(member) === 'exact') result.set(member.id, group.color);
      return result;
    }
    function paint() {
      const current = activeShot(), matching = matches(current);
      for (const card of cards().children) {
        const color = matching.get(card.dataset.nodeId);
        if (color) {
          card.dataset.annotationLabel = active;
          card.style.setProperty('--annotation-ink', color);
          card.setAttribute('aria-description', `Spotlight: ${message(current)}. Exact captured node version.`);
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
      $('annotation-clear').disabled = !activeShot();
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
        button.setAttribute('role', 'menuitemradio'); button.setAttribute('aria-checked', String(active === shot.id));
        const text = element('span', 'annotation-label-text', message(shot));
        text.append(element('small', '', `${new Date(shot.created_at).toLocaleString()} · ${counts(shot)}`));
        button.append(text);
        if (fresh.has(shot.id)) button.append(element('strong', 'annotation-new', 'New'));
        button.addEventListener('click', () => {
          active = shot.id; paint();
          const ids = [...matches(shot).keys()];
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
    $('annotation-clear').addEventListener('click', () => { active = undefined; paint(); toggle(false); });
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
      presentation: () => ({ annotationPanelOpen: open, activeAnnotation: active }),
      changed() { render(); paint(); },
      receive(value) {
        const previous = new Set(shots.map(shot => shot.id));
        const arrivals = loaded ? value.filter(shot => !previous.has(shot.id)) : [];
        shots = value; error = undefined; loaded = true;
        const present = new Set(shots.map(shot => shot.id));
        for (const id of fresh) if (!present.has(id)) fresh.delete(id);
        arrivals.forEach(shot => fresh.add(shot.id));
        if (!activeShot()) active = undefined;
        if (arrivals.length) $('annotation-live').textContent = `${fresh.size} new spotlight${fresh.size === 1 ? '' : 's'}. Open Spotlights to inspect the retained list.`;
        render(); paint(); save();
      },
      error(message) { error = message; render(); $('annotation-live').textContent = `Local spotlight list could not be refreshed. ${message}`; },
    };
  }
  window.SpecSpecAnnotations = { create };
})();
