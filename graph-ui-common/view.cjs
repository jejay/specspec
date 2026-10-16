/* Local webview shell. Project text is inserted only through DOM text/value APIs. */
function graphHtml(resource, cspSource, nonce, options = {}) {
  const attr = value => String(value).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
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
    <p id="sync-notice" role="status" hidden>Displayed graph is out of date. Fix the Markdown files and refresh; graph changes are disabled.</p>
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
    <main id="viewport" tabindex="0" aria-label="Specification node canvas" aria-describedby="canvas-help"><div id="graph">
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
    <section id="source-tools" hidden><h3>Source regions</h3><ul id="source-links"></ul>
    <p class="form-help">Links identify source snapshots, not proof of implementation. Click to resolve/preview. Strict reports internal edits; expanding includes them. Separate gaps and boundary insertions are excluded.</p>
    <label>Source path<input id="source-path" placeholder="src/example.py"></label>
    <label>Inclusive ranges<input id="source-ranges" placeholder="100:150, 300:500"></label>
    <label>Tracking<select id="source-mode"><option value="strict">Strict (specific)</option><option value="expanding">Expanding (broad)</option></select></label>
    <label><input type="checkbox" id="source-staged"> Capture staged code (otherwise HEAD). Staging remains manual.</label>
    <button type="button" id="capture-source">Append source reference to this form</button></section>
    <div class="actions"><button type="submit" id="save">Save node</button><button type="button" id="delete">Delete node &amp; descendants</button><button type="button" id="discard">Discard form edits</button></div></form>
    <section id="before-section" hidden><h3>Base revision text</h3><pre id="before"></pre></section></section></div>
    <dialog id="source-preview" aria-labelledby="source-preview-title"><h2 id="source-preview-title">Source preview</h2><p id="source-preview-status"></p><pre id="source-preview-code" tabindex="0"></pre><button id="close-source-preview" type="button">Close</button></dialog>
    <dialog id="annotation-compose" aria-labelledby="annotation-compose-title"><form id="annotation-compose-form"><h2 id="annotation-compose-title">Create spotlight from highlights</h2><label for="annotation-message">Message for the agent</label><textarea id="annotation-message" rows="4" maxlength="500" required></textarea><p id="annotation-compose-error" role="status"></p><button id="annotation-compose-cancel" type="button">Cancel</button><button id="annotation-compose-save" type="submit">Create spotlight</button></form></dialog>
    <footer>Click a node to explore and edit its neighborhood. Shift-click node chrome cycles highlight colors; Ctrl/Command+Shift-click clears one. Spotlights exchanges immutable local owner/agent messages; save highlights with a message for the agent. Inset rings identify exact matching node versions. The red badge counts arrivals since the list was last opened. New spotlights never move the camera or interrupt editing. Fills: selected color mode. Git title/corner: A added, M modified, D deleted, R renamed. Default workspace compares to HEAD; deleted nodes remain visible as D until committed. Linked-source cues are not node M. Downstream counts include all depths, deduplicated per child; overlapping totals are not additive. Git staging remains manual.</footer>
    <script nonce="${nonce}" src="${resource('host.js')}"></script>
    <script nonce="${nonce}" src="${resource('vendor/graph-vendor.js')}"></script>
    <script nonce="${nonce}" src="${resource('graph-model.js')}"></script>
    <script nonce="${nonce}" src="${resource('graph-camera.js')}"></script>
    <script nonce="${nonce}" src="${resource('graph-annotations.js')}"></script>
    <script nonce="${nonce}" src="${resource('graph.js')}"></script></body></html>`;
}

module.exports = { graphHtml };
