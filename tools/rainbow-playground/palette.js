/* Standalone OKLCH generator. No specspec runtime or browser API dependency. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.RainbowPlayground = api;
})(globalThis, () => {
  'use strict';
  const DEFAULTS = { count: 7, lightness: 0.69, chroma: 0.12, startHue: 320, endHue: 20 };
  function validate(input) {
    const p = Object.fromEntries(Object.keys(DEFAULTS).map(key => [key, Number(input[key])]));
    if (Object.values(p).some(v => !Number.isFinite(v)) || Object.keys(DEFAULTS).some(key => input[key] === '' || input[key] == null)) throw new Error('All parameters must be numbers.');
    if (!Number.isInteger(p.count) || p.count < 2 || p.count > 32) throw new Error('Color count must be an integer from 2 to 32.');
    if (p.lightness < 0 || p.lightness > 1) throw new Error('Lightness must be between 0 and 1.');
    if (p.chroma < 0 || p.chroma > 0.4) throw new Error('Chroma must be between 0 and 0.4.');
    if ([p.startHue, p.endHue].some(h => h < 0 || h > 360)) throw new Error('Hue endpoints must be between 0 and 360 degrees.');
    return p;
  }
  function linearRGB(L, C, H) {
    const a = C * Math.cos(H * Math.PI / 180), b = C * Math.sin(H * Math.PI / 180);
    const l = (L + 0.3963377774*a + 0.2158037573*b)**3;
    const m = (L - 0.1055613458*a - 0.0638541728*b)**3;
    const s = (L - 0.0894841775*a - 1.291485548*b)**3;
    return [4.0767416621*l - 3.3077115913*m + 0.2309699292*s,
      -1.2684380046*l + 2.6097574011*m - 0.3413193965*s,
      -0.0041960863*l - 0.7034186147*m + 1.707614701*s];
  }
  const inGamut = rgb => rgb.every(v => v >= -1e-7 && v <= 1+1e-7);
  function sample(L, C, H) {
    let chroma = C;
    const gamutReduced = !inGamut(linearRGB(L, C, H));
    if (gamutReduced) {
      let low = 0, high = C;
      for (let i=0; i<24; i++) {
        const middle = (low+high)/2;
        if (inGamut(linearRGB(L, middle, H))) low = middle; else high = middle;
      }
      chroma = low;
    }
    const hex = '#'+linearRGB(L, chroma, H).map(v => {
      // Clamp only tiny matrix/rounding error after fixed-L/H chroma reduction.
      const c = Math.max(0, Math.min(1, v));
      const srgb = c <= 0.0031308 ? 12.92*c : 1.055*c**(1/2.4)-0.055;
      return Math.round(srgb*255).toString(16).padStart(2, '0');
    }).join('');
    return { hex, hue: H, lightness: L, requestedChroma: C, chroma, gamutReduced };
  }
  function generate(input) {
    const parameters = validate(input);
    const samples = Array.from({ length: parameters.count }, (_, i) => sample(parameters.lightness, parameters.chroma,
      parameters.startHue + (parameters.endHue-parameters.startHue)*i/(parameters.count-1)));
    const nearest = (hue, used = new Set()) => {
      const available = samples.flatMap((s,i) => used.has(i) ? [] : [i]);
      const candidates = available.length ? available : samples.map((s,i) => i);
      const distance = h => { const d = Math.abs(h-hue)%360; return Math.min(d, 360-d); };
      return candidates.reduce((best,i) => distance(samples[i].hue) < distance(samples[best].hue) ? i : best);
    };
    // Reserve the Added green near the default Git text #81b88b (~149.5° OKLCH).
    // Requirement gets an unused green-family swatch; narrow palettes may reuse.
    const roles = { implementation: nearest(300), added: nearest(149.5), changed: nearest(264),
      removed: nearest(30), 'source-changed': nearest(75) };
    return { kind: 'specspec-rainbow-palette', version: 1, parameters, colors: samples.map(s => s.hex),
      mappings: { requirement: nearest(165, new Set(Object.values(roles))), ...roles },
      gamutReducedIndices: samples.flatMap((s,i) => s.gamutReduced ? [i] : []), samples };
  }
  function css(result) {
    return ':root {\n'+result.colors.map((hex,i) => `  --rainbow-${i+1}: ${hex};`).join('\n')+'\n'+
      Object.entries(result.mappings).map(([kind,index]) => `  --palette-${kind}: var(--rainbow-${index+1});`).join('\n')+'\n}\n';
  }
  return { DEFAULTS, validate, linearRGB, inGamut, generate, css };
});
