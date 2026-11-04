# Architecture

Read the existing implementation and callers before you add or move behavior.
Give each semantic contract, state, and validation rule one owner.
Use abstractions that serve current callers.
Do not add speculative layers, extension points, or empty modules.

Group modules by responsibility.
A utility module must not import the business module that uses it.
Keep dependencies consistent with the responsibility boundary.
Repair the behavior at its owner instead of adding a caller workaround.
