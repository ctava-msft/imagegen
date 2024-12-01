from flask import Blueprint, jsonify, render_template, request, render_template
from models import Session, Message

app = Blueprint('app', __name__)

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Create a new session
@app.route('/session/create/', methods=['POST'])
def create_session():
    session = Session()
    session.save()
    return render_template('session_detail.html', session_id=session.session_id)


@app.route('/session/<session_id>/', methods=['GET'])
def session_detail(session_id):
    session = Session.query.get(session_id)
    
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    # Get all messages related to this session
    messages = session.messages.all()
    
    return render_template('session_detail.html', session= session,messages= messages,session_id = session_id)

@app.route('/generate_response/<session_id>', methods=['POST'])
def generate_response(session_id):
    data = request.json
    user_input = data.get('user_input')

    message = Message(session_id=session_id, prompt=user_input)
    
    message.generate_completion()

    # Save prompt tokens
    message.prompt_tokens = len(user_input.split())

    message.save()

    return jsonify({'response': message.completion})