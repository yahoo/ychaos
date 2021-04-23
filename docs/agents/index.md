# YChaos Agents

Agents are the actual attack modules that are responsible to
perform monitored attack onto the system.

## Installation

To install the required dependencies to run agents, you can use the `agents`
extras.

```bash
pip install vzmi.ychaos[agents]
```

The above command will install the core requirements of ychaos
along with the optional requirements needed to run chaos agents on the system.

## Configuration

The only input to any agent is a configuration object. This is usually supplied
from the test plan. On the implementation side, the dictionary is serialized
to a proper schema to get all the required details to run the agent.

Any custom configuration needed can be defined by implementing the [`AgentConfig`](#TODO) class.

## Lifecycle

The agents defined in the package (and the extensions) follow a simple lifecycle.
These lifecycle define what the agent does before, during and after the attack.
The lifecycle of the agents are defined by these methods

1. **setup**: Responsible for setting up the system, environment for the minion to run
2. **run**: The actual attack on the system
3. **teardown**: Bringing back the system back to how it was before the attack
4. **monitor**: A special method that tracks the system, minion and its current status.

Each and every agent that is defined should implement each of these lifecyle methods
to define their behaviour in the particular scenario. The base Agent is defined [here][vzmi.ychaos.agents.agent.Agent].
Any extending agent can implement this interface.
