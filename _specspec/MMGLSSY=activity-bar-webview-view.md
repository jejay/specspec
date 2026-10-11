---
id: MMGLSSY=
type: requirement
parents:
- HV8tZho=
- YOPhqYc=
- bOXyw00=
retired: true
---
# Host the canvas in a retained Activity Bar webview view

Contribute a SpecSpec Activity Bar container with a WebviewView and the minimal dachshund icon. Use the supported custom-container placement and respect VS Code's saved user order. Inspection of its contribution API and a real launch show that extension containers are assigned after built-ins: a manifest order field cannot position the icon between Run/Debug and Extensions. Do not use private workbench APIs or rewrite user layout to force ordering; document dragging the dachshund below Run/Debug. This corrects the initial order-4 proposal based on platform evidence. Open Graph focuses the view; offer explicit project selection (including nested graphs) and revision comparison. Retain the view when hidden and keep state project-scoped across reload/switches. Narrowing the sidebar clips the world, not resizes/reflows cards. No separate editor-tab rendering fork is introduced.

Origin: the user's cross-platform/sidebar/branding request in this conversation. Technical choices remain revisable.
