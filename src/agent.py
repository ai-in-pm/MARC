import uuid
from typing import Any, Dict, List
import logging

class Agent:
    """
    Base class for all agents in the multi-agent system.
    Provides core functionality for agent communication and interaction.
    """
    def __init__(self, name: str = None, role: str = "generic"):
        """
        Initialize an agent with a unique identifier and optional name/role.
        
        Args:
            name (str, optional): Custom name for the agent. Defaults to None.
            role (str, optional): Role or specialization of the agent. Defaults to "generic".
        """
        self.id = str(uuid.uuid4())
        self.name = name or f"{role}_agent_{self.id[:8]}"
        self.role = role
        self.memory = []
        self.knowledge_base = {}
        
        # Configure logging
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)
        
    def communicate(self, message: str, recipient: 'Agent' = None) -> Dict[str, Any]:
        """
        Send a message to another agent or broadcast to the multi-agent system.
        
        Args:
            message (str): Content of the message.
            recipient (Agent, optional): Specific agent to send the message to. 
                                         If None, broadcast to all agents.
        
        Returns:
            Dict containing message metadata and response.
        """
        self.logger.info(f"Sending message: {message}")
        
        # In a real system, this would interact with a communication broker
        return {
            "sender": self.name,
            "recipient": recipient.name if recipient else "broadcast",
            "message": message,
            "timestamp": uuid.uuid4()
        }
    
    def process_message(self, message: Dict[str, Any]) -> str:
        """
        Process an incoming message and generate a response.
        
        Args:
            message (Dict): Incoming message dictionary.
        
        Returns:
            str: Response to the message.
        """
        self.memory.append(message)
        return f"Received message from {message.get('sender', 'unknown')}"
    
    def learn(self, new_knowledge: Dict[str, Any]) -> None:
        """
        Update the agent's knowledge base.
        
        Args:
            new_knowledge (Dict): New information to be learned.
        """
        self.knowledge_base.update(new_knowledge)
        self.logger.info(f"Learned new knowledge: {new_knowledge}")
    
    def __repr__(self) -> str:
        """
        String representation of the agent.
        
        Returns:
            str: Agent's identifier and role.
        """
        return f"Agent(id={self.id}, name={self.name}, role={self.role})"
