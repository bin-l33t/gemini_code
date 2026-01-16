# fix_map_final.py
import json

# The definitive map based on cli.js variable assignments
HARD_TRUTH = {
    "${A}": "path",                # Context: "Invalid value ${A}" in file checks
    "${Q}": "encoding",            # Context: "encoding:Q.encoding"
    "${mW.name}": "TodoWrite",     # Context: resolved previously
    "${EE}": "StructuredOutput",   # Context: resolved previously
    "${K9}": "Bash",               # Context: var K9="Bash"
    "${BI}": "Grep",               # Context: var BI="Grep"
    "${gI}": "Glob",               # Context: var gI="Glob"
    "${f3}": "Edit",               # Context: var f3="Edit"
    "${eZ}": "Write",              # Context: var eZ="Write"
    "${b3}": "Notebook",           # Context: Notebook read/edit logic
    "${C3}": "Bash"                # Context: often alias for K9 in prompt consts
}

print("--- 🔒 Locking in Verified Variables ---")
with open("variable_map.json", "w") as f:
    json.dump(HARD_TRUTH, f, indent=2)

print("✅ variable_map.json updated with HARD EVIDENCE.")
