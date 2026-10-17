/* Local webview shell. Project text is inserted only through DOM text/value APIs. */
function graphHtml(resource, cspSource, nonce, options = {}) {
  const attr = value => String(value).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
  const icon = paths => `<svg class="camera-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">${paths}</svg>`;
  const corners = '<path d="M8 3H3v5m13-5h5v5M3 16v5h5m13-5v5h-5"/>';
  return `<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
    <meta name="specspec-project" content="${attr(options.scope || '')}">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${cspSource} 'unsafe-inline'; img-src ${cspSource}; script-src 'nonce-${nonce}';">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="${resource('graph.css')}" rel="stylesheet"><link href="${resource('host.css')}" rel="stylesheet"><title>SpecSpec Graph</title></head>
    <body><header class="toolbar"><span class="brand-icon" aria-hidden="true" style="mask-image:url('${attr(resource('specspec.svg'))}')"></span><strong>SpecSpec</strong>
    <button id="project" title="Choose a local SpecSpec project">Open project</button>
    <button id="back" hidden>← Total graph</button><button id="refresh">Refresh</button>
    <button id="compare">Compare revisions</button><button id="workspace">HEAD / workspace</button>
    <button id="new">+ New node</button><button id="resume" hidden>Resume draft</button>
    <button id="annotations-toggle" aria-haspopup="menu" aria-expanded="false" aria-controls="annotations-panel" aria-label="Spotlights"><span>Spotlights</span><span id="spotlights-count" class="spotlights-count" aria-hidden="true" hidden></span></button>
    <label class="color-control" for="color-mode">Color by <select id="color-mode">
    <option value="distance">Min. Distance to Manifesto</option><option value="max-distance">Max. Distance to Manifesto</option><option value="absolute-influence">Absolute influence</option><option value="relative-influence">Relative influence</option><option value="log-absolute-influence">Log Absolute Influence</option><option value="log-relative-influence">Log Relative Influence</option><option value="type">Node type</option><option value="git-revision">Git/Revision Status</option></select></label>
    <span id="revision"></span></header>
    <div id="legend" aria-label="Node color legend"></div>
    <p id="message" role="status">Loading specification graph…</p>
    <p id="annotation-warning" role="status" hidden></p>
    <p id="sync-notice" role="status" hidden>Last valid graph · Repair Markdown and refresh to resume editing.</p>
    <details id="linked-sources" hidden><summary id="source-summary"></summary><ul id="source-files"></ul></details>
    <p id="annotation-live" class="sr-only" role="status" aria-live="polite" aria-atomic="true"></p>
    <div class="canvas-shell">
    <aside id="annotations-panel" hidden role="menu" aria-labelledby="annotations-heading">
      <h2 id="annotations-heading" class="sr-only">Spotlights</h2>
      <p id="annotation-error" role="status" hidden></p>
      <p id="annotation-list-summary" class="form-help"></p>
      <div id="annotation-list" role="group" aria-label="Retained spotlights"></div>
      <div class="annotation-panel-footer" role="group" aria-label="Spotlight actions"><button id="annotation-create" role="menuitem">Create spotlight from highlights…</button><button id="annotation-clear" role="menuitem">Clear highlight</button><button id="annotation-flush" role="menuitem">Flush local spotlights…</button></div>
    </aside>
    <main id="viewport" tabindex="0" aria-label="Specification node canvas"><div id="graph">
    <svg id="edges" aria-hidden="true"></svg><div id="cards"></div></div></main>
    <nav class="camera-controls" aria-label="Canvas navigation">
    <div class="zoom-controls" role="group" aria-label="Zoom">
    <button id="zoom-out" title="Zoom out (-)" aria-label="Zoom out">${icon('<path d="M5 12h14"/>')}</button>
    <button id="zoom-reset" title="Actual size (1)" aria-label="Actual size"><span id="zoom-level">100%</span></button>
    <button id="zoom-in" title="Zoom in (+)" aria-label="Zoom in">${icon('<path d="M5 12h14M12 5v14"/>')}</button></div>
    <span class="camera-divider" aria-hidden="true"></span>
    <div class="framing-controls" role="group" aria-label="Framing">
    <button id="frame-all" title="Frame graph (Home / F)" aria-label="Frame graph">${icon(corners + '<path d="m8 9 4 6 5-7"/><circle cx="8" cy="9" r="1.5"/><circle cx="12" cy="15" r="1.5"/><circle cx="17" cy="8" r="1.5"/>')}</button>
    <button id="frame-node" hidden title="Frame node" aria-label="Frame node">${icon(corners + '<rect x="8" y="8" width="8" height="8" rx="1.5"/>')}</button>
    <button id="frame-area" title="Frame rectangle" aria-label="Frame rectangle" aria-pressed="false">${icon('<rect x="5" y="5" width="14" height="14" rx="1" stroke-dasharray="3 3"/><path d="M2 5h6M5 2v6"/>')}</button></div></nav></div>
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
    <section id="source-tools" hidden><h3>Source regions</h3><ul id="source-links"></ul>
    <p class="form-help">Strict: fixed regions · Expanding: growing regions</p>
    <label>Source path<input id="source-path" placeholder="src/example.py"></label>
    <label>Inclusive ranges<input id="source-ranges" placeholder="100:150, 300:500"></label>
    <label>Tracking<select id="source-mode"><option value="strict">Strict (specific)</option><option value="expanding">Expanding (broad)</option></select></label>
    <label><input type="checkbox" id="source-staged"> Capture staged code · Default: HEAD</label>
    <button type="button" id="capture-source">Append source reference to this form</button></section>
    <div class="actions"><button type="submit" id="save">Save node</button><button type="button" id="delete">Delete node &amp; descendants</button><button type="button" id="discard">Discard form edits</button></div></form>
    <section id="before-section" hidden><h3>Base revision text</h3><pre id="before"></pre></section></section></div>
    <dialog id="source-preview" aria-labelledby="source-preview-title"><h2 id="source-preview-title">Source preview</h2><p id="source-preview-status"></p><pre id="source-preview-code" tabindex="0"></pre><button id="close-source-preview" type="button">Close</button></dialog>
    <dialog id="annotation-compose" aria-labelledby="annotation-compose-title"><form id="annotation-compose-form"><h2 id="annotation-compose-title">Create spotlight from highlights</h2><label for="annotation-message">Message for the agent</label><textarea id="annotation-message" rows="4" maxlength="500" required></textarea><p id="annotation-compose-error" role="status"></p><button id="annotation-compose-cancel" type="button">Cancel</button><button id="annotation-compose-save" type="submit">Create spotlight</button></form></dialog>
    <script nonce="${nonce}" src="${resource('host.js')}"></script>
    <script nonce="${nonce}" src="${resource('vendor/graph-vendor.js')}"></script>
    <script nonce="${nonce}" src="${resource('graph-model.js')}"></script>
    <script nonce="${nonce}" src="${resource('graph-camera.js')}"></script>
    <script nonce="${nonce}" src="${resource('graph-annotations.js')}"></script>
    <script nonce="${nonce}" src="${resource('graph.js')}"></script></body></html>`;
}

module.exports = { graphHtml };
