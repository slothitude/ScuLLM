# Gemma 4 main-track submission bundle (B1 skeleton)

Declarative agent tree for the swegemma harness. Layout follows HARNESS_README.md section 2.2. All field names in the YAML files are taken from HARNESS_README.md section 2.3 and verified against the adk_submission 0.2.13 wheel schema (SandboxedLlmAgentConfig, AgentToolEntry, SubAgentRef, ThinkingConfig).

## Bundle map

- agent.yaml — root LlmAgent `crow`. Declares the single base model, the tool set, the analyzer wiring, the repo-navigation skill, and generation config. Instruction loaded from prompts/system.md via !include.
- sub_agents/code_analyzer.yaml — read-only LlmAgent `code_analyzer`, wired twice: as an AgentTool on the root with skip_summarization: true (gotcha 4), and as a peer sub_agents entry per work order B1. Both references compile independently; the peer entry is droppable at M2 if traces show the root transferring into the read-only analyzer instead of calling its tool.
- eval_config.yaml — per-task budgets under the evaluation key.
- prompts/system.md — the agent's operating laws: verify before submit, incremental edits, scratch in /tmp, budget-awareness, submit last, protected test configs.
- skills/repo-navigation/SKILL.md — the search_similar_code, get_code_neighbors, get_code_subgraph, then narrow read_file loop.

## Single base model (section 3.2)

Every agent in this tree declares exactly one base model alias:

    gemma-4-e2b-it-qat-w4a16-ct

agent.yaml and sub_agents/code_analyzer.yaml both name it, so the declared-model set has exactly one unique value and passes validate_single_declared_model. The alias is one of the four ALLOWED_MODEL_NAMES.

## Tool budget

The root declares all nine harness tools (section 6): the seven budget-counting ones (run_command, read_file, edit_file, write_file, get_code_neighbors, search_similar_code, get_code_subgraph) plus the two free lifecycle tools (submit_patch and get_status, both count_tool_call=False per section 6.1). submit_patch is required by gotcha 5 and get_status backs the budget-awareness law in the system prompt; undeclared tools are never advertised (section 5.2), so both must be listed. The analyzer declares only read_file plus the three graph tools.

## Budgets (eval_config.yaml)

timeout_seconds 300, max_tool_calls 100, max_time_minutes 60, max_turns 500 — the harness defaults from section 7.1. The sample submission's 10 / 1 / 50 numbers are the trap; do not copy them.

## M2-optional: adapters

The adapters/ directory is optional in the layout (section 2.2). This skeleton reserves two adapter slots but leaves the adapter keys commented out until M2 ships the weights:

- agent.yaml: crow_lora
- sub_agents/code_analyzer.yaml: analyzer_lora

Reason for commenting: the harness notebook's structural check asserts that no yaml declares an adapter key while no adapters directory exists, and section 3.4 requires adapters to live under adapters/<adapter_name>/ containing adapter_config.json plus adapter_model.safetensors. At M2, add the two adapter directories, uncomment both adapter lines, and relax the notebook check. Adapter names must match the section 3.4 name pattern and the total unpacked bundle stays under 3 GiB.

## Validate (notebook compile path)

Notebook: eval/kernels/gemma-4-developer-agent-baseline-harness.ipynb. Structural pre-checks (cell 4): exactly one root config, no symlinks, only .yaml .yml .md .txt .py .json .safetensors files, total under 3 GiB, one declared model inside ALLOWED_MODELS, and markdown placeholders limited to problem_description and hints.

Harness validate plus compile (cell 6), where BUNDLE is the unpacked submission directory and tools maps the nine tool names to their sandbox functions:

    from adk_submission import ModelRegistry, compile_submission, validate_directory
    from adk_submission.discovery import discover_declared_models
    from swegemma.config import build_submission_limits

    limits, constraints = build_submission_limits()
    validate_directory(BUNDLE, limits)
    declared = discover_declared_models(BUNDLE, normalize_fn=norm_model)
    compiled_agent = compile_submission(BUNDLE, tools, models, limits=limits, generation_constraints=constraints)

norm_model lower-cases and strips provider prefixes (openai, google, hosted_vllm, custom). models registers the base alias against the local vLLM endpoint as an openai-prefixed LiteLlm handle (cell 6 wires it to a throwaway api_base for the offline compile check).

## Open flags for M2

1. SKILL.md frontmatter (name, description) is not specified in HARNESS_README.md; it is verified empirically against the installed google-adk 1.36.1 Frontmatter schema instead: skill name must equal the skill directory name and be lowercase kebab-case (snake_case is an experimental, default-off feature flag), so the directory is repo-navigation rather than the work order's repo_navigation spelling.
2. The dual analyzer wiring (AgentTool plus peer sub_agent) compiles cleanly but gives the root a transfer path into a read-only agent; the system prompt forbids it, but drop the sub_agents entry if M2 traces show it happening.
3. Adapter keys stay commented until adapters/ ships at M2.
