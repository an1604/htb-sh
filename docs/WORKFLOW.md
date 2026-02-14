# Example Workflow

This document walks through typical usage of the HTB Command Automation Tool during a pentesting session.

## Scenario: Setting Up for a New Target

### 1. Browse available tools

```bash
htb tool list
htb tool list --category scanning
htb tool categories
```

### 2. Add a new tool (if needed)

```bash
# Interactive
htb tool add

# Quick
htb tool add gobuster --description "Directory bruster" --category web
```

### 3. Add commands for your workflow

```bash
# Fully interactive (recommended)
htb add

# Add to specific tool (skip tool selection)
htb add nmap

# Quick add with all flags
htb add nmap --id aggressive-scan --name "Aggressive Scan" \
  --cmd "nmap -A {target}" --explain "OS detection, version detection" \
  --param "target:Target IP:required" --tag scanning,aggressive
```

### 4. Find commands when needed

```bash
# List all
htb list

# By tool
htb list nmap
htb list nmap --detailed

# By category
htb list --category scanning

# Search
htb search "version detection"
htb search --tag enumeration
htb search --tool nmap --tag scanning
```

### 5. View command details

```bash
htb show nmap:basic-scan
htb show nmap:basic-scan --highlight
```

### 6. Generate and use commands

```bash
# Interactive (prompts for params)
htb gen nmap:basic-scan

# With parameters (copies to clipboard)
htb gen nmap:basic-scan -p target=10.10.10.5

# Without copying
htb gen nmap:basic-scan -p target=10.10.10.5 --no-copy

# Print only (for piping)
htb gen nmap:basic-scan -p target=10.10.10.5 --print-only
```

### 7. Edit or delete commands

```bash
# Interactive edit
htb edit nmap:basic-scan

# Quick edit
htb edit nmap:basic-scan --explanation "Updated explanation"

# Delete (with confirmation)
htb delete nmap:basic-scan

# Force delete
htb delete nmap:basic-scan --force
```

## Typical Session Flow

1. **Before engagement:** Add tools and commands you expect to use.
2. **During engagement:** Search, show, and gen commands as needed.
3. **After engagement:** Edit or delete commands to refine your database for next time.
