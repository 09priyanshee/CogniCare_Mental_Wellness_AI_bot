from flask import Flask, render_template, request, jsonify
from langchain_core.messages import HumanMessage, AIMessage
from demo import (
    initial_selection,
    handle_selection,
    handle_stress_topic_selection,
    handle_emotional_regulation_topic_selection,
    handle_mindfulness_topic_selection,
    handle_coping_topic_selection,
    handle_program_interest,
    handle_program_length,
    handle_progress,
    generate_daily_motivation,
    llm,
    safe_state_transition,
    AgentState
)

app = Flask(__name__, template_folder='templates')

def initialize_state():
    return {
        "messages": [],
        "current_step": "initial_selection",
        "current_topic": "",
        "active_program": None,
        "last_motivation_date": ""
    }

state = initialize_state()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    global state
    try:
        user_input = request.json.get("message", "").strip().lower()
        prev_ai_count = len([m for m in state["messages"] if isinstance(m, AIMessage)])
        
        # Handle "resume program" command first
        if "resume program" in user_input:
            if state.get("active_program"):
                state["messages"].extend([
                    AIMessage(content="Resuming your program..."),
                    AIMessage(content="Daily Program Check-In:\n1. Mark today as complete\n2. View progress\n3. Exit program")
                ])
                state["current_step"] = "program_active"
            else:
                state["messages"].append(AIMessage(content="No active program found. Returning to main menu."))
                state["current_step"] = "initial_selection"
            return format_response(state, prev_ai_count)

        # Add user input to conversation history
        state["messages"].append(HumanMessage(content=user_input))
        
        # Handle state transitions
        current_step = state["current_step"]
        
        if current_step == "initial_selection":
            state = safe_state_transition(initial_selection(state))
        elif current_step == "await_selection":
            state = safe_state_transition(handle_selection(state))
        elif current_step == "await_stress_management_topic":
            state = safe_state_transition(handle_stress_topic_selection(state))
        elif current_step == "await_emotional_regulation_topic":
            state = safe_state_transition(handle_emotional_regulation_topic_selection(state))
        elif current_step == "await_mindfulness_topic":
            state = safe_state_transition(handle_mindfulness_topic_selection(state))
        elif current_step == "await_coping_strategy_topic":
            state = safe_state_transition(handle_coping_topic_selection(state))
        elif current_step == "program_active":
            state = safe_state_transition(handle_progress(state, user_input))
        elif current_step == "await_program_interest":
            state = safe_state_transition(handle_program_interest(state))
        elif current_step == "await_program_length":
            state = safe_state_transition(handle_program_length(state))
        else:
            # Handle free-form conversation
            try:
                prompt = f"""Respond to this mental health-related input with empathy:
                User: {user_input}
                Therapist:"""
                response = llm.invoke(prompt).content
                state["messages"].append(AIMessage(content=response))
                return jsonify({"responses": [response]})
            except Exception as e:
                print(f"Error generating response: {str(e)}")
                return jsonify({"responses": ["I'm having trouble responding right now. Please try again."]})

        return format_response(state, prev_ai_count)

    except Exception as e:
        print(f"Error: {str(e)}")
        state = initialize_state()
        return jsonify({"responses": ["Session reset due to error. Please start over."]}), 500

def format_response(state, prev_count):
    """Format messages for web response"""
    ai_messages = [msg.content.replace("**", "<strong>").replace("\n", "<br>") 
                  for msg in state["messages"] if isinstance(msg, AIMessage)]
    new_responses = ai_messages[prev_count:]
    return jsonify({"responses": new_responses})

@app.route("/reset", methods=["POST"])
def reset():
    global state
    state = initialize_state()
    return jsonify({"status": "reset"})

if __name__ == "__main__":
    app.run(debug=True)
