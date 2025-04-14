from typing import List, Dict, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import requests
from datetime import datetime  


# Configuration
API_KEY = "AIzaSyDL6QfkZ6aTiiuC270rkTs-Tb8nt0dPOfk"

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=API_KEY,
    temperature=0.7,
    max_output_tokens=600
)

llm_program = ChatGoogleGenerativeAI(  # For program generation
    model="gemini-2.0-flash",
    google_api_key="AIzaSyDL6QfkZ6aTiiuC270rkTs-Tb8nt0dPOfk",
    temperature=0.7
)

class AgentState(TypedDict):
    messages: List[BaseMessage]
    current_step: str
    current_topic: str 

state = {
    "messages": [],
    "current_step": "initial_selection",
    "current_topic": "",
    "active_program": None ,
    "last_motivation_date": ""
}


def stress_management_topic_selection(state: AgentState):
    state["messages"].append(AIMessage(
        content="Choose a stress management topic:\n"
                "1. Breathing Techniques\n"
                "2. Time Management\n"
                "3. Relaxation Exercises\n"
                "4. Something else...\n"
                "Select a number between (1-4)"
    ))
    return {**state, "current_step": "await_stress_management_topic"}

def emotional_regulation_topic_selection(state: AgentState):
    state["messages"].append(AIMessage(
        content="Choose an emotional regulation topic:\n"
                "1. Managing Anger\n"
                "2. Dealing with Sadness\n"
                "3. Overcoming Anxiety\n"
                "4. Something else...\n"
                "Select a number between (1-4)"
    ))
    return {**state, "current_step": "await_emotional_regulation_topic"}

def mindfulness_topic_selection(state: AgentState):
    state["messages"].append(AIMessage(
        content="Choose a mindfulness exercise:\n"
                "1. Body Scan Meditation\n"
                "2. Gratitude Practice\n"
                "3. Visualization Techniques\n"
                "4. Something else...\n"
                "Select a number between (1-4)"
    ))
    return {**state, "current_step": "await_mindfulness_topic"}

def coping_strategy_topic_selection(state: AgentState):
    state["messages"].append(AIMessage(
        content="Choose a coping strategy:\n"
                "1. Journaling\n"
                "2. Talking to Someone\n"
                "3. Physical Activity\n"
                "4. Something else...\n"
                "Select a number between (1-4)"
    ))
    return {**state, "current_step": "await_coping_strategy_topic"}

def generate_content(topic: str) -> str:
    prompt = f"""Provide actionable advice and exercises for the topic '{topic}'. 
    Focus on practical steps and empathy. Use plain text only. Avoid using markdown symbols like *, **, or other special characters. writr under 300 words.
    """
    
    try:
        return llm.invoke(prompt).content
    except Exception as e:
        return f"Error generating content: {str(e)}"

def handle_custom_help(state: AgentState):
    last_input = next(
        (msg.content for msg in reversed(state["messages"]) if isinstance(msg, HumanMessage)),
        ""
    ).strip()

    prompt = f"""User input: {last_input}
Provide empathetic and actionable advice for their concern."""
    
    try:
        response = llm.invoke(prompt).content
        state["messages"].append(AIMessage(content=response))
        state["messages"].append(AIMessage(content="Would you like to explore this further?"))
        return {**state, "current_step": "await_custom_help_response"}
    
    except Exception as e:
        state["messages"].append(AIMessage(content=f"Error handling custom help: {str(e)}"))




def generate_program(topic: str, days: int) -> str:
    prompt = f"""Create a short {days}-day program for {topic} with:
    - Short but clear daily structure
    - Few actionable steps
    - Short final encouragement
    Use plain text only. Avoid using markdown symbols like *, **, or other special characters. 
    The text should be easy to read and understand and under 600 words"""

    try:
        return llm_program.invoke(prompt).content
    except Exception as e:
        return f"Error generating program: {str(e)}"
    



def initial_selection(state: AgentState):
    today = datetime.now().strftime("%Y-%m-%d")
    
    if state.get("last_motivation_date") != today:
        daily_motivation = generate_daily_motivation()
        state["messages"].append(AIMessage(content=f"✨ Daily Motivation ✨\n{daily_motivation}"))
        state["last_motivation_date"] = today

    state["messages"].append(AIMessage(
        content="Welcome to MindfulBot, your Mental Health Therapy Chatbot!\n\n"
                "What do you need today?\n"
                "1. Stress Management\n"
                "2. Emotional Regulation\n"
                "3. Mindfulness Exercises\n"
                "4. Coping Strategies\n"
                "5. Just Chat\n"
                "Select a number between (1-5)"
    ))
    return {**state, "current_step": "await_selection"}



def generate_daily_motivation() -> str:
    prompt = """Write a short motivational message for someone struggling with mental health challenges."""
    
    try:
        return llm.invoke(prompt).content
    except Exception as e:
        return f"Error generating motivation: {str(e)}"

def handle_selection(state: AgentState):
    last_input = next(
        (msg.content for msg in reversed(state["messages"]) if isinstance(msg, HumanMessage)),
        ""
    ).strip().lower()

    option_map = {
        "stress management": "1", 
        "emotional regulation": "2", 
        "mindfulness exercises": "3", 
        "coping strategies": "4", 
        "just chat": "5"
    }
    
    selected_option = option_map.get(last_input, last_input)

    if selected_option == "1":
        return stress_management_topic_selection(state)
    elif selected_option == "2":
        return emotional_regulation_topic_selection(state)
    elif selected_option == "3":
        return mindfulness_topic_selection(state)
    elif selected_option == "4":
        return coping_strategy_topic_selection(state)
    elif selected_option == "5":
        state["messages"].append(AIMessage(content="Let's chat! How can I help you today?"))
        return {**state, "current_step": "await_just_chat"}


def handle_stress_topic_selection(state: AgentState):
    last_input = next(
        (msg.content for msg in reversed(state["messages"]) if isinstance(msg, HumanMessage)),
        ""
    ).strip()

    
    topic_map = {
        "1" : "Breathing Techniques\n",
        "2" : "Time Management\n",
        "3" : "Relaxation Exercises\n",
        "4" : "Something else...\n"
    }

    if last_input in topic_map:
        if last_input == "4":
            state["messages"].append(AIMessage(content="What would you like help with?"))
            return {**state, "current_step": "await_custom_help"}
        
        state["current_topic"] = topic_map[last_input]  # Store topic
        response = generate_content(state["current_topic"])
        state["messages"].append(AIMessage(content=response))
        state["messages"].append(AIMessage(content=f"Would you like to start a structured program for {topic_map[last_input]}? (yes/no)"))
        return {**state, "current_step": "await_program_interest"}

    
    state["messages"].append(AIMessage(content="Please select a valid topic (1-4)"))
    return {**state, "current_step": "await_stress_topic_selection"}



def handle_emotional_regulation_topic_selection(state: AgentState):
    last_input = next(
        (msg.content for msg in reversed(state["messages"]) if isinstance(msg, HumanMessage)),
        ""
    ).strip()

    
    topic_map = {
        "1" : "Managing Anger",
        "2" : "Dealing with Sadness",
        "3" : "Overcoming Anxiety", 
        "4": "Something else..."
    }

    if last_input in topic_map:
        if last_input == "4":  # User selected "Something else"
            state["messages"].append(AIMessage(content="What do you need help with?"))
            return {**state, "current_step": "await_custom_help"}  # Transition to custom help mode

    if last_input in topic_map:
        topic = topic_map[last_input]
        response = generate_content(topic)
        state["messages"].append(AIMessage(content=response))
        state["messages"].append(AIMessage(content=f"Would you like to start a structured program for {topic_map[last_input]}? (yes/no)"))
        return {**state, "current_step": "await_program_interest"}

    state["messages"].append(AIMessage(content="Please select a valid topic (1-4)."))
    return {**state, "current_step": "await_emotional_topic_selection"}

def handle_mindfulness_topic_selection(state: AgentState):
    last_input = next(
        (msg.content for msg in reversed(state["messages"]) if isinstance(msg, HumanMessage)),
        ""
    ).strip()

    
    topic_map = {
        "1" : "Body Scan Meditation",
        "2" : "Gratitude Practice",
        "3" : "Visualization Techniques",
        "4" : "Something else..."
    }
    if last_input in topic_map:
        if last_input == "4":  # User selected "Something else"
            state["messages"].append(AIMessage(content="What do you need help with?"))
            return {**state, "current_step": "await_custom_help"}  # Transition to custom help mode
        
    if last_input in topic_map:
        # Generate meditation content for the selected topic
        topic = topic_map[last_input]
        response = generate_content(topic)
        state["messages"].append(AIMessage(content=response))
        state["messages"].append(AIMessage(content=f"Would you like to start a structured program for {topic_map[last_input]}? (yes/no)"))
        return {**state, "current_step": "await_program_interest"}


    state["messages"].append(AIMessage(content="Please select a valid topic (1-4)."))
    return {**state, "current_step": "await_mindfulness_topic_selection"}

def handle_coping_topic_selection(state: AgentState):
    last_input = next(
        (msg.content for msg in reversed(state["messages"]) if isinstance(msg, HumanMessage)),
        ""
    ).strip()

    
    topic_map = {
        "1" : "Journaling",
        "2" : "Talking to Someone",
        "3" : "Physical Activity",
        "4" : "Something else..."
    }

    if last_input in topic_map:
        if last_input == "4":  # User selected "Something else"
            state["messages"].append(AIMessage(content="What do you need help with?"))
            return {**state, "current_step": "await_custom_help"}  # Transition to custom help mode

    if last_input in topic_map:
        # Generate meditation content for the selected topic
        topic = topic_map[last_input]
        response = generate_content(topic)
        state["messages"].append(AIMessage(content=response))
        state["messages"].append(AIMessage(content=f"Would you like to start a structured program for {topic_map[last_input]}? (yes/no)"))
        return {**state, "current_step": "await_program_interest"}


    state["messages"].append(AIMessage(content="Please select a valid topic (1-4)."))
    return {**state, "current_step": "await_accountability_topic_selection"}

def handle_just_chat(state: AgentState):
    last_input = next(
        (msg.content for msg in reversed(state["messages"]) if isinstance(msg, HumanMessage)),
        ""
    ).strip().lower()

    if "resume program" in last_input:
        if state.get("active_program"):
            # Maintain existing messages while adding check-in prompt
            return {
                **state,
                "messages": state["messages"] + [
                    AIMessage(content="Resuming your program..."),
                    AIMessage(content="Daily Program Check-In:\n1. Mark today as complete\n2. View progress\n3. Exit program")
                ],
                "current_step": "program_active"
            }
        else:
            return {
                **state,
                "messages": state["messages"] + [AIMessage(content="No active program found. Returning to main menu.")],
                "current_step": "await_program_"
            }
    
    # Keep existing chat handling logic
    return state



def handle_custom_help(state: AgentState):
    """
    Handle user input when they select 'Something else' and specify their needs.
    """
    # Get the last 5 messages for context
    history = "\n".join(
        [f"{'User' if isinstance(m, HumanMessage) else 'Bot'}: {m.content}" 
         for m in state["messages"][-5:]]
    )
    
    last_input = next(
        (msg.content for msg in reversed(state["messages"]) if isinstance(msg, HumanMessage)),
        ""
    ).strip()

    # Generate a conversational response based on user input and history
    prompt = f"""Conversation Context:{history}

    Current User Message: {last_input}

    Provide spiritual guidance that:
    - References previous discussions if relevant
    - Addresses the current concern
    - Offers practical steps and scripture
    - Asks follow-up questions"""

    response = llm.invoke(prompt).content
    state["messages"].append(AIMessage(content=response))
    state["messages"].append(AIMessage(content="Would you like to explore this further?"))
    return {**state, "current_step": "await_custom_help_response"}


def handle_program_interest(state: AgentState):
    last_input = next(
        (msg.content.lower() for msg in reversed(state["messages"]) if isinstance(msg, HumanMessage)),
        ""
    ).strip()

    if last_input == "yes":
        state["messages"].append(AIMessage(content="Choose program length (7/14/30 days):"))
        return {**state, "current_step": "await_program_length"}

    elif last_input == "no":
        state["messages"].append(AIMessage(content="What else can I help you with?"))
        return {**state, "current_step": "await_just_chat"}
    
    # Check if the user wants to see options again  
    if "options" in last_input or "what are the five options" in last_input:
        state["messages"].append(AIMessage(content="Here are the five options:\n"
                                                   "1. Daily Devotion\n"
                                                   "2. Daily Prayer\n"
                                                   "3. Daily Meditation\n"
                                                   "4. Daily Accountability\n"
                                                   "5. Just Chat"))
        return {**state, "current_step": "await_selection"}
    
    # Check if the user wants to see the main menu
    if "main menu" in last_input or "return to main menu" in last_input:
        state["messages"].append(AIMessage(content="Here are the five options:\n"
                                                   "1. Daily Devotion\n"
                                                   "2. Daily Prayer\n"
                                                   "3. Daily Meditation\n"
                                                   "4. Daily Accountability\n"
                                                   "5. Just Chat"))
        return {**state, "current_step": "await_selection"}

    
    state["messages"].append(AIMessage(content="Returning to main menu..."))
    return {**state, "current_step": "initial_selection"}


def handle_program_length(state: AgentState):
    last_input = next(
        (msg.content for msg in reversed(state["messages"]) 
         if isinstance(msg, HumanMessage)),
        ""
    ).strip()

    if last_input in ["7", "14", "30"]:
        program = {
            "topic": state["current_topic"],
            "length": int(last_input),
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "progress": 0
        }
        
        state["active_program"] = program
        program_content = generate_program(program['topic'], int(last_input))
        
        # Add program content and check-in prompt
        state["messages"].append(AIMessage(
            content=f"""🎉 Program Started!
            Topic: {program['topic']}
            Duration: {last_input} days
            {program_content}"""
        ))
        
        # Add Daily Check-In message
        state["messages"].append(AIMessage(
            content="""Daily Program Check-In:
                1. Mark today as complete   
                2. View progress
                3. Exit program"""
        ))
        
        return {**state, "current_step": "program_active"}
    
    # Handle invalid input for program length
    state["messages"].append(AIMessage(content="Invalid input. Please choose 7/14/30"))
    return {**state, "current_step": "await_program_length"}



def final_response(state: AgentState):
    last_input = next(
        (msg.content.lower() for msg in reversed(state["messages"]) if isinstance(msg, HumanMessage)),
        ""
    )
    
    if last_input == "yes":
        # Keep conversation history for continuity
        state["messages"].append(AIMessage(
            content="What else can I help you with today?"
        ))
        return {**state, "current_step": "initial_selection"}
    
    state["messages"].append(AIMessage(
        content="God bless you! Our conversation history will be saved until you restart."
    ))
    return {**state, "current_step": "end"}


def classify_user_intent(user_input: str) -> str:
    """
    Classify user input into therapy-focused intents.
    """
    prompt = f"""
    Analyze this mental health-related input and classify into:
    - "stress_management" (e.g., "stress", "overwhelmed", "pressure")
    - "emotional_regulation" (e.g., "angry", "sad", "anxious")
    - "mindfulness" (e.g., "meditate", "grounding", "present moment")
    - "coping_strategies" (e.g., "cope", "deal with", "handle challenges")
    - "program_check_in" (e.g., "check progress", "daily update")
    - "exit_program" (e.g., "stop program", "pause tracking")
    - "main_menu" (e.g., "start over", "main options")
    - "just_chat" (e.g., "talk", "need to vent")
    - "crisis" (e.g., "emergency", "urgent help", "suicidal")
    - "invalid" for unclear inputs

    User Input: "{user_input}"
    Return ONLY the matching intent name from above.
    """
    
    try:
        intent = llm.invoke(prompt).content.strip().lower()
        # Normalize potential variations
        intent = intent.replace(" ", "_").split("_")[0]
        return intent if intent in [
            "stress_management", "emotional_regulation", "mindfulness",
            "coping_strategies", "program_check_in", "exit_program",
            "main_menu", "just_chat", "crisis", "invalid"
        ] else "invalid"
    except Exception as e:
        print(f"Error classifying intent: {e}")
        return "invalid" if "crisis" not in user_input.lower() else "crisis"

    

def handle_progress(state: AgentState, user_input: str) -> AgentState:
    """
    Handle progress updates and daily check-in logic for active programs.
    """
    check_in_message = """Daily Program Check-In:
1. Mark today as complete   
2. View progress
3. Exit program"""

    # Add check-in message if missing
    if not any(msg.content == check_in_message for msg in state["messages"]):
        state["messages"].append(AIMessage(content=check_in_message))

    if not state.get("active_program"):
        state["messages"].append(AIMessage(content="No active program found. Returning to the main menu."))
        state["current_step"] = "initial_selection"
        return state

    if user_input == "1":  # Mark today as complete
        state["active_program"]["progress"] += 1
        progress = state["active_program"]["progress"]
        length = state["active_program"]["length"]
        if progress >= length:
            state["messages"].append(AIMessage(content="🎉 Program completed! Returning to main menu."))
            state["current_step"] = "initial_selection"
            state["active_program"] = None
        else:
            state["messages"].append(AIMessage(content=f"Progress updated! Day {progress}/{length}."))
            state["current_step"] = "program_active"

    elif user_input == "2":  # View progress
        topic = state["active_program"]["topic"]
        progress = state["active_program"]["progress"]
        length = state["active_program"]["length"]
        state["messages"].append(AIMessage(content=f"Program: {topic}\nProgress: Day {progress}/{length}."))
        state["current_step"] = "program_active"

    elif user_input == "3":  # Exit program
        state["messages"].append(AIMessage(content="Program paused. You can resume later using 'resume program'."))
        state["current_step"] = "await_just_chat"

    else:  # Invalid input
        state["messages"].append(AIMessage(content="Invalid choice. Please select 1, 2, or 3."))

    return state


def safe_state_transition(new_state: AgentState | None) -> AgentState:
    """Ensure state is never None"""
    if new_state is None:
        return {
            "messages": [],
            "current_step": "initial_selection",
            "current_topic": "",
            "active_program": None,
            "last_motivation_date": ""
        }
    return new_state



if __name__ == "__main__":

    state = {
        "messages": [],
        "current_step": "initial_selection",
        "current_topic": "",
        "active_program": None,
        "last_motivation_date": ""
    }


    displayed_messages = set()

    while True:
        
        state = safe_state_transition(state)  # Ensure valid state
    
        print(f"DEBUG: Current step is {state['current_step']}")  # Debugging the flow

        if state["current_step"] == "initial_selection":
            state = initial_selection(state)

        # Print AI messages that haven't been displayed yet
        for msg in state["messages"]:
            if isinstance(msg, AIMessage) and msg.content not in displayed_messages:
                print("\n" + "=" * 50)
                print(msg.content)
                displayed_messages.add(msg.content)  # Mark as displayed

        # Handle user input based on current step
        if state["current_step"] in ["await_selection", "final_response"]:
            user_input = input("\nYour response: ").strip()
            if not user_input:
                state["messages"].append(AIMessage(content="Input cannot be empty. Please try again."))
                continue
            state["messages"].append(HumanMessage(content=user_input))
            state = handle_selection(state) if state["current_step"] == "await_selection" else final_response(state)


        elif state["current_step"] == "await_stress_management_topic":  
            user_input = input("\nYour response: ")
            state["messages"].append(HumanMessage(content=user_input))
            state = handle_stress_topic_selection(state) 
        
        elif state["current_step"] == "await_emotional_regulation_topic":
            user_input = input("\nYour response: ")
            state["messages"].append(HumanMessage(content=user_input))
            state = handle_emotional_regulation_topic_selection(state)

        elif state["current_step"] == "await_mindfulness_topic":
            user_input = input("\nYour response: ")
            state["messages"].append(HumanMessage(content=user_input))
            state = handle_mindfulness_topic_selection(state)    
            
        elif state["current_step"] == "await_coping_strategy_topic":
            user_input = input("\nYour response: ")
            state["messages"].append(HumanMessage(content=user_input))
            state = handle_coping_topic_selection(state)


        elif state["current_step"] == "await_just_chat":
            user_input = input("\nYour response: ")
            state = safe_state_transition(handle_just_chat({
                **state,
                "messages": state["messages"] + [HumanMessage(content=user_input)]
            }))

        elif state["current_step"] == "await_custom_help":
            user_input = input("\nYour response: ")
            state["messages"].append(HumanMessage(content=user_input))
            state = handle_custom_help(state)

        elif state["current_step"] == "await_custom_help_response":
            user_input = input("\nYour response: ")
            if user_input.lower() == "no":
                state["messages"].append(AIMessage(content="God bless you! Type anything to restart."))
                state = {"messages": [], "current_step": "end"}
            else:
                state["messages"].append(AIMessage(content="What else can I help you with?"))
                state["current_step"] = "await_custom_help"

        elif state["current_step"] == "await_program_interest": 
            user_input = input("\nYour response: ")
            state["messages"].append(HumanMessage(content=user_input))
            state = handle_program_interest(state)
        
        elif state["current_step"] == "await_program_length":
            user_input = input("\nYour response: ")
            state["messages"].append(HumanMessage(content=user_input))
            state = handle_program_length(state)

        elif state["current_step"] == "program_active":
            user_input = input("\nYour response: ").strip()
            state["messages"].append(HumanMessage(content=user_input))
            state = handle_progress(state, user_input)

        
        intent = classify_user_intent(user_input)
        
        if intent == "stress_management":
            state = stress_management_topic_selection(state)
        elif intent == "emotional_regulation":
            state = emotional_regulation_topic_selection(state)
        elif intent == "mindfulness":
            state = mindfulness_topic_selection(state)
        elif intent == "coping_strategies":
            state = coping_strategy_topic_selection(state)
        elif intent == "program_check_in":
            state["messages"].append(AIMessage(content="""Daily Program Check-In:
                    1. Mark today as complete   
                    2. View progress
                    3. Exit program"""))
            state["current_step"] = "program_active"
        elif intent == "just_chat":
            state["messages"].append(AIMessage(content="Let's chat! How can I support you today?"))
            state["current_step"] = "await_just_chat"
        elif intent == "view_progress":
            if state.get("active_program"):
                progress = state["active_program"]["progress"]
                length = state["active_program"]["length"]
                state["messages"].append(AIMessage(
                    content=f"Program: {state['active_program']['topic']}\nProgress: Day {progress}/{length}"
                ))
            else:
                state["messages"].append(AIMessage(content="No active program found."))
        elif intent == "exit_program":
            state["messages"].append(AIMessage(content="Program paused. You can resume later using 'resume program'."))
            state["current_step"] = "initial_selection"
        elif intent == "main_menu":
            state = initial_selection(state)
        
    

