---
id: e5c7bf6a-99d2-4173-94d4-a73cb796f470
type: requirement
parents:
- 6f69c873-0ab4-450b-b306-791102affe95
- 65f28474-18be-46f8-89f6-b9ce30a0ec96
- 2b8a4bbc-d15a-4347-90b4-691abdeefaef
managed_hash: 66dc95d093e780c8d42c04f8e720c0e20cf281c0fc49cd54e52c492312409c54
---
# Host the canvas in a retained Activity Bar webview view

Contribute a SpecSpec Activity Bar container with a WebviewView and the minimal dachshund icon. Use the supported custom-container placement and respect VS Code's saved user order. Inspection of its contribution API and a real launch show that extension containers are assigned after built-ins: a manifest order field cannot position the icon between Run/Debug and Extensions. Do not use private workbench APIs or rewrite user layout to force ordering; document dragging the dachshund below Run/Debug. This corrects the initial order-4 proposal based on platform evidence. Open Graph focuses the view; offer explicit project selection (including nested graphs) and revision comparison. Retain the view when hidden and keep state project-scoped across reload/switches. Narrowing the sidebar clips the world, not resizes/reflows cards. No separate editor-tab rendering fork is introduced.

Origin: the user's cross-platform/sidebar/branding request in this conversation. Technical choices remain revisable.
