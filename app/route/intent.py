from llm.model_manager import detect_intent , detect_intent_with_openai
from state.memory import history
from state.state_user import conversation_state

def handleIntent(user_message):
    print("start")
    recent_history = history[-6:]
    current_city = conversation_state["current_city"]
    intent = detect_intent(
        user_message,
        recent_history,
        current_city,
    )
    return intent
