/* Plain scripts so this page works from file:// without a server or imports. */
(() => {
  'use strict';
  const api = window.RainbowPlayground, $ = id => document.getElementById(id);
  const keys = Object.keys(api.DEFAULTS);
  let current, valid = true;
  const mappingNames = { requirement: 'Requirement', implementation: 'Implementation', added: 'A · Added', changed: 'M · Modified', removed: 'D · Deleted', renamed: 'R · Renamed', 'source-changed': 'Source impact' };
  function node(accent, title, subtitle, manifesto = false) {
    const card = document.createElement('div'); card.className = 'node'+(manifesto ? ' manifesto' : '');
    card.style.setProperty('--accent', accent);
    const heading = document.createElement('strong'), text = document.createElement('small');
    heading.textContent = title; text.textContent = subtitle; card.append(heading, text); return card;
  }
  function exportResult() {
    if (!current) return;
    $('result').value = $('format').value === 'css' ? api.css(current)
      : JSON.stringify($('format').value === 'parameters' ? { kind: current.kind, version: current.version, parameters: current.parameters }
        : { kind: current.kind, version: current.version, parameters: current.parameters, colors: current.colors,
          mappings: current.mappings, gamutReducedIndices: current.gamutReducedIndices }, null, 2);
  }
  function render() {
    try { current = api.generate(Object.fromEntries(keys.map(key => [key, $(key).value]))); }
    catch (error) {
      valid = false; $('copy').disabled = true; $('message').textContent = error.message+' Preview and output still show the last valid result.'; return;
    }
    valid = true; $('copy').disabled = false;
    for (const key of keys) document.querySelector(`[data-for="${key}"]`).value = $(key).value;
    $('swatches').replaceChildren(); $('nodes').replaceChildren(); $('mappings').replaceChildren();
    current.samples.forEach((sample,i) => {
      const swatch = document.createElement('div'), chip = document.createElement('div');
      swatch.className = 'swatch'; chip.className = 'chip'; swatch.style.setProperty('--accent', sample.hex);
      swatch.append(chip, document.createTextNode(`${i+1} · ${sample.hex}`));
      swatch.title = `Hue ${sample.hue.toFixed(2)}°, chroma ${sample.chroma.toFixed(4)}`;
      $('swatches').append(swatch);
      $('nodes').append(node(sample.hex, `${i+1} hop${i===0 ? '' : 's'}`, sample.gamutReduced ? `C reduced to ${sample.chroma.toFixed(3)}` : `Hue ${sample.hue.toFixed(1)}°`));
    });
    $('nodes').append(node('#d3d3d3', 'Manifesto', 'Neutral in distance / type modes', true));
    for (const [kind,index] of Object.entries(current.mappings)) {
      const item = document.createElement('div'); item.className = 'mapping'; item.style.setProperty('--accent', current.colors[index]);
      item.textContent = `${mappingNames[kind]} · color ${index+1} · ${current.colors[index]}`; $('mappings').append(item);
    }
    const reduced = current.gamutReducedIndices;
    $('message').textContent = reduced.length ? `Chroma reduced to fit sRGB for colors ${reduced.map(i=>i+1).join(', ')}. Hue and lightness retained before hex rounding.`
      : 'All requested base colors fit sRGB.';
    exportResult();
  }
  $('parameters').addEventListener('submit', event => event.preventDefault());
  $('parameters').addEventListener('input', event => {
    if (event.target.dataset.for) $(event.target.dataset.for).value = event.target.value;
    render();
  });
  $('theme').addEventListener('change', () => $('preview').classList.toggle('light', $('theme').value === 'light'));
  $('format').addEventListener('change', exportResult);
  $('reset').addEventListener('click', () => {
    for (const key of keys) $(key).value = api.DEFAULTS[key];
    render();
  });
  $('copy').addEventListener('click', async () => {
    if (!valid) return;
    try {
      if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText($('result').value);
      $('message').textContent = 'Copied. Paste this result back to the assistant.';
    } catch {
      $('result').focus(); $('result').select();
      $('message').textContent = 'Automatic clipboard access is unavailable. Result selected: press Ctrl+C (Cmd+C on Mac), then paste it back.';
    }
  });
  render();
})();
