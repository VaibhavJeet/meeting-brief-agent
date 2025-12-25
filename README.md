# Meeting Brief Agent

An AI-powered agent that generates comprehensive pre-meeting intelligence briefs by aggregating data from emails, calendars, CRM systems, and past interactions. Built with LangChain, MCP (Model Context Protocol) integrations, and Next.js 15.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)
![LangChain](https://img.shields.io/badge/LangChain-0.3+-orange.svg)

## Problem Statement

Professionals often enter meetings unprepared due to:
- **Scattered Information**: Relevant context spread across emails, calendars, CRM, and notes
- **Time Constraints**: No time to manually review all past interactions before meetings
- **Missing Context**: Forgetting important details from previous conversations
- **No Unified View**: Lack of consolidated view of relationship history and open items

## Solution

Meeting Brief Agent provides automated pre-meeting intelligence:

1. **Calendar Integration**: Fetches upcoming meetings and participant details
2. **Email Context**: Analyzes recent email threads with meeting participants
3. **CRM Data**: Pulls contact profiles, deal history, and account information
4. **Interaction History**: Summarizes past meetings and key discussion points
5. **Brief Generation**: Creates structured, actionable meeting briefs

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Next.js 15 Frontend                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │ Calendar │  │  Briefs  │  │ Contacts │  │    Settings      │ │
│  │   View   │  │   List   │  │  Manager │  │                  │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │
└─────────────────────────────┬───────────────────────────────────┘
                              │ REST API
┌─────────────────────────────▼───────────────────────────────────┐
│                     FastAPI Backend                              │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                   LangChain Agent Core                       ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  ││
│  │  │   Context   │  │   Brief     │  │    Insight          │  ││
│  │  │  Gatherer   │  │  Generator  │  │    Extractor        │  ││
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘  ││
│  └─────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    MCP Integrations                          ││
│  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────────────────┐ ││
│  │  │Calendar│  │ Email  │  │  CRM   │  │      Database      │ ││
│  │  │  MCP   │  │  MCP   │  │  MCP   │  │        MCP         │ ││
│  │  └────────┘  └────────┘  └────────┘  └────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Remote LLM │    │  Local LLM   │    │   Vector DB  │
│ (OpenAI/etc) │    │   (Ollama)   │    │  (ChromaDB)  │
└──────────────┘    └──────────────┘    └──────────────┘
```

## Tech Stack

### Backend
- **Python 3.11+**
- **FastAPI** - High-performance async API framework
- **LangChain 0.3+** - Agent orchestration, chains, tools, memory
- **LangGraph** - Multi-agent workflow orchestration
- **ChromaDB** - Vector storage for semantic search
- **Pydantic** - Data validation and settings management

### Frontend
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe development
- **TailwindCSS** - Utility-first styling
- **Shadcn/UI** - Accessible component library
- **React Query** - Server state management

### MCP Integrations
- **Calendar MCP** - Google Calendar/Outlook integration
- **Email MCP** - Gmail/IMAP email access
- **CRM MCP** - Salesforce/HubSpot data
- **Database MCP** - Meeting and brief storage

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker (optional, for local services)

### 1. Clone the repository
```bash
git clone https://github.com/VaibhavJeet/meeting-brief-agent.git
cd meeting-brief-agent
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Configure your .env file
python -m uvicorn app.main:app --reload
```

### 3. Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

### 4. Access the Application
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

## Configuration

### LLM Configuration

The agent supports both remote and local LLMs:

#### Remote LLM (OpenAI, Anthropic, etc.)
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo-preview
```

#### Local LLM (Ollama)
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

#### Local LLM (llama.cpp)
```env
LLM_PROVIDER=llamacpp
LLAMACPP_MODEL_PATH=/path/to/model.gguf
LLAMACPP_N_CTX=4096
```

### MCP Integrations

Configure in `config/mcp.yaml`:

```yaml
integrations:
  calendar:
    enabled: true
    provider: google  # or outlook
    credentials_path: ./credentials/google.json

  email:
    enabled: true
    provider: gmail
    credentials_path: ./credentials/gmail.json

  crm:
    enabled: false
    provider: hubspot  # or salesforce
    api_key: ${CRM_API_KEY}

  database:
    enabled: true
    provider: postgresql
    connection_string: ${DATABASE_URL}
```

## Project Structure

```
meeting-brief-agent/
├── backend/
│   ├── app/
│   │   ├── agents/           # LangChain agents
│   │   │   ├── context_gatherer.py
│   │   │   ├── brief_generator.py
│   │   │   ├── insight_extractor.py
│   │   │   └── orchestrator.py
│   │   ├── chains/           # LangChain chains
│   │   ├── tools/            # Custom LangChain tools
│   │   ├── mcp/              # MCP integration handlers
│   │   │   ├── base.py
│   │   │   ├── calendar.py
│   │   │   ├── email.py
│   │   │   ├── crm.py
│   │   │   └── database.py
│   │   ├── models/           # Pydantic models
│   │   ├── api/              # FastAPI routes
│   │   └── core/             # Configuration, LLM setup
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js App Router
│   │   ├── components/       # React components
│   │   ├── lib/              # Utilities
│   │   └── hooks/            # Custom hooks
│   ├── package.json
│   └── Dockerfile
├── config/
│   └── mcp.yaml              # MCP configuration
├── docker-compose.yml
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
└── LICENSE
```

## Features

### Calendar Integration
- Upcoming meeting detection
- Participant extraction
- Recurring meeting tracking
- Multi-calendar support

### Email Context
- Thread summarization
- Sentiment analysis
- Key topic extraction
- Attachment tracking

### CRM Integration
- Contact profiles
- Deal/opportunity status
- Account history
- Custom field support

### Brief Generation
- Participant backgrounds
- Relationship timeline
- Open action items
- Suggested talking points
- Risk/opportunity highlights

## API Reference

### Meetings
- `GET /api/meetings` - List upcoming meetings
- `GET /api/meetings/{id}` - Get meeting details
- `POST /api/meetings/{id}/brief` - Generate brief for meeting

### Briefs
- `GET /api/briefs` - List generated briefs
- `GET /api/briefs/{id}` - Get brief details
- `POST /api/briefs` - Create manual brief
- `PUT /api/briefs/{id}` - Update brief

### Contacts
- `GET /api/contacts` - List contacts
- `GET /api/contacts/{id}` - Get contact details
- `GET /api/contacts/{id}/history` - Get interaction history

### Settings
- `GET /api/settings/integrations` - Get integration status
- `PUT /api/settings/integrations` - Update integrations

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest` (backend) / `npm test` (frontend)
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [LangChain](https://langchain.com) for the agent framework
- [Model Context Protocol](https://modelcontextprotocol.io) for integration standards
- [Anthropic](https://anthropic.com) for Claude and MCP specification
