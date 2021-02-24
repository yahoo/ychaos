#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms
from vzmi.ychaos.agents.agent import Agent
from vzmi.ychaos.app_logger import AppLogger

logging = AppLogger.get_logger("agents")


def log_agent_lifecycle(func):
    def annotation(*args, **kwargs):
        """
        Logs the lifecycle of the agent
        Args:
            *args: args[0] is the agent
            **kwargs:
        """
        agent: Agent = args[0]
        logging.info(
            event="agents.lifecycle.start",
            agent=agent.config.name,
            method=func.__name__,
            state=agent.current_state,
        )
        try:
            _return_val = func(*args, **kwargs)
        except Exception as e:
            raise e from None
        finally:
            logging.info(
                event="agents.lifecycle.end",
                agent=agent.config.name,
                method=func.__name__,
                state=agent.current_state,
            )
        return _return_val

    return annotation
