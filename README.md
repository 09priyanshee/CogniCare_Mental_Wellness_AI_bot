# CogniCare_Mental_Wellness_Chatbot

## *CogniCare: Your Partner in Mental Wellness* 

### Why This Project is Important
Mental health is as vital as physical health, yet many people lack access to daily support and guidance. CogniCare is a therapy chatbot designed to provide empathetic, actionable, and accessible mental health support to anyone, anytime. It helps users manage stress, regulate emotions, practice mindfulness, and build healthy coping strategies—all in a private, judgment-free space.

### Technologies Used
- Python 3
- Flask (for the web server and API)
- LangChain (for conversational state and message management)
- Google Gemini API (for AI-powered empathetic responses)
- HTML/CSS/JavaScript (for the web interface)

VS Code (for development)

### Implementation

- Conversational AI: Uses Google Gemini via LangChain to generate supportive, context-aware responses.
- Stateful Chatbot: Maintains conversation state and user progress using a custom state machine in Python.
- Web Interface: Built with Flask, HTML, CSS, and JavaScript for a responsive, user-friendly experience.
- Therapy Programs: Offers structured programs for stress management, emotional regulation, mindfulness, and coping strategies.
- Daily Motivation: Provides a new motivational message each day to encourage users.

### Directory Explanation
text
/
│
├── app.py                # Flask web server and API endpoints
├── demo.py               # Core chatbot logic and state management
├── static/
│   ├── image/
│   │   └── logo.png      # Project logo for the web interface
│   ├── script.js         # Frontend JavaScript for chat interaction
│   └── style.css         # CSS for styling the web interface
├── templates/
│   └── index.html        # Main HTML template for the chat UI
├── venv/                 # Python virtual environment (not uploaded to GitHub)
├── README.md             # Project documentation (this file)
└── ...                   # Other config and cache files

###Message for Readers
Thank you for checking out CogniCare!
This project is a step toward making mental health support more accessible and stigma-free.
If you find it helpful, consider sharing it with others or contributing to its development.
Remember: You are not alone, and every step toward wellness matters.

Feel free to copy, modify, and use this template for your GitHub repository!
If you need a badge section, installation instructions, or contribution guidelines, let me know!
