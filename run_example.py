import os
import sys

# Add the project root to Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from examples.research_collaboration import multi_agent_research_scenario

if __name__ == "__main__":
    multi_agent_research_scenario()
