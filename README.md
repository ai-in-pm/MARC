# MARC (Multi-Agent Research Collaborator)

### Overview
This Multi-Agent Research Collaborator demonstrates a flexible and extensible framework for building collaborative agent systems inspired by research in Large Language Model (LLM) multi-agent interactions.

This Repository was inspired by ChatDev, to learn more about ChatDev, visit the repository https://github.com/OpenBMB/ChatDev

### Features
- Base `Agent` class with core communication and learning capabilities
- Specialized agent types:
  - `ResearchAgent`: Conducts research and gathers information
  - `AnalyticsAgent`: Performs data analysis and generates insights
  - `CoordinatorAgent`: Manages agent tasks and coordination

### Setup Virtual Environment
1. Create a virtual environment:
```bash
# On Windows
python -m venv venv

# On macOS/Linux
python3 -m venv venv
```

2. Activate the virtual environment:
```bash
# On Windows
.\venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### LLM Selection and Agent Activation

#### Supported Large Language Models
- OpenAI GPT
- Anthropic Claude
- Mistral
- Groq
- Google Gemini

#### Workflow
1. Launch the application
2. Navigate to the "LLM Selection" tab
3. Choose your preferred Large Language Model
4. Agents will be activated automatically
5. Explore research, paper library, and collaboration features

### Environment Setup
1. Copy `.env.example` to `.env`
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` and replace placeholders with your actual API keys
   ```
   OPENAI_API_KEY=your_actual_openai_key
   ANTHROPIC_API_KEY=your_actual_anthropic_key
   MISTRAL_API_KEY=your_actual_mistral_key
   GROQ_API_KEY=your_actual_groq_key
   GOOGLE_API_KEY=your_actual_google_key
   ```

### Security Notes
- `.env` is gitignored and should NEVER be committed
- Use `.env.example` as a template for sharing configuration
- Keep all API keys confidential

### Usage
Ensure the virtual environment is activated before running:

```bash
# Method 1: Using run_example.py
python run_example.py

# Method 2: Using Python module execution
python -m examples.research_collaboration
```

### Running the GUI
To launch the Multi-Agent Research Collaboration Platform:
```bash
# Ensure virtual environment is activated
python -m gui.agent_dashboard
```

### GUI Features
The Multi-Agent Research Collaboration Platform includes multiple interactive tabs:

1. **Research Tab**
   - Conduct research on specific topics
   - Analyze research findings
   - View detailed research results

2. **Paper Library Tab**
   - Add new research papers
   - Search papers by keyword
   - View paper details
   - Manage research paper collection

3. **Agent Network Tab**
   - Visualize agent interactions
   - Display agent relationships
   - Show communication pathways

4. **Collaboration Log Tab**
   - Track agent activities
   - Log research and analysis events
   - Clear log as needed

### Interaction Workflow
1. Use the Research Tab to conduct and analyze research
2. Add papers to the library in the Paper Library Tab
3. Explore agent interactions in the Agent Network Tab
4. Monitor collaboration activities in the Collaboration Log Tab

### Research Paper Collection

#### Features
- Search research papers across multiple sources
- Sources include:
  - arXiv
  - Google Scholar
  - Semantic Scholar
- View detailed paper information
- Double-click to see full paper details

#### How to Use
1. Navigate to the "Research Papers" tab
2. Enter a search query (e.g., "machine learning", "AI ethics")
3. Click "Search Papers"
4. Browse results in the table
5. Double-click a paper to view full details

#### Advanced Filtering
- Use specific keywords to narrow down search results
- Supports multi-source research paper collection

### Dependencies for Research Paper Collection
- `requests`: Web requests
- `beautifulsoup4`: HTML parsing
- `scholarly`: Google Scholar scraping
- `selenium`: Web browser automation
- `arxiv`: arXiv API integration

### Deactivating the Virtual Environment
When you're done, you can deactivate the virtual environment:
```bash
deactivate
```

### Logging
- Console logs will be displayed during execution
- Detailed logs are saved in `multi_agent.log` in the project root directory

### Troubleshooting
- Ensure you are running the command from the `MARC` directory
- Verify Python 3.7+ is installed
- Check that all dependencies are installed via `pip install -r requirements.txt`
- If module import errors persist, check your `PYTHONPATH` and project structure

### Project Structure
- `src/`: Core agent framework
  - `agent.py`: Base Agent class
  - `specialized_agents.py`: Specialized agent implementations
- `examples/`: Demonstration scenarios
- `tests/`: Unit and integration tests (to be implemented)
