# Contrib Agent

YChaos allows the users to define their own chaos agents to be run
on their targets to test the resiliency of the system. The principal
concept of contrib agent is to have users write their own chaos modules
and eventually contribute back to the framework.

## Quickstart

To develop a simple YChaos agent, create a python file say `/tmp/awesome_agent.py`, 
with a sample structure given below. 

```python linenums="1" hl_lines="48 49"
from vzmi.ychaos.agents.agent import Agent, AgentConfig
from vzmi.ychaos.agents.utils.annotations import log_agent_lifecycle
from queue import LifoQueue
from pydantic import BaseModel


class MyAwesomeAgentConfig(BaseModel):
    name: str = "my_awesome_agent"
    description: str = "This is an invincible agent"
    
    # Define the pydantic model with configuration that can be
    # sent to the agent during initialization

class MyAwesomeAgent(Agent):
    """
    An agent of unimaginable capabilities.
    """

    def __init__(self, config):
        assert isinstance(config, AgentConfig)
        super(MyAwesomeAgent, self).__init__(config)

    def monitor(self) -> LifoQueue:
        super(MyAwesomeAgent, self).monitor()
        # Monitor the agent and the system as to
        # how the agent is performing
        return self._status

    @log_agent_lifecycle
    def setup(self) -> None:
        super(MyAwesomeAgent, self).setup()
        # Set up the system to perform an attack

    @log_agent_lifecycle
    def run(self) -> None:
        super(MyAwesomeAgent, self).run()
        # Define the program Logic here as to what needs
        # to be done during attack, say delete an important file

    @log_agent_lifecycle
    def teardown(self) -> None:
        super(MyAwesomeAgent, self).teardown()
        # Bring back the system's state to normal
        # by reverting all the changes you have done during the attack

# Define these 2 Global constants for the framework to import
# these classes.
AgentClass = MyAwesomeAgent
AgentConfigClass = MyAwesomeAgentConfig
```

Once the python module is created, all that is needed to be done is to
import this file in testplan. Configure the attack configuration in the testplan
as mentioned below by changing relevant parameters. Refer to the Testplan
schema for more details.

=== "JSON"

    ```json
    {
        "attack": {
            "target_type": "self",
            "agents": [
                {
                    "type": "contrib",
                    "path": "/tmp/awesome_agent.py",
                    "config": {
                        "key1": "value1",
                        "key2": "value2"
                    }
                }
            ]
        }
    }
    ```
    
=== "YAML"

    ```yaml
    ---
    attack:
        target_type: self     # Your preferred target type
        agents:
        -   type: contrib
            path: "/tmp/awesome_agent.py"
            config:
                key1: value1
                key2: value2
    ```
