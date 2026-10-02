import uuid
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class Session:
    """Represents an ER:LC gaming session"""
    
    def __init__(self, session_id: str, host_id: int, host_name: str, game_type: str, max_players: int = 6):
        self.id = session_id
        self.host_id = host_id
        self.host_name = host_name
        self.game_type = game_type
        self.max_players = max_players
        self.players = [host_id]  # Host is the first player
        self.status = "🟢 Active"
        self.created_at = datetime.now()
        self.started_at = None
        self.ended_at = None
    
    def add_player(self, player_id: int, player_name: str) -> bool:
        """Add a player to the session"""
        if len(self.players) >= self.max_players:
            return False
        if player_id in self.players:
            return False
        self.players.append(player_id)
        return True
    
    def remove_player(self, player_id: int) -> bool:
        """Remove a player from the session"""
        if player_id not in self.players:
            return False
        self.players.remove(player_id)
        
        # If host leaves, end the session
        if player_id == self.host_id:
            self.end_session()
        
        return True
    
    def start_session(self):
        """Mark session as started"""
        self.started_at = datetime.now()
        self.status = "🔴 In Progress"
    
    def end_session(self):
        """End the session"""
        self.ended_at = datetime.now()
        self.status = "⚫ Ended"
    
    def get_info(self) -> Dict:
        """Get session information"""
        return {
            'id': self.id,
            'host_id': self.host_id,
            'host_name': self.host_name,
            'game_type': self.game_type,
            'max_players': self.max_players,
            'current_players': len(self.players),
            'players': self.players,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
        }


class SessionManager:
    """Manages all gaming sessions"""
    
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        self.player_sessions: Dict[int, str] = {}  # Track which session each player is in
    
    def create_session(self, host_id: int, host_name: str, game_type: str, max_players: int = 6) -> Dict:
        """Create a new session"""
        session_id = str(uuid.uuid4())[:8]  # Generate short session ID
        
        # Check if host already in a session
        if host_id in self.player_sessions:
            raise ValueError("Player is already in an active session")
        
        session = Session(session_id, host_id, host_name, game_type, max_players)
        self.sessions[session_id] = session
        self.player_sessions[host_id] = session_id
        
        return session.get_info()
    
    def join_session(self, session_id: str, player_id: int, player_name: str) -> Tuple[bool, str]:
        """Join an existing session"""
        
        # Check if player already in a session
        if player_id in self.player_sessions:
            return False, "You are already in an active session"
        
        # Check if session exists
        if session_id not in self.sessions:
            return False, f"Session {session_id} not found"
        
        session = self.sessions[session_id]
        
        # Check if session is full
        if len(session.players) >= session.max_players:
            return False, "Session is full"
        
        # Add player to session
        if session.add_player(player_id, player_name):
            self.player_sessions[player_id] = session_id
            return True, f"Joined session {session_id}!"
        else:
            return False, "Could not join session"
    
    def leave_session(self, player_id: int) -> Tuple[bool, str]:
        """Leave current session"""
        
        if player_id not in self.player_sessions:
            return False, "You are not in any session"
        
        session_id = self.player_sessions[player_id]
        session = self.sessions[session_id]
        
        session.remove_player(player_id)
        del self.player_sessions[player_id]
        
        # Clean up ended sessions
        if session.status == "⚫ Ended":
            del self.sessions[session_id]
        
        return True, f"Left session {session_id}"
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session information"""
        if session_id not in self.sessions:
            return None
        return self.sessions[session_id].get_info()
    
    def get_active_sessions(self) -> List[Dict]:
        """Get all active sessions"""
        active = []
        for session in self.sessions.values():
            if session.status != "⚫ Ended":
                active.append(session.get_info())
        return active
    
    def get_player_session(self, player_id: int) -> Optional[Dict]:
        """Get the session a player is currently in"""
        if player_id not in self.player_sessions:
            return None
        session_id = self.player_sessions[player_id]
        return self.get_session(session_id)
    
    def start_session(self, session_id: str) -> bool:
        """Start a session"""
        if session_id not in self.sessions:
            return False
        self.sessions[session_id].start_session()
        return True
    
    def end_session(self, session_id: str) -> bool:
        """End a session"""
        if session_id not in self.sessions:
            return False
        self.sessions[session_id].end_session()
        return True
