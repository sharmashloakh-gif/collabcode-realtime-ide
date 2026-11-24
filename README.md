# CollabCode — Live Collaborative Code Execution Sandbox

A browser-based collaborative coding environment built with **Django**, **JavaScript**, **Bootstrap**, and **Python AST sandboxing** for technical interviews and pair programming.

## Highlights
- AST-level static security scanner blocks dangerous imports (`os`, `subprocess`, `sys`) before execution.
- Resource-bounded execution with timeout guards and stdout/stderr capture.
- Clean split-pane Bootstrap dark IDE interface with live diff sync.
