#  Copyright 2021, Verizon Media
#  Licensed under the terms of the ${MY_OSI} license. See the LICENSE file in the project root for terms
from ychaos.agents.agent import Agent
from ychaos.app_logger import AppLogger


def log_agent_lifecycle(func):
    logger = AppLogger.get_logger("agents")

    def annotation(*args, **kwargs):
        agent: Agent = args[0]
        logger.info(
            event="agents.lifecycle.start",
            agent=agent.config.name,
            method=func.__name__,
            state=agent.current_state.name,
        )
        try:
            _return_val = func(*args, **kwargs)
        except Exception as e:
            raise e from None
        finally:
            logger.info(
                event="agents.lifecycle.end",
                agent=agent.config.name,
                method=func.__name__,
                state=agent.current_state.name,
            )
        return _return_val

    return annotation
