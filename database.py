from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class FileLog(db.Model):
    __tablename__ = 'file_logs'

    id         = db.Column(db.Integer, primary_key=True)
    filename   = db.Column(db.String(255), nullable=False)
    action     = db.Column(db.String(10), nullable=False)  # 'encrypt' or 'decrypt'
    file_size  = db.Column(db.Integer)                     # bytes
    ip_address = db.Column(db.String(50))
    status     = db.Column(db.String(10), default='success') # 'success' or 'error'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':         self.id,
            'filename':   self.filename,
            'action':     self.action,
            'file_size':  self.file_size,
            'ip_address': self.ip_address,
            'status':     self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }