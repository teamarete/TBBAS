"""
Database models for TBBAS
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class BoxScore(db.Model):
    """Box score for a game"""
    id = db.Column(db.Integer, primary_key=True)

    # Game info
    game_date = db.Column(db.Date, nullable=False)
    classification = db.Column(db.String(20), nullable=False)

    # Team 1 (Home)
    team1_name = db.Column(db.String(100), nullable=False)
    team1_score = db.Column(db.Integer, nullable=False)
    team1_fg = db.Column(db.Integer)  # Field goals made
    team1_fga = db.Column(db.Integer)  # Field goals attempted
    team1_3pt = db.Column(db.Integer)  # 3-pointers made
    team1_3pta = db.Column(db.Integer)  # 3-pointers attempted
    team1_ft = db.Column(db.Integer)  # Free throws made
    team1_fta = db.Column(db.Integer)  # Free throws attempted
    team1_reb = db.Column(db.Integer)  # Total rebounds
    team1_ast = db.Column(db.Integer)  # Assists
    team1_stl = db.Column(db.Integer)  # Steals
    team1_blk = db.Column(db.Integer)  # Blocks
    team1_to = db.Column(db.Integer)  # Turnovers

    # Team 2 (Away)
    team2_name = db.Column(db.String(100), nullable=False)
    team2_score = db.Column(db.Integer, nullable=False)
    team2_fg = db.Column(db.Integer)
    team2_fga = db.Column(db.Integer)
    team2_3pt = db.Column(db.Integer)
    team2_3pta = db.Column(db.Integer)
    team2_ft = db.Column(db.Integer)
    team2_fta = db.Column(db.Integer)
    team2_reb = db.Column(db.Integer)
    team2_ast = db.Column(db.Integer)
    team2_stl = db.Column(db.Integer)
    team2_blk = db.Column(db.Integer)
    team2_to = db.Column(db.Integer)

    # Metadata
    submitted_by = db.Column(db.String(100))  # Optional coach name/email
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<BoxScore {self.team1_name} {self.team1_score} - {self.team2_score} {self.team2_name}>'

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'game_date': self.game_date.isoformat() if self.game_date else None,
            'classification': self.classification,
            'team1_name': self.team1_name,
            'team1_score': self.team1_score,
            'team1_stats': {
                'fg': f"{self.team1_fg or 0}/{self.team1_fga or 0}",
                '3pt': f"{self.team1_3pt or 0}/{self.team1_3pta or 0}",
                'ft': f"{self.team1_ft or 0}/{self.team1_fta or 0}",
                'reb': self.team1_reb or 0,
                'ast': self.team1_ast or 0,
                'stl': self.team1_stl or 0,
                'blk': self.team1_blk or 0,
                'to': self.team1_to or 0
            },
            'team2_name': self.team2_name,
            'team2_score': self.team2_score,
            'team2_stats': {
                'fg': f"{self.team2_fg or 0}/{self.team2_fga or 0}",
                '3pt': f"{self.team2_3pt or 0}/{self.team2_3pta or 0}",
                'ft': f"{self.team2_ft or 0}/{self.team2_fta or 0}",
                'reb': self.team2_reb or 0,
                'ast': self.team2_ast or 0,
                'stl': self.team2_stl or 0,
                'blk': self.team2_blk or 0,
                'to': self.team2_to or 0
            },
            'submitted_by': self.submitted_by,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None
        }
