/* Spatial navigation only. A camera never relayouts or mutates the graph. */
(function (root, factory) {
  const commonJS = typeof module === 'object' && module.exports;
  const api = factory(commonJS ? require('./vendor/graph-vendor.js') : root.specspecVendor);
  if (commonJS) module.exports = api;
  else root.specspecCamera = api;
})(globalThis, vendor => {
  'use strict';
  const MIN_SCALE = 0.12, MAX_SCALE = 2.5;
  const clamp = k => Math.max(MIN_SCALE, Math.min(MAX_SCALE, k));
  function validTransform(value) {
    return value && [value.x, value.y, value.k].every(Number.isFinite) && value.k > 0
      ? { x: value.x, y: value.y, k: clamp(value.k) } : undefined;
  }
  function frameTransform(bounds, width, height, maximumScale = 1) {
    const k = clamp(Math.min((Math.max(120, width) - 80) / Math.max(1, bounds.width),
      (Math.max(120, height) - 80) / Math.max(1, bounds.height), maximumScale));
    return { x: width / 2 - (bounds.x + bounds.width / 2) * k,
      y: height / 2 - (bounds.y + bounds.height / 2) * k, k };
  }

  function rectangleBounds(start, end, pose) {
    if (![start?.x, start?.y, end?.x, end?.y, pose?.x, pose?.y, pose?.k].every(Number.isFinite)
      || pose.k <= 0 || Math.abs(end.x - start.x) < 4 || Math.abs(end.y - start.y) < 4) return;
    return { x: (Math.min(start.x, end.x) - pose.x) / pose.k,
      y: (Math.min(start.y, end.y) - pose.y) / pose.k,
      width: Math.abs(end.x - start.x) / pose.k, height: Math.abs(end.y - start.y) / pose.k };
  }

  function createCamera(viewport, world, { onChange = () => {}, onFrame = () => {}, onRectangleChange = () => {} } = {}) {
    const win = viewport.ownerDocument.defaultView;
    const selection = vendor.select(viewport);
    const native = target => target?.closest?.('#node-details, input, textarea, select, a, label, [contenteditable]:not([contenteditable="false"]), button:not(.card)');
    const dimensions = () => ({ width: viewport.clientWidth || 1000, height: viewport.clientHeight || 650 });
    const duration = () => !win.matchMedia || win.matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 180;
    let current = { x: 0, y: 0, k: 1 };
    const mac = /Mac|iPhone|iPad|iPod/i.test(win.navigator.userAgentData?.platform || win.navigator.platform);
    const primaryHeld = event => Boolean(mac ? event.metaKey : event.ctrlKey);
    const modifier = event => primaryHeld(event) && !(mac ? event.ctrlKey : event.metaKey) && !event.shiftKey && !event.altKey;
    let armed = false, held = false, suppressed = false, inside = false, blocked = false, pointerTarget, drag, notified = false;
    let swallowClick = false, clickTimer, releasePending;
    const band = viewport.ownerDocument.createElement('div');
    band.id = 'frame-selection'; band.className = 'frame-selection'; band.hidden = true;
    band.setAttribute('aria-hidden', 'true'); viewport.append(band);
    const behavior = vendor.zoom().scaleExtent([MIN_SCALE, MAX_SCALE])
      .extent(() => { const { width, height } = dimensions(); return [[0, 0], [width, height]]; })
      .clickDistance(4).duration(180)
      .filter(event => {
        if (drag || native(event.target)) return false;
        if (event.type === 'wheel') return true;
        if (event.type.startsWith('touch')) return !event.target.closest('.card');
        return event.button === 1 || (event.button === 0 && !event.ctrlKey && !event.target.closest('.card'));
      })
      .on('start', event => {
        if (event.sourceEvent?.type === 'mousedown') {
          event.sourceEvent.preventDefault(); viewport.classList.add('panning');
        }
      })
      .on('zoom', event => {
        current = { x: event.transform.x, y: event.transform.y, k: event.transform.k };
        world.style.transform = `translate(${current.x}px, ${current.y}px) scale(${current.k})`;
        viewport.style.backgroundPosition = `${current.x}px ${current.y}px`;
        const grid = 24 * current.k * 2 ** Math.max(0, Math.ceil(Math.log2(0.75 / current.k)));
        viewport.style.backgroundSize = `${grid}px ${grid}px`;
        viewport.dataset.cameraX = current.x; viewport.dataset.cameraY = current.y; viewport.dataset.scale = current.k;
        onChange({ ...current }, false);
      })
      .on('end', () => { viewport.classList.remove('panning'); onChange({ ...current }, true); });
    selection.call(behavior).on('dblclick.zoom', null);
    // No browser auto-scroll or accidental clicks after middle-button navigation.
    const auxiliary = event => { if (event.button === 1 && !native(event.target)) event.preventDefault(); };
    viewport.addEventListener('auxclick', auxiliary);

    function syncRectangle() {
      const ready = inside && !blocked && !native(pointerTarget) && (armed || held && !suppressed);
      viewport.classList.toggle('rectangle-ready', Boolean(drag || ready));
      viewport.classList.toggle('rectangle-dragging', Boolean(drag));
      const active = Boolean(armed || drag || ready);
      if (notified !== active) { notified = active; onRectangleChange(active); }
    }
    function modifiers(event) {
      held = modifier(event);
      blocked = Boolean(event.shiftKey || event.altKey || (mac ? event.ctrlKey : event.metaKey));
      if (!primaryHeld(event)) suppressed = false;
    }
    const point = event => {
      const area = viewport.getBoundingClientRect();
      return { x: event.clientX - area.left - viewport.clientLeft, y: event.clientY - area.top - viewport.clientTop };
    };
    function paintBand(end) {
      band.style.left = `${Math.min(drag.start.x, end.x)}px`; band.style.top = `${Math.min(drag.start.y, end.y)}px`;
      band.style.width = `${Math.abs(end.x - drag.start.x)}px`; band.style.height = `${Math.abs(end.y - drag.start.y)}px`;
    }
    function consumeReleaseClick() {
      swallowClick = true; win.clearTimeout(clickTimer);
      clickTimer = win.setTimeout(() => { swallowClick = false; }, 0);
    }
    function finishRectangle(event, cancel = false) {
      const active = drag;
      if (event) modifiers(event);
      const bounds = active && !cancel ? rectangleBounds(active.start, point(event), active.pose) : undefined;
      drag = undefined; armed = false; suppressed = held; band.hidden = true;
      if (active) {
        try { viewport.releasePointerCapture?.(active.id); } catch { /* Capture may already be released. */ }
        if (cancel) { releasePending = active.id; swallowClick = true; win.clearTimeout(clickTimer); }
        else consumeReleaseClick();
      }
      syncRectangle();
      if (bounds) { const { width, height } = dimensions(); set(frameTransform(bounds, width, height, MAX_SCALE), true); }
    }
    const trackRectangle = event => {
      if (drag) return;
      inside = event.pointerType !== 'touch'; pointerTarget = event.target; modifiers(event); syncRectangle();
    };
    const leaveRectangle = () => { inside = false; if (!drag) syncRectangle(); };
    const beginRectangle = event => {
      modifiers(event); inside = true; pointerTarget = event.target;
      if (drag || event.button !== 0 || event.pointerType === 'touch' || native(event.target)
        || event.shiftKey || event.altKey || (mac ? event.ctrlKey : event.metaKey)
        || !(armed || held && !suppressed)) { syncRectangle(); return; }
      event.preventDefault(); selection.interrupt();
      drag = { id: event.pointerId ?? 1, start: point(event), pose: { ...current } };
      band.hidden = false; paintBand(drag.start); syncRectangle();
      try { viewport.setPointerCapture?.(drag.id); } catch { /* Synthetic/unsupported pointer capture. */ }
    };
    const movingRectangle = event => {
      if (!drag || (event.pointerId ?? 1) !== drag.id) return;
      event.preventDefault(); event.stopPropagation(); paintBand(point(event));
    };
    const releaseRectangle = event => {
      if (!drag && releasePending === (event.pointerId ?? 1)) {
        releasePending = undefined; event.preventDefault(); event.stopPropagation(); consumeReleaseClick(); return;
      }
      if (!drag || (event.pointerId ?? 1) !== drag.id) return;
      event.preventDefault(); event.stopPropagation(); finishRectangle(event);
    };
    const cancelPointer = event => { if (drag && (event.pointerId ?? 1) === drag.id) finishRectangle(undefined, true); };
    const rectangleKeys = event => {
      modifiers(event);
      const editing = native(event.target) && !event.target.closest?.('.camera-controls');
      if (event.key === 'Escape' && (drag || !editing && (armed || viewport.classList.contains('rectangle-ready')))) {
        event.preventDefault(); finishRectangle(undefined, true);
      } else syncRectangle();
    };
    const blurRectangle = () => { held = false; inside = false; finishRectangle(undefined, true); };
    const mouseGuard = event => { if (drag) { event.preventDefault(); event.stopImmediatePropagation(); } };
    const clickGuard = event => { if (swallowClick) { event.preventDefault(); event.stopImmediatePropagation(); } };
    const freshPointer = () => { if (!drag) { releasePending = undefined; swallowClick = false; win.clearTimeout(clickTimer); } };
    win.addEventListener('pointerdown', freshPointer, true);
    viewport.addEventListener('pointerdown', beginRectangle, true);
    for (const name of ['pointerover', 'pointermove']) viewport.addEventListener(name, trackRectangle);
    viewport.addEventListener('pointerleave', leaveRectangle);
    viewport.addEventListener('lostpointercapture', cancelPointer);
    viewport.addEventListener('mousedown', mouseGuard, true);
    viewport.addEventListener('wheel', mouseGuard, { capture: true, passive: false });
    win.addEventListener('pointermove', movingRectangle, true);
    win.addEventListener('pointerup', releaseRectangle, true);
    win.addEventListener('pointercancel', cancelPointer, true);
    win.addEventListener('click', clickGuard, true);
    win.addEventListener('keydown', rectangleKeys);
    win.addEventListener('keyup', rectangleKeys);
    win.addEventListener('blur', blurRectangle);

    function collection(animate) {
      selection.interrupt();
      return animate && duration() ? selection.transition().duration(duration()) : selection;
    }
    function set(value, animate = false) {
      const valid = validTransform(value);
      if (!valid) return;
      collection(animate).call(behavior.transform, vendor.zoomIdentity.translate(valid.x, valid.y).scale(valid.k));
    }
    function scaleBy(factor, animate = true) { collection(animate).call(behavior.scaleBy, factor); }
    function scaleTo(k, animate = true) { collection(animate).call(behavior.scaleTo, clamp(k)); }
    function pan(x, y) { set({ x: current.x + x, y: current.y + y, k: current.k }); }
    const keyboard = event => {
      if (drag || native(event.target) || event.ctrlKey || event.altKey || event.metaKey) return;
      const commands = { ArrowLeft: () => pan(60, 0), ArrowRight: () => pan(-60, 0),
        ArrowUp: () => pan(0, 60), ArrowDown: () => pan(0, -60),
        '+': () => scaleBy(1.25), '=': () => scaleBy(1.25), '-': () => scaleBy(0.8),
        '1': () => scaleTo(1), Home: onFrame, f: onFrame, F: onFrame };
      if (commands[event.key]) { event.preventDefault(); commands[event.key](); }
    };
    viewport.addEventListener('keydown', keyboard);
    // Keyboard focus on offscreen compact nodes should reveal them, without scrolling the world.
    const focus = event => {
      const card = event.target.closest('.card');
      if (!card || card.classList.contains('expanded') || !card.matches(':focus-visible')) return;
      const rect = card.getBoundingClientRect(), area = viewport.getBoundingClientRect();
      const dx = rect.left < area.left ? area.left - rect.left + 24 : rect.right > area.right ? area.right - rect.right - 24 : 0;
      const dy = rect.top < area.top ? area.top - rect.top + 24 : rect.bottom > area.bottom ? area.bottom - rect.bottom - 24 : 0;
      if (dx || dy) pan(dx, dy);
    };
    viewport.addEventListener('focusin', focus);
    return { value: () => ({ ...current }), set, scaleBy, scaleTo, dimensions, stop: () => selection.interrupt(),
      rectangleModifier: mac ? 'Command' : 'Ctrl',
      toggleRectangle: () => { if (armed || drag) finishRectangle(undefined, true); else { armed = true; syncRectangle(); } },
      frame: (bounds, animate = true) => { const { width, height } = dimensions(); set(frameTransform(bounds, width, height), animate); },
      dispose: () => {
        blurRectangle(); win.clearTimeout(clickTimer); band.remove();
        selection.interrupt().on('.zoom', null); viewport.removeEventListener('keydown', keyboard);
        viewport.removeEventListener('focusin', focus); viewport.removeEventListener('auxclick', auxiliary);
        viewport.removeEventListener('pointerdown', beginRectangle, true);
        for (const name of ['pointerover', 'pointermove']) viewport.removeEventListener(name, trackRectangle);
        viewport.removeEventListener('pointerleave', leaveRectangle); viewport.removeEventListener('lostpointercapture', cancelPointer);
        viewport.removeEventListener('mousedown', mouseGuard, true); viewport.removeEventListener('wheel', mouseGuard, true);
        win.removeEventListener('pointerdown', freshPointer, true);
        win.removeEventListener('pointermove', movingRectangle, true); win.removeEventListener('pointerup', releaseRectangle, true);
        win.removeEventListener('pointercancel', cancelPointer, true); win.removeEventListener('click', clickGuard, true);
        win.removeEventListener('keydown', rectangleKeys); win.removeEventListener('keyup', rectangleKeys); win.removeEventListener('blur', blurRectangle);
      },
    };
  }
  return { MIN_SCALE, MAX_SCALE, validTransform, frameTransform, rectangleBounds, createCamera };
});
