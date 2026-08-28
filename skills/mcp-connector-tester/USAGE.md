# MCP Connector Tester Skill - Usage Guide

## What This Skill Does

The **MCP Connector Tester** skill provides a systematic workflow for testing, exploring, and documenting any MCP (Model Context Protocol) connector. It was created based on the process used to test the Supabase MCP connector.

## When to Use

Use this skill when you want to:
- **Test a new MCP connector** to verify it works
- **Explore capabilities** of an MCP connector you haven't used before
- **Create documentation** for an MCP connector
- **Troubleshoot authentication** issues with an MCP connector
- **Demonstrate features** to others
- **Generate comprehensive guides** for connector setup and usage

## What It Provides

### 1. Systematic Testing Workflow

The skill guides you through a 4-phase testing process:

1. **Explore Capabilities** - List and categorize all available tools
2. **Test Authentication** - Verify credentials and configuration
3. **Demonstrate Features** - Run representative operations safely
4. **Create Documentation** - Generate comprehensive guides

### 2. Documentation Templates

Three ready-to-use templates for consistent documentation:

- **connector_overview.md** - Complete reference guide structure
- **authentication_guide.md** - Step-by-step credential setup
- **troubleshooting_guide.md** - Common issues and solutions

### 3. Best Practices

Built-in guidance for:
- Safe testing (avoiding destructive operations)
- Authentication troubleshooting
- Documentation structure
- Security considerations

## Example Usage

### Testing a New Connector

**User**: "Help me test the Airtable MCP connector and show me how to use it"

**Manus with this skill will**:
1. List all available Airtable tools
2. Check authentication status
3. Guide you through credential setup if needed
4. Test basic operations (list bases, list tables)
5. Create comprehensive documentation showing:
   - All capabilities organized by category
   - Authentication setup instructions
   - Example operations with real results
   - Troubleshooting guide

### Documenting an Existing Connector

**User**: "Create documentation for the Hugging Face connector"

**Manus with this skill will**:
1. Explore all available tools
2. Categorize by functionality
3. Generate complete documentation using templates
4. Include authentication setup
5. Provide example operations
6. Add troubleshooting section

### Troubleshooting Authentication

**User**: "My Supabase connector isn't working, help me fix it"

**Manus with this skill will**:
1. Check authentication status
2. Identify the credential type needed
3. Guide you to the correct location to get credentials
4. Help configure in Manus
5. Verify the connection works
6. Provide troubleshooting steps if issues persist

## What Makes This Skill Valuable

### Based on Real Experience

This skill was created by analyzing the actual process used to test the Supabase connector, capturing:
- The systematic exploration approach
- Authentication troubleshooting steps
- Documentation structure that worked well
- Common pitfalls and how to avoid them

### Reusable Templates

The documentation templates provide consistent structure across all connectors while being flexible enough to customize for each connector's unique features.

### Safety-First Approach

Built-in guidance to:
- Test read-only operations first
- Avoid destructive operations
- Warn before operations that incur costs
- Respect user data and privacy

### Comprehensive Output

Generates multiple documentation artifacts:
- Capabilities overview
- Authentication guide
- Example demonstrations
- Troubleshooting guide
- Complete reference combining all above

## Skill Structure

```
mcp-connector-tester/
├── SKILL.md                              # Main skill instructions
└── templates/                            # Documentation templates
    ├── connector_overview.md             # Complete reference structure
    ├── authentication_guide.md           # Credential setup guide
    └── troubleshooting_guide.md          # Common issues and solutions
```

## How It Works

When you ask to test or document an MCP connector, Manus will:

1. **Read this skill** to understand the systematic testing workflow
2. **Follow the 4-phase process** outlined in SKILL.md
3. **Use the templates** to create consistent documentation
4. **Apply best practices** for safety and thoroughness
5. **Deliver comprehensive documentation** as Markdown files

## Benefits

- **Saves time** - No need to figure out testing approach each time
- **Consistent quality** - Same thorough process for every connector
- **Complete documentation** - Nothing important gets missed
- **Safe testing** - Built-in guardrails against destructive operations
- **Reusable** - Works for any MCP connector

## Future Enhancements

Potential improvements:
- Add scripts for automated testing
- Include comparison templates for evaluating multiple connectors
- Add visualization tools for capability mapping
- Create connector compatibility checklist

## Credits

Created based on the Supabase MCP connector testing session, capturing the systematic approach that proved effective for exploring, testing, and documenting MCP connectors.
