# Syntra - AI-Powered Workflow Automation Agent

[![Google ADK](https://img.shields.io/badge/Google-ADK-4285F4?logo=google)](https://github.com/google/adk)
[![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-8E75B2)](https://ai.google.dev/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)

> **Automate repetitive tasks using natural language.** Syntra is an intelligent multi-agent system that understands your workflow needs and executes them automatically.

---

## 🎯 What It Does

Syntra transforms natural language into automated workflows:

```
"When I read a sales email, extract top 5 deals and email me"
                            ↓
        Syntra automatically processes sales emails
                            ↓
            Delivers structured insights to your inbox
```

**No coding. No configuration. Just describe what you want.**

---

## ✨ Key Features

- 🤖 **Multi-Agent Architecture** - Hierarchical ADK agents with parent-child delegation
- 🧠 **Intelligent Content Understanding** - Detects email types, extracts structured data
- 📧 **Real Email Integration** - Gmail SMTP with HTML formatting
- 🌐 **Browser Extension** - Chrome extension captures Gmail & Medium events
- ⚡ **Dynamic Processing** - Single LLM core adapts to any user query
- 💾 **Context Management** - In-memory session service maintains state
- 🎨 **Modern UI** - Glassmorphism design with workflow templates

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Google Gemini API Key
- Gmail account with App Password
- Chrome browser

### Installation

```bash
# Clone repository
git clone <repository-url>
cd WorkFLowSynthesizer

# Install dependencies
pip install -r requirements.txt

# Configure API keys
# Edit workflow_synthesizer/config.py with your credentials
```

### Configuration

**1. Gemini API Key**

Edit `config.py`:
```python
GEMINI_API_KEY = "your-gemini-api-key"
```

**2. Gmail SMTP**

Edit `workflow_synthesizer/config.py`:
```python
GMAIL_USER = "your-email@gmail.com"
GMAIL_APP_PASSWORD = "your-app-password"
GMAIL_DISPLAY_NAME = "Syntra"
```

[Get Gmail App Password](https://support.google.com/accounts/answer/185833)

### Run Server

```bash
python unified_server.py
```

Access dashboard at: **http://localhost:8000/dashboard**

### Install Chrome Extension

1. Open Chrome → `chrome://extensions`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select `chrome_extension/` folder
5. Extension icon appears in toolbar

---

## 📖 Usage Examples

### Example 1: Sales Email Analysis

**User Input:**
```
When I open a sales report email, extract top 5 deals by value 
and overdue follow-ups, then email me
```

**What Happens:**
1. Syntra monitors Gmail for emails you open
2. Detects sales-related content automatically
3. Extracts deals with values and dates
4. Identifies overdue items
5. Sends formatted summary to your inbox

### Example 2: Article Summarization

**User Input:**
```
When I read a Medium article, extract 3 key takeaways and email me
```

**What Happens:**
1. Chrome extension captures article content
2. LLM extracts main points
3. Delivers concise summary via email

### Example 3: Email Tone Check

**User Input:**
```
When I compose an email, analyze the tone and suggest improvements
```

**What Happens:**
1. Monitors Gmail compose window
2. Analyzes tone (professional, casual, aggressive)
3. Provides actionable suggestions
4. Sends analysis before you hit send

---

## 🏗️ Architecture

### Three-Tier Processing

```
User Request
    ↓
┌─────────────────────────────────┐
│  Tier 1: Simple Executor        │ → Basic workflows
│  Tier 2: Multi-Agent System     │ → Coordinated processing
│  Tier 3: Hierarchical ADK       │ → Parent-child delegation
└─────────────────────────────────┘
    ↓
Dynamic LLM Processing
    ↓
Result Delivery (Email/Popup)
```

### Multi-Agent System

```
WorkflowCoordinator (Parent)
├── UnderstandingAgent → Parses user intent
├── ActionAgent → Processes content dynamically
└── DeliveryAgent → Sends results via email/popup
```

### Google ADK Features Used

- ✅ Multi-agent orchestration with `Agent` class
- ✅ Hierarchical architecture using `sub_agents` pattern
- ✅ Custom tool integration with function decorators
- ✅ Dynamic model selection (Gemini 2.5 Flash)
- ✅ Stateful agent execution with context
- ✅ Tool function calling from LLM responses
- ✅ Session management for workflow state
- ✅ Error handling with graceful fallbacks

---

## 📁 Project Structure

```
WorkFLowSynthesizer/
├── workflow_synthesizer/          # ADK package
│   ├── agent.py                   # Main orchestrator
│   ├── config.py                  # Gmail & Gemini config
│   ├── tools.py                   # ADK tools
│   └── sub_agents/                # Specialized agents
├── multi_agent/                   # Multi-agent system
│   ├── orchestrator.py            # Agent coordinator
│   ├── hierarchical_processor.py  # ADK hierarchy
│   ├── action_agent.py            # Content processor
│   └── delivery_agent.py          # Result delivery
├── agents/                        # Simple agents
│   └── executor.py                # Basic executor
├── tools/                         # Core tools
│   └── summarizer.py              # LLM processor
├── core/                          # Core services
│   ├── session_service.py         # State management
│   ├── smart_trigger_service.py   # Workflow parser
│   └── trigger_manager.py         # Event coordination
├── chrome_extension/              # Browser extension
│   ├── manifest.json
│   ├── popup/                     # Extension UI
│   └── scripts/                   # Content scripts
├── unified_server.py              # FastAPI server
├── config.py                      # API keys
└── README.md
```

---

## 🛠️ API Endpoints

### Workflows

```bash
# Create workflow
POST /workflow
{
  "query": "When I download a PDF, summarize it and email me",
  "use_smart": true
}

# List workflows
GET /workflows

# Get workflow
GET /workflow/{id}
```

### Events

```bash
# Send event
POST /event
{
  "event_type": "email_read",
  "email_subject": "Sales Report",
  "email_body": "..."
}

# List events
GET /events
```

### Results

```bash
# Get result
GET /result/{id}

# List results
GET /results
```

---

## 🎨 Chrome Extension Features

### Popup Interface

- **Status Dashboard** - Server status, event count
- **Email Configuration** - Set default recipient
- **Quick Templates** - One-click workflow creation
- **Active Workflows** - Toggle workflows on/off
- **Recent Activity** - View processed events

### Content Scripts

- **Gmail Compose** - Captures email drafts
- **Gmail Read** - Monitors opened emails
- **Medium Articles** - Extracts article content

---

## 🧪 Testing

### Run Tests

```bash
# Integration tests
python -m tests.test_agent

# Evaluation tests
pytest eval/test_eval.py -v
```

### Manual Testing

```bash
# Start server
python unified_server.py

# In another terminal, test workflow creation
curl -X POST http://localhost:8000/workflow \
  -H "Content-Type: application/json" \
  -d '{"query": "When I download a file, email me", "use_smart": true}'
```

---

## 📊 Technical Stack

| Component | Technology |
|-----------|-----------|
| **Agent Framework** | Google ADK |
| **LLM** | Gemini 2.5 Flash |
| **Backend** | FastAPI |
| **File Monitoring** | Watchdog |
| **Email** | Gmail SMTP |
| **Browser** | Chrome Extension (Manifest V3) |
| **Storage** | In-memory + JSON |

---

## 🔧 Configuration Options

### Model Selection

Edit `workflow_synthesizer/config.py`:
```python
DEFAULT_MODEL = "gemini-2.5-flash"  # or "gemini-2.0-flash"
```

### Session Limits

Edit `workflow_synthesizer/config.py`:
```python
MAX_EVENTS = 100   # Maximum events to store
MAX_RESULTS = 50   # Maximum results to store
```

### Downloads Path

Edit `workflow_synthesizer/config.py`:
```python
DOWNLOADS_PATH = "~/Downloads"
```

---

## 🚧 Troubleshooting

### Server won't start

```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill process if needed
kill -9 <PID>
```

### Extension not capturing events

1. Reload extension at `chrome://extensions`
2. Refresh Gmail/Medium page
3. Check browser console (F12) for logs

### Email not sending

1. Verify Gmail App Password is correct
2. Check 2FA is enabled on Gmail account
3. Review server logs for SMTP errors

### API rate limit (429 error)

1. Wait 1-2 minutes for quota reset
2. Switch to different Gemini model
3. Reduce workflow creation frequency

---

## 🎯 Roadmap

- [ ] Task management integration (Asana, Jira)
- [ ] Slack/Discord notifications
- [ ] PDF parsing for financial reports
- [ ] Workflow templates library
- [ ] Multi-user authentication
- [ ] Analytics dashboard
- [ ] Mobile app support

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📝 License

MIT License - See [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

- **Google ADK Team** - For the amazing agent framework
- **Google Gemini** - For powerful LLM capabilities
- **FastAPI** - For elegant API framework

---

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ using Google ADK and Gemini 2.5 Flash**
