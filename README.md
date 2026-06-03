# Py Analytics Agent

Enterprise AI-powered data analytics assistant that allows users to query enterprise data using natural language and receive intelligent responses including text insights, tables, and visual charts.

The platform combines:

- Large Language Models
- Secure code execution
- Databricks analytics
- Conversational memory
- Private artifact storage
- Modern web UI

---

# Architecture Overview

```
                 User
                  |
                  v
          Next.js Frontend
                  |
                  |
              FastAPI
                  |
      +-----------+------------+
      |           |            |
      v           v            v
   OpenAI       Cosmos DB      E2B Sandbox
      |           |            |
      |           |            |
      |           |       Python Runtime
      |           |            |
      |           |            v
      |           |       Databricks SQL
      |           |
      v           v
   Code Gen   Chat Memory

                  |
                  v

            Azure Blob Storage
            (Private Artifacts)
```

---

# Core Capabilities

## Conversational Analytics

Users can ask:

```
Show monthly fraud trends
Create a bar chart by month
Find anomalies
Summarize latest KPIs
```

The assistant automatically:

1. Understands intent
2. Reads schema context
3. Generates Python code
4. Executes securely
5. Returns analytics output

---

# Technology Stack

## Frontend

### Next.js

Used for the user interface.

Features:

- React-based UI
- TypeScript support
- Component architecture
- Fast development experience

Location:

```
frontend/
```

Major components:

```
components/

Sidebar.tsx
    Chat navigation

ChatInput.tsx
    User prompts

MessageBubble.tsx
    Chat experience

ResultRenderer.tsx
    Dynamic rendering:
        - text
        - tables
        - charts

NewChatModal.tsx
    Create analytics sessions
```

---

## TypeScript

Used for frontend type safety.

Example:

```ts
type AgentResult =
 | ChartResult
 | TableResult
 | TextResult
```

Benefits:

- Prevents UI/runtime mismatch
- Validates backend contracts
- Improves maintainability

---

# Backend

## FastAPI

Python API backend.

Responsibilities:

- Authentication abstraction
- Chat APIs
- Agent orchestration
- Databricks metadata APIs
- Artifact handling

Location:

```
backend/app
```

---

# API Modules

## Chat Service

Handles:

- Create chats
- Store messages
- Retrieve history

Storage:

Azure Cosmos DB

Collections:

```
chats
messages
```

---

# AI Agent Flow

## Intent Classification

Determines:

```
GENERAL
or
ANALYTICS
```

Examples:

GENERAL:

```
hi
thank you
```

ANALYTICS:

```
create sales chart
show fraud trend
```

---

# LLM Code Generation

Provider:

OpenAI API

Responsibilities:

- Understand user request
- Generate Python analytics code
- Repair failed code

Generated code can:

- Query Databricks
- Transform data
- Create charts

---

# E2B Sandbox

Secure Python execution environment.

Purpose:

Never execute AI generated code directly on backend.

Flow:

```
Generated Python
        |
        v
E2B Sandbox
        |
        v
Safe execution
```

Installed runtime includes:

- pandas
- matplotlib
- databricks connector

---

# Databricks Integration

Used as enterprise data warehouse.

Supports:

- Catalog discovery
- Schema discovery
- Table metadata
- SQL execution

Example:

```
catalog.schema.table

fraud360.gold.mv_daily_fraud_kpis
```

---

# Chart Generation

Charts are generated using:

- Python
- matplotlib

Flow:

```
User request

"Create monthly trend"

        |

LLM creates code

        |

E2B executes

        |

PNG generated

        |

Azure Blob upload

        |

Frontend renders
```

---

# Azure Blob Storage

Stores generated artifacts.

Examples:

```
charts/{chat_id}/{uuid}.png
```

Security:

- Storage account is private
- No public blob access

---

# User Delegation SAS

Images are accessed using temporary SAS URLs.

Cosmos stores:

```json
{
 "blob_name": "charts/file.png"
}
```

Runtime generates:

```
temporary secure URL
```

Benefits:

- No account keys
- Short-lived access
- Enterprise security model

---

# Cosmos DB

Stores:

## Chats

```json
{
 "id": "...",
 "title": "...",
 "catalog": "fraud360",
 "schema": "gold"
}
```

## Messages

```json
{
 "role": "assistant",
 "content": {
    "type": "chart",
    "blob_name": "..."
 }
}
```

---

# Authentication Design

Current development:

```
x-user-id header
```

Future:

Microsoft Entra ID

Flow:

```
User Login
    |
JWT Token
    |
FastAPI validates
    |
Extract user identity
```

---

# Security Features

Implemented:

- Private storage
- User Delegation SAS
- Sandbox execution
- User scoped chats
- Code validation hooks

---

# Running Locally

## Backend

Create environment:

```
python -m venv .venv
```

Start:

```
uvicorn backend.app.main:app --reload
```

---

## Frontend

Install:

```
npm install
```

Run:

```
npm run dev
```

Open:

```
http://localhost:3000
```

---

# Future Enhancements

## Refresh Analytics Results

Planned:

Each AI generated result will have:

```
↻ Refresh
```

User clicks:

- Re-executes saved generated code
- Pulls latest Databricks data
- Updates chart/table

Flow:

```
Stored code
    |
    v
E2B execute again
    |
    v
Fresh Databricks query
    |
    v
Updated result
```

---

## Additional Roadmap

- Streaming responses
- Dashboard mode
- Scheduled reports
- Chart editing
- Export PDF
- Role based access
- Deployment to AKS