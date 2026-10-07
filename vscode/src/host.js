/* The only renderer-facing VS Code adapter. State is isolated by project root. */
(() => {
  const api = acquireVsCodeApi();
  const scope = document.querySelector('meta[name="specspec-project"]')?.content || '';
  const stored = api.getState() || {};
  // Preserve pre-extraction drafts in their original graph; never share across roots.
  const projects = stored.projects || { [scope]: stored };
  window.SpecSpecHost = Object.freeze({
    getState: () => projects[scope],
    setState: value => { projects[scope] = value; api.setState({ projects }); },
    postMessage: value => api.postMessage(value),
    onMessage: listener => {
      const handler = event => listener(event.data);
      window.addEventListener('message', handler);
      return () => window.removeEventListener('message', handler);
    },
  });
})();
