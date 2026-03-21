from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from services.ctf_engine import CTFPlatformEngine
from firebase_admin import firestore
import os

ctf_bp = Blueprint('ctf', __name__)

# Initialize engine with Firestore
# We get the client directly from firebase_admin which is initialized in app.py
def get_db():
    try:
        return firestore.client()
    except Exception:
        # Fallback for standalone modular app testing if needed
        return None

ctf_engine = CTFPlatformEngine(get_db())

def get_current_user():
    """Helper to get user info from session."""
    user_id = session.get('user_id')
    if not user_id:
        # For demo/guest users without login, use session id as fallback
        if 'guest_id' not in session:
            import uuid
            session['guest_id'] = f"guest_{uuid.uuid4().hex[:8]}"
        user_id = session['guest_id']
    
    username = session.get('user_name', 'Agent_Unknown')
    if username == 'Agent_Unknown' and 'guest_id' in session:
         username = f"Guest_{session['guest_id'][-4:]}"
         
    return user_id, username

@ctf_bp.route('/')
def dashboard():
    """CTF dashboard with progress tracking and unlock states."""
    user_id, _ = get_current_user()
    user_stats = ctf_engine.get_user_stats(user_id)
    solved_ids = user_stats.get('solved_challenges', [])
    
    # Calculate progress
    total_challenges = len(ctf_engine.challenges)
    solved_count = len(solved_ids)
    progress_percent = int((solved_count / total_challenges) * 100) if total_challenges > 0 else 0
    
    # Check unlock status for all challenges
    challenge_data = []
    for c in ctf_engine.challenges:
        is_unlocked = ctf_engine.is_unlocked(user_id, c.id)
        is_solved = c.id in solved_ids
        challenge_data.append({
            'info': c,
            'is_unlocked': is_unlocked,
            'is_solved': is_solved
        })
        
    return render_template('ctf/dashboard.html', 
                           challenges=challenge_data,
                           progress=progress_percent,
                           points=user_stats.get('points', 0),
                           solved_count=solved_count)

@ctf_bp.route('/challenge/<int:challenge_id>')
def challenge_view(challenge_id):
    """View specific challenge details."""
    user_id, _ = get_current_user()
    challenge = ctf_engine.get_challenge(challenge_id)
    
    if not challenge:
        flash("Intel mission not found.", "danger")
        return redirect(url_for('ctf.dashboard'))
        
    if not ctf_engine.is_unlocked(user_id, challenge_id):
        flash("This mission is still classified. Complete prerequisites to unlock.", "warning")
        return redirect(url_for('ctf.dashboard'))
        
    user_stats = ctf_engine.get_user_stats(user_id)
    is_solved = challenge_id in user_stats.get('solved_challenges', [])
    
    return render_template('ctf/challenge.html', 
                           challenge=challenge, 
                           is_solved=is_solved)

@ctf_bp.route('/leaderboard')
def leaderboard():
    """Global CTF leaderboard."""
    top_agents = ctf_engine.get_leaderboard(limit=20)
    return render_template('ctf/leaderboard.html', agents=top_agents)

@ctf_bp.route('/api/validate', methods=['POST'])
def validate_flag():
    """API endpoint to validate flags and award points."""
    try:
        data = request.get_json()
        challenge_id = int(data.get('challenge_id'))
        flag = data.get('flag', '').strip()
        
        user_id, username = get_current_user()
        
        if not ctf_engine.is_unlocked(user_id, challenge_id):
            return jsonify({'success': False, 'message': 'Mission is still classified.'}), 403
            
        if ctf_engine.validate_flag(challenge_id, flag):
            result = ctf_engine.record_solve(user_id, username, challenge_id)
            challenge = ctf_engine.get_challenge(challenge_id)
            
            return jsonify({
                'success': True,
                'message': 'ACCESS GRANTED. Intel verified.',
                'points_awarded': challenge.points if result.get('new_solve') else 0,
                'solution': challenge.solution,
                'is_repeat': not result.get('new_solve')
            })
        else:
            return jsonify({'success': False, 'message': 'ACCESS DENIED. Invalid flag.'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
