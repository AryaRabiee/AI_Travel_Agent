from llm.model_manager import detect_intent 
from state.memory import history
from state.state_user import conversation_state
from llm.log import logger

def handleIntent(user_message, session):
    """
    Intent رو detect کن
    """
    logger.info("handleIntent called | message: %s", user_message)
    
    recent_history = session.history[-6:]
    current_city = session.conversation_state.get("current_city")
    
    intent_data = detect_intent(
        user_message,
        recent_history,
        current_city,
    )
    
    logger.info("Intent detected: %s", intent_data)
    return intent_data
