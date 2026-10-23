/* Template has one shared source; this wrapper preserves the typed host boundary. */
const shared: { graphHtml: typeof graphHtml } = require('./common/view.cjs');
export function graphHtml(resource: (name: string) => string, cspSource: string, nonce: string,
  options: { scope?: string; showProject?: boolean } = {}): string {
  return shared.graphHtml(resource, cspSource, nonce, options);
}
