/* Spatial navigation only. A camera never relayouts or mutates the graph. */
(function (root, factory) {
  const commonJS = typeof module === 'object' && module.exports;
  const api = factory(commonJS ? require('./vendor/graph-vendor.js') : root.SpecSpecVendor);
  if (commonJS) module.exports = api;
  else root.SpecSpecCamera = api;
})(globalThis, vendor => {
  'use strict';
  const MIN_SCALE = 0.12, MAX_SCALE = 2.5;
  const clamp = k => Math.max(MIN_SCALE, Math.min(MAX_SCALE, k));
  function validTransform(value) {
    return value && [value.x, value.y, value.k].every(Number.isFinite) && value.k > 0
      ? { x: value.x, y: value.y, k: clamp(value.k) } : undefined;
  }
  function frameTransform(bounds, width, height) {
    const k = clamp(Math.min((Math.max(120, width) - 80) / Math.max(1, bounds.width),
      (Math.max(120, height) - 80) / Math.max(1, bounds.height), 1));
    return { x: width / 2 - (bounds.x + bounds.width / 2) * k,
      y: height / 2 - (bounds.y + bounds.height / 2) * k, k };
  }

  function createCamera(viewport, world, { onChange = () => {}, onFrame = () => {} } = {}) {
    const win = viewport.ownerDocument.defaultView;
    const selection = vendor.select(viewport);
    const native = target => target?.closest?.('#node-details, input, textarea, select, a, [contenteditable="true"], button:not(.card)');
    const dimensions = () => ({ width: viewport.clientWidth || 1000, height: viewport.clientHeight || 650 });
    const duration = () => !win.matchMedia || win.matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 180;
    let current = { x: 0, y: 0, k: 1 };
    const behavior = vendor.zoom().scaleExtent([MIN_SCALE, MAX_SCALE])
      .extent(() => { const { width, height } = dimensions(); return [[0, 0], [width, height]]; })
      .clickDistance(4).duration(180)
      .filter(event => {
        if (native(event.target)) return false;
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
      if (native(event.target) || event.ctrlKey || event.altKey || event.metaKey) return;
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
      frame: (bounds, animate = true) => { const { width, height } = dimensions(); set(frameTransform(bounds, width, height), animate); },
      dispose: () => { selection.interrupt().on('.zoom', null); viewport.removeEventListener('keydown', keyboard);
        viewport.removeEventListener('focusin', focus); viewport.removeEventListener('auxclick', auxiliary); },
    };
  }
  return { MIN_SCALE, MAX_SCALE, validTransform, frameTransform, createCamera };
});
