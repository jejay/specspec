/* Sandboxed preload: no generic IPC, FS, subprocess, or Electron object exposure. */
const { contextBridge, ipcRenderer } = require('electron');
if (process.isMainFrame) {
  const initial = ipcRenderer.sendSync('specspec:initial');
  let state = initial.state;
  contextBridge.exposeInMainWorld('SpecSpecNative', Object.freeze({
    getState: () => state,
    setState: value => { state = value; ipcRenderer.send('specspec:state', { generation: initial.generation, value }); },
    postMessage: value => ipcRenderer.send('specspec:message', { generation: initial.generation, value }),
    onMessage: listener => {
      const handler = (_event, value) => listener(value);
      ipcRenderer.on('specspec:host', handler); return () => ipcRenderer.removeListener('specspec:host', handler);
    },
    revisionResult: value => ipcRenderer.send('specspec:revision-result', { generation: initial.generation, value }),
  }));
}
