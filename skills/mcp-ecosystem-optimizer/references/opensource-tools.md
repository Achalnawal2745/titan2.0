# Open-Source Tools for MCP Management

This reference catalogs battle-tested open-source tools for managing, monitoring, and expanding MCP ecosystems.

## Management Dashboards

### MCP Dashboard (bryankthompson/mcp-dashboard)

**GitHub:** https://github.com/bryankthompson/mcp-dashboard

**Description:** A comprehensive web-based management interface for multiple MCP servers, built on the foundation of the official MCP Inspector.

**Tech Stack:** React 18, TypeScript, Tailwind CSS, Express backend

**Key Features:**
- Multi-server management with simultaneous connections
- Real-time monitoring via Server-Sent Events (SSE)
- Support for STDIO, SSE, and Streamable HTTP transports
- Server cards displaying transport type, tool count, connection details, and status
- In-place configuration editing without reconnection
- Tool execution with form-based parameter input
- Resource explorer with JSON visualization
- Dark mode support
- Built-in authentication with session tokens

**Installation:**
```bash
npx @bryan-thompson/dashboard
```

**Configuration:**
```json
{
  "CLIENT_PORT": 6286,
  "SERVER_PORT": 6287,
  "HOST": "localhost"
}
```

**Use Cases:**
- Centralized dashboard for all MCP servers
- Real-time status monitoring
- Quick server configuration changes
- Tool testing and debugging

**Quality Indicators:** New project (fork of official MCP Inspector), MIT License, active development

---

## Configuration Management

### mcp-serverman (benhaotang/mcp-serverman)

**GitHub:** https://github.com/benhaotang/mcp-serverman

**Description:** A command-line tool for managing MCP server configurations with version control, profiles, and multi-client support.

**Tech Stack:** Python CLI

**Key Features:**
- Version control for server configurations (like Git for MCP configs)
- Profile management for different environments (dev, staging, production)
- Multi-client support (Claude, Cline, MCP-Bridge)
- Enable/disable servers without deletion
- Companion MCP server for AI-driven configuration management
- Backup and restore functionality

**Installation:**
```bash
pip install mcp-serverman
```

**Common Commands:**
```bash
# Initialize
mcp-serverman client init

# List servers
mcp-serverman list --enabled

# Enable/disable
mcp-serverman enable <server_name>
mcp-serverman disable <server_name>

# Version control
mcp-serverman save <server_name> --comment "Added new tools"
mcp-serverman change <server_name> --version <version>

# Profiles
mcp-serverman preset save production
mcp-serverman preset load development

# Multi-client
mcp-serverman client add default --name "Default" --path "/path/to/config.json" --default

# Companion server
mcp-serverman companion
```

**Use Cases:**
- Version-controlled MCP configurations
- Environment-specific profiles (dev, staging, prod)
- Rollback to previous configurations
- AI-driven configuration management

**Quality Indicators:** 10 stars, 4 releases, MIT License, active development

---

## Monitoring & Observability

### Supabase Grafana (supabase/supabase-grafana)

**GitHub:** https://github.com/supabase/supabase-grafana

**Description:** Official Supabase observability stack using Prometheus and Grafana for comprehensive database monitoring.

**Tech Stack:** Prometheus, Grafana, Docker Compose

**Key Features:**
- 200+ Postgres performance and health metrics
- 1-minute granularity for high-resolution monitoring
- Prometheus-compatible Metrics API
- Pre-built dashboards for common use cases
- Custom dashboard creation
- Alert configuration

**Installation:**
```bash
git clone https://github.com/supabase/supabase-grafana.git
cd supabase-grafana
# Configure environment variables
docker-compose up -d
```

**Use Cases:**
- Deep monitoring of Supabase (PostgreSQL) MCP servers
- Performance optimization
- Capacity planning
- Incident response

**Quality Indicators:** Official Supabase project, well-documented, production-ready

---

## Rapid Integration Tools

### API Wrapper MCP (gomcpgo/api-wrapper-mcp)

**GitHub:** https://github.com/gomcpgo/api-wrapper-mcp

**Description:** Create MCP servers for any REST API using simple YAML configuration files.

**Tech Stack:** Go

**Key Features:**
- YAML-based configuration
- Automatic schema generation from OpenAPI specs
- Support for multiple APIs in one server
- Authentication handling (API keys, OAuth)
- Request/response transformation

**Configuration Example:**
```yaml
name: slack
server: http://localhost:8081
tools:
  - name: post_message
    method: POST
    path: /chat.postMessage
    parameters:
      - name: channel
        in: body
        required: true
      - name: text
        in: body
        required: true
```

**Use Cases:**
- Quickly wrap APIs without native MCP servers
- Prototype integrations
- Custom internal API exposure

**Quality Indicators:** Active development, clear documentation

---

### FastMCP (jlowin/fastmcp)

**GitHub:** https://github.com/jlowin/fastmcp

**Description:** The fast, Pythonic way to build MCP servers using decorators.

**Tech Stack:** Python

**Key Features:**
- Decorator-based tool definition
- Automatic schema generation from function signatures
- Provider system for multiple component sources
- Built-in validation
- Minimal boilerplate

**Code Example:**
```python
from fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
def greet(name: str) -> str:
    """Greet a person by name."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()
```

**Use Cases:**
- Rapid MCP server development
- Custom tool creation
- Python-based integrations
- Prototyping new capabilities

**Quality Indicators:** Active development, Pythonic design, growing community

---

## Database Integration

### Supabase MCP Server (supabase-community/supabase-mcp)

**GitHub:** https://github.com/supabase-community/supabase-mcp

**Description:** Official community MCP server for Supabase, enabling direct database management and querying.

**Tech Stack:** Python/TypeScript

**Key Features:**
- Table management (create, read, update, delete)
- Configuration fetching
- Data querying with natural language
- TypeScript type generation from schema
- Interactive React widgets for exploration
- Management API access

**Use Cases:**
- Database-backed MCP management system
- Metadata storage for other MCP servers
- Usage logging and analytics
- Configuration storage

**Quality Indicators:** Official community project, well-maintained

---

## Universal Integration Frameworks

### HAPI MCP (ai.com.mcp/hapi-mcp)

**Description:** Dynamically exposes OpenAPI REST APIs as MCP tools for AI assistants.

**Key Features:**
- Universal OpenAPI-to-MCP conversion
- No manual tool definition needed
- Supports any OpenAPI 3.0 spec
- Automatic parameter validation

**Use Cases:**
- Integrate any API with OpenAPI documentation
- Avoid writing custom MCP servers
- Standardized API access

**Quality Indicators:** Official registry listing, active development

---

## Recommended Tool Stack

For a comprehensive MCP management solution, combine these tools:

**Layer 1: Data Storage**
- Supabase (central database for metadata and logs)

**Layer 2: Monitoring**
- MCP Dashboard (real-time web UI)
- Supabase Grafana (deep database metrics)

**Layer 3: Configuration**
- mcp-serverman (version control and profiles)
- Git repository (configuration backup)

**Layer 4: Integration**
- API Wrapper MCP (YAML-based API wrapping)
- FastMCP (Python-based custom servers)
- HAPI MCP (OpenAPI conversion)

**Layer 5: Automation**
- Custom health check scripts
- Automated failover logic
- Load balancing configuration

---

## Tool Selection Criteria

When choosing tools, prioritize:

1. **Active Maintenance:** Last commit within 6 months
2. **Clear Documentation:** README with examples and API docs
3. **License:** MIT or Apache 2.0 preferred
4. **Community:** Active issues, PRs, and discussions
5. **Production Readiness:** Stable releases, not alpha/beta
6. **Integration:** Works well with existing stack

---

## Common Integration Patterns

### Pattern 1: Dashboard + Config Manager
- MCP Dashboard for monitoring
- mcp-serverman for configuration
- Git for version control

### Pattern 2: Database-Backed Management
- Supabase for metadata storage
- Custom MCP server for management operations
- Grafana for visualization

### Pattern 3: Rapid Prototyping
- FastMCP for quick server creation
- API Wrapper MCP for external APIs
- MCP Dashboard for testing

### Pattern 4: Enterprise Setup
- All tools from recommended stack
- Custom authentication layer
- Automated deployment pipelines
- Comprehensive monitoring and alerting
