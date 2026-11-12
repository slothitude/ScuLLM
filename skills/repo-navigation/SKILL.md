---
name: repo-navigation
description: How to explore a repository with the code-intelligence graph tools before spending any read_file budget.
---

# Repo navigation loop

The repository ships pre-built call-graph and embedding indexes keyed by dotted symbol path, for example pkg.module.Class.method, Class.method, or func_name. Run the graph tools BEFORE reading files; each graph call is cheaper than a blind read.

1. Locate. Call search_similar_code with a symbol name taken from the problem statement, an error trace, or a test failure. It returns the top-k matching graph nodes with code snippets and similarity scores, turning a bare name into exact node paths.
2. Trace. Call get_code_neighbors on the node you care about to list its callers and callees. This tells you who consumes the symbol you must change and what breaks when a signature moves.
3. Bound. Call get_code_subgraph with the two or three nodes that matter to get the induced subgraph connecting them. That node set is your minimal read set.
4. Read narrowly. Only now call read_file, and only on files the subgraph named, using start_line and end_line slices. read_file caps at 150 lines and 10000 characters per call, so slice instead of reading whole files.

Rules of thumb:

- Pass dotted paths when you have them; short names fall back through exact, suffix, case-insensitive, then substring match.
- Filter get_code_neighbors with an edge_type such as calls when you only want call edges.
- Cap the fan-out: max_neighbors and k default to 50 and 10; lower them when you only need the direct ring.
- If the graph tools return nothing useful, fall back to git grep through run_command on the root agent, then re-enter this loop from the grep hit.
- This skill is read-only guidance. Edits belong to the parent agent's edit_file loop, not to exploration.
