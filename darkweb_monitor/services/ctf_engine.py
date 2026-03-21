import os
import json
import hashlib
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
from firebase_admin import firestore

@dataclass
class ProChallenge:
    id: int
    title: str
    type: str
    difficulty: str
    points: int
    prerequisite_id: Optional[int]
    scenario: str
    objective: str
    flag_hash: str
    hints: List[str]
    solution: str
    asset_path: Optional[str] = None

class CTFPlatformEngine:
    """Professional CTF Engine with Firestore-backed dynamic loading."""
    
    def __init__(self, db: Any = None, challenges_path: str = "ctf/challenges.json"):
        self._db = db
        self.challenges_path = challenges_path
        self.challenges: List[ProChallenge] = []
        if self.db:
            self._load_challenges()

    @property
    def db(self):
        """Lazy database connection."""
        if self._db is None:
            try:
                self._db = firestore.client()
                # If challenges weren't loaded because db was missing, load them now
                if not self.challenges:
                    self._load_challenges()
            except Exception as e:
                print(f"[CTF] Failed to connect to Firestore: {e}")
                return None
        return self._db

    def _load_challenges(self):
        """Load challenges primarily from Firestore, falling back to JSON then syncing."""
        try:
            if not self.db:
                print("[CTF] Loader deferred: DB connection not established yet.")
                return

            # 1. Try loading from Firestore
            docs = self.db.collection('ctf_challenges').order_by('id').stream()
            db_challenges = []
            for doc in docs:
                db_challenges.append(ProChallenge(**doc.to_dict()))
            
            if db_challenges:
                self.challenges = db_challenges
                print(f"[CTF] Loaded {len(self.challenges)} challenges from Firestore.")
                return

            # 2. If Firestore is empty, load from JSON and sync
            if os.path.exists(self.challenges_path):
                with open(self.challenges_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    json_challenges = [ProChallenge(**c) for c in data.get('challenges', [])]
                    
                    if json_challenges:
                        self.challenges = json_challenges
                        self.sync_challenges_to_db()
                        print(f"[CTF] Seeded {len(self.challenges)} challenges from JSON to Firestore.")
            else:
                print(f"[CTF] Error: No challenges found in Firestore or JSON ({self.challenges_path})")
                
        except Exception as e:
            print(f"[CTF] Critical Error in challenge loader: {e}")

    def sync_challenges_to_db(self):
        """Sync current challenge list to Firestore."""
        batch = self.db.batch()
        for challenge in self.challenges:
            doc_ref = self.db.collection('ctf_challenges').document(str(challenge.id))
            batch.set(doc_ref, asdict(challenge))
        batch.commit()

    def get_challenge(self, challenge_id: int) -> Optional[ProChallenge]:
        for c in self.challenges:
            if c.id == challenge_id:
                return c
        return None

    def validate_flag(self, challenge_id: int, submitted_flag: str) -> bool:
        """Securely validate a flag using SHA-256 hashing."""
        challenge = self.get_challenge(challenge_id)
        if not challenge:
            return False
        
        submitted_hash = hashlib.sha256(submitted_flag.strip().encode()).hexdigest()
        return challenge.flag_hash == submitted_hash

    def is_unlocked(self, user_id: str, challenge_id: int) -> bool:
        """Check if a challenge is unlocked based on prerequisites."""
        if not self.challenges:
            self._load_challenges()
            
        challenge = self.get_challenge(challenge_id)
        if not challenge:
            return False
            
        if challenge.prerequisite_id is None:
            return True
            
        # Check if prerequisite is solved in Firestore
        if not self.db:
            return False

        user_ref = self.db.collection('ctf_users').document(user_id)
        doc = user_ref.get()
        if not doc.exists:
            return False
            
        solved_ids = doc.to_dict().get('solved_challenges', [])
        return challenge.prerequisite_id in solved_ids

    def record_solve(self, user_id: str, username: str, challenge_id: int) -> Dict[str, Any]:
        """Record a successful solve in Firestore and update leaderboard."""
        if not self.db:
            return {'success': False, 'error': 'Database connection lost.'}

        challenge = self.get_challenge(challenge_id)
        if not challenge:
            return {'success': False, 'error': 'Challenge not found'}

        user_ref = self.db.collection('ctf_users').document(user_id)
        
        @firestore.transactional
        def update_in_transaction(transaction, user_ref):
            snapshot = user_ref.get(transaction=transaction)
            
            if snapshot.exists:
                data = snapshot.to_dict()
                solved = data.get('solved_challenges', [])
                if challenge_id in solved:
                    return {'success': True, 'new_solve': False}
                
                new_solved = solved + [challenge_id]
                new_points = data.get('points', 0) + challenge.points
                
                transaction.update(user_ref, {
                    'solved_challenges': new_solved,
                    'points': new_points,
                    'last_solve_time': datetime.now(),
                    'username': username
                })
            else:
                transaction.set(user_ref, {
                    'username': username,
                    'points': challenge.points,
                    'solved_challenges': [challenge_id],
                    'last_solve_time': datetime.now(),
                    'created_at': datetime.now()
                })
            
            return {'success': True, 'new_solve': True}

        return update_in_transaction(self.db.transaction(), user_ref)

    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch the top agents from Firestore."""
        if not self.db:
            return []

        docs = self.db.collection('ctf_users') \
            .order_by('points', direction=firestore.Query.DESCENDING) \
            .order_by('last_solve_time', direction=firestore.Query.ASCENDING) \
            .limit(limit) \
            .stream()
            
        return [doc.to_dict() for doc in docs]

    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get progress stats for a specific user."""
        if not self.db:
            return {'points': 0, 'solved_challenges': []}

        doc = self.db.collection('ctf_users').document(user_id).get()
        if doc.exists:
            return doc.to_dict()
        return {'points': 0, 'solved_challenges': []}
