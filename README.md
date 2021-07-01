# nimhello

Visual code setup for Nim and Nimble Projects

This setup allows for 4 Tasks:

1) Nim: Debug Build           Slow debug builds for single file
2) Nim: Fast Build            Fast release builds for single file
3) Nimble: Debug Build        Slow debug builds for nimble projects
4) Nimble: Fast Build         Fast release builds for nimble projects

When you press "Run and Debug" on Visual studio. You can use:

1) Nim Debugger: This will run the "Nim: Debug Build" task and run the debug build using LLDB
2) Nimble Debugger: This will run the "Nimble: Debugger" task and run the debug build using LLDB

The python script `.vscode/lldbnim.py` cleans up lldb output for nim.
