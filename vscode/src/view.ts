/* Local webview shell. Project text is inserted only through DOM text/value APIs. */
export function graphHtml(resource: (name: string) => string, cspSource: string, nonce: string): string {
  return `<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}';">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="${resource('graph.css')}" rel="stylesheet"><title>SpecSpec Graph</title></head>
    <body><header class="toolbar"><strong>SpecSpec</strong>
    <button id="back" hidden>← Total graph</button><button id="refresh">Refresh</button>
    <button id="compare">Compare revisions</button><button id="workspace">HEAD / workspace</button>
    <button id="new">+ New node</button><button id="resume" hidden>Resume draft</button>
    <label class="color-control" for="color-mode">Color by <select id="color-mode">
    <option value="status">Status</option><option value="distance">Distance to manifesto</option></select></label>
    <span id="revision"></span></header>
    <div id="legend" aria-label="Node color legend"></div>
    <p id="message" role="status">Loading specification graph…</p>
    <details id="linked-sources" hidden><summary id="source-summary"></summary><ul id="source-files"></ul></details>
    <div class="canvas-shell"><main id="viewport" tabindex="0" aria-label="Specification node canvas" aria-describedby="canvas-help"><div id="graph">
    <svg id="edges" aria-hidden="true"></svg><div id="cards"></div></div></main>
    <nav class="camera-controls" aria-label="Canvas navigation">
    <button id="zoom-out" title="Zoom out (-)" aria-label="Zoom out">−</button>
    <button id="zoom-reset" title="Actual size (1)"><span id="zoom-level">100%</span></button>
    <button id="zoom-in" title="Zoom in (+)" aria-label="Zoom in">+</button>
    <button id="frame-all" title="Frame the visible graph (Home / F)">Frame graph</button>
    <button id="frame-node" hidden title="Frame the selected node">Frame node</button></nav>
    <p id="canvas-help" class="canvas-help">Middle-drag or drag the background to pan · Wheel / pinch to zoom · Home to frame · Arrow keys to pan</p></div>
    <div id="detail-parking" hidden><section id="node-details" class="node-settings">
    <h2 id="title">Select a node</h2><p id="identity"></p><p id="focus-context" class="form-help"></p><form id="editor" hidden>
    <label id="type-label">Type<select id="node-type"><option value="requirement">Requirement</option><option value="implementation">Implementation</option></select></label>
    <label id="slug-label">Filename summary<input id="slug" maxlength="120"></label>
    <label>Binding Markdown<textarea id="body" rows="14" spellcheck="false"></textarea></label>
    <fieldset id="parents-fieldset"><legend>Parents</legend>
    <p id="parents-summary" class="form-help" role="status"></p><ul id="parent-links"></ul>
    <div id="parent-add-controls"><label for="parent-candidate">Add a parent</label>
    <div class="parent-add"><select id="parent-candidate" aria-label="Available parent nodes"></select>
    <button id="add-parent" type="button">Add parent</button></div></div></fieldset>
    <label id="sources-label">Source references (JSON)<textarea id="sources" rows="4" spellcheck="false"></textarea></label>
    <div class="actions"><button type="submit" id="save">Save proposal</button><button type="button" id="accept">Accept</button><button type="button" id="retire">Retire</button><button type="button" id="discard">Discard form edits</button></div></form>
    <section id="before-section" hidden><h3>Base revision text</h3><pre id="before"></pre></section></section></div>
    <footer>Click a node to explore and edit its neighborhood. Fills: selected color mode. Git badges/strokes: added, removed, changed, renamed. Downstream counts include all depths, deduplicated per child; overlapping totals are not additive. Git staging remains manual.</footer>
    <script nonce="${nonce}" src="${resource('vendor/graph-vendor.js')}"></script>
    <script nonce="${nonce}" src="${resource('graph-model.js')}"></script>
    <script nonce="${nonce}" src="${resource('graph-camera.js')}"></script>
    <script nonce="${nonce}" src="${resource('graph.js')}"></script></body></html>`;
}
