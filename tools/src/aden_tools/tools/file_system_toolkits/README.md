# File System Toolkits

A collection of sandboxed file system tools for use in Hive agents. All operations are restricted to a per-session workspace directory to prevent path traversal attacks.

## No Credentials Required

These tools operate on the local filesystem within a sandboxed session directory. No API keys or external services are needed.

## Security Model

All paths are resolved through `get_secure_path()`, which:
- Restricts access to `~/.hive/workspaces/<workspace_id>/<session_id>/`
- Rejects any path that would escape the sandbox via `../` or symlinks

## Available Tools

### `list_dir`
List the contents of a directory within the session sandbox.

**Parameters:** `path`, `workspace_id`, `agent_id`, `session_id`

**Use when:** Exploring directory structure, discovering available files.

---

### `view_file`
Read the contents of a file within the sandbox.

**Parameters:** `path`, `workspace_id`, `agent_id`, `session_id`, `start_line` (optional), `end_line` (optional)

**Use when:** Reading configuration, source code, or data files.

---

### `write_to_file`
Write or overwrite a file in the sandbox.

**Parameters:** `path`, `content`, `workspace_id`, `agent_id`, `session_id`

**Use when:** Creating new files or saving agent output.

---

### `replace_file_content`
Replace specific text within a file (find-and-replace).

**Parameters:** `path`, `old_content`, `new_content`, `workspace_id`, `agent_id`, `session_id`

**Use when:** Making targeted edits to existing files.

---

### `apply_diff` / `apply_patch`
Apply a unified diff or patch to a file.

**Parameters:** `path`, `diff`/`patch`, `workspace_id`, `agent_id`, `session_id`

**Use when:** Applying structured code changes.

---

### `grep_search`
Search for a pattern in files within the sandbox.

**Parameters:** `pattern`, `path`, `workspace_id`, `agent_id`, `session_id`, `recursive` (default: true)

**Use when:** Finding occurrences of text across multiple files.

---

### `execute_command_tool`
Execute a shell command within the sandboxed workspace.

**Parameters:** `command`, `workspace_id`, `agent_id`, `session_id`

**Use when:** Running build scripts, tests, or other shell commands scoped to the workspace.

---

### `hashline` / `hashline_edit`
Content-addressed line tracking for precise file edits.

**Use when:** Making edits that need to be anchored to specific content rather than line numbers.

---

### `data_tools`
Structured data manipulation utilities (CSV, JSON, etc.).

**Use when:** Processing data files within the workspace.

## Example Agent Prompt

```
List the files in my project directory, then read the README,
search for any TODO comments, and write a summary to summary.txt.
```
