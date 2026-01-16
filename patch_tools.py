import json

# Mapping schemas to their likely internal names based on Anthropic's typical naming
NAME_MAP = {
    "javascript_exec": "browser_evaluate",
    "left_click": "computer",  # The general computer use tool
    "start_recording": "record_session",
    "createIfEmpty": "ensure_tab_group",
    "onlyErrors": "get_console_logs",
    "urlPattern": "get_network_activity"
}

def patch():
    with open("healed_tools.json", "r") as f:
        tools = json.load(f)

    patched_count = 0
    
    # Handle the nested list structure seen in your logs
    flat_tools = []
    for item in tools:
        if isinstance(item, list):
            flat_tools.extend(item)
        else:
            flat_tools.append(item)

    for tool in flat_tools:
        # 1. Patch by 'action' property enum or description
        props = tool.get("inputSchema", {}).get("properties", {}) or tool.get("properties", {})
        
        if "name" not in tool or tool["name"] == "unknown_tool":
            # Heuristic 1: Check 'action' enums
            if "action" in props:
                action_prop = props["action"]
                if "enum" in action_prop:
                    if "left_click" in action_prop["enum"]:
                        tool["name"] = "computer"
                        patched_count += 1
                    elif "start_recording" in action_prop["enum"]:
                        tool["name"] = "record_session"
                        patched_count += 1
                elif "description" in action_prop and "javascript_exec" in action_prop["description"]:
                     tool["name"] = "browser_evaluate"
                     patched_count += 1
            
            # Heuristic 2: Unique property signatures
            elif "createIfEmpty" in props:
                tool["name"] = "ensure_tab_group"
                patched_count += 1
            elif "onlyErrors" in props and "tabId" in props:
                tool["name"] = "get_console_logs"
                patched_count += 1
            elif "urlPattern" in props and "tabId" in props:
                tool["name"] = "get_network_activity"
                patched_count += 1

    with open("gemini_browser_tools.json", "w") as f:
        json.dump(flat_tools, f, indent=2)
    
    print(f"✅ Patched {patched_count} tools. Saved to gemini_browser_tools.json")

if __name__ == "__main__":
    patch()
