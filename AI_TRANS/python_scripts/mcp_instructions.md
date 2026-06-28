# Excel Translator MCP Server Instructions

## Overview
We have built an MCP (Model Context Protocol) Server for you named **ExcelTranslator**. This server provides Antigravity with robust, reusable tools to perform large-scale targeted modifications, extraction, and character analysis on your translation `.xlsx` files without writing ad-hoc python scripts every time.

## Provided Tools
Once the MCP is connected, Antigravity will automatically be able to use the following tools:
1. **`get_unique_names(file_path)`**: Quickly lists all character names found in a given file.
2. **`extract_character_lines(file_path, character_name, keyword)`**: Pulls up specific dialogues from a specific character, matching optional keywords or regex. Good for context gathering.
3. **`apply_text_replacement(file_path, character_name, target, replacement, include_nan)`**: Instantly replaces a specific phrase for a specific character across the whole file.
4. **`apply_regex_replacement(file_path, character_name, pattern, replacement, include_nan)`**: Advanced regex-based replacements for complex pronoun/grammar swaps.

## How to add this MCP to Antigravity
To register this MCP server so I (Antigravity) can use these tools persistently:

1. Open your Antigravity Settings or Configuration file (typically located where Antigravity manages MCP configurations, e.g., via the Antigravity UI under "MCP Servers").
2. Add a new **`stdio`** transport MCP server.
3. Use the following configuration:
   - **Name:** `ExcelTranslator`
   - **Command:** `python`
   - **Args:** `["c:\\Users\\tivac\\Downloads\\Compressed\\drive-download-20251110T020358Z-1-001\\AI_TRANS\\python_scripts\\mcp_server.py"]`

*(Alternatively, if Antigravity is configured via `mcp.json`, add this dictionary to your `mcpServers` object):*
```json
"ExcelTranslator": {
  "command": "python",
  "args": ["c:\\Users\\tivac\\Downloads\\Compressed\\drive-download-20251110T020358Z-1-001\\AI_TRANS\\python_scripts\\mcp_server.py"]
}
```

Once connected, I will be fully equipped to handle character voice, tone, and pronoun re-writing as a built-in feature!
