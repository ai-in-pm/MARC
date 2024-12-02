import os
import sys

# Ensure the project root is in the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import logging
from src.agent import Agent
from src.specialized_agents import ResearchAgent, AnalyticsAgent, CoordinatorAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Add console output
        logging.FileHandler(os.path.join(project_root, 'multi_agent.log'))  # Log to file
    ]
)

def multi_agent_research_scenario():
    """
    Demonstrate a multi-agent research collaboration scenario.
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize coordinator
        coordinator = CoordinatorAgent()
        
        # Create specialized agents
        ai_research_agent = ResearchAgent(research_domain="Artificial Intelligence")
        data_analyst = AnalyticsAgent()
        
        # Register agents with coordinator
        coordinator.register_agent(ai_research_agent)
        coordinator.register_agent(data_analyst)
        
        # Conduct research
        research_topic = "Large Language Model Multi-Agent Systems"
        research_findings = ai_research_agent.conduct_research(research_topic)
        
        # Analyze research findings
        analysis_result = data_analyst.analyze_data(research_findings)
        
        # Coordinator assigns follow-up task
        follow_up_task = {
            "type": "detailed_investigation",
            "topic": research_topic,
            "priority": "high"
        }
        task_assignment = coordinator.assign_task(ai_research_agent, follow_up_task)
        
        # Log results
        logger.info("Multi-Agent Research Collaboration Results:")
        logger.info(f"Research Findings: {research_findings}")
        logger.info(f"Analysis Results: {analysis_result}")
        logger.info(f"Task Assignment: {task_assignment}")
        
        return {
            "research_findings": research_findings,
            "analysis_result": analysis_result,
            "task_assignment": task_assignment
        }
    
    except Exception as e:
        logger.error(f"Error in multi-agent research scenario: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    multi_agent_research_scenario()
