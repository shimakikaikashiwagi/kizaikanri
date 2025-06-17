from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# Userモデル
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        """パスワードをハッシュ化して保存する"""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """入力されたパスワードが正しいか確認する"""
        return check_password_hash(self.password, password)


from datetime import datetime

class ConstructionMachine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    manufacturer = db.Column(db.String(100), nullable=True)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    location = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    state = db.Column(db.String(20), nullable=True)
    image_path = db.Column(db.String(200), nullable=True)
    shipment_location = db.Column(db.String(100), nullable=True)
    shipment_site = db.Column(db.String(100))
    shipment_start_date = db.Column(db.Date)
    shipment_end_date = db.Column(db.Date)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # ← 追加！

    def __repr__(self):
        return f'<ConstructionMachine {self.name}>'

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "manufacturer": self.manufacturer,
            "serial_number": self.serial_number,
            "location": self.location,
            "is_active": self.is_active,
            "state": self.state,
            "image_path": self.image_path,
            "shipment_location": self.shipment_location,
            "shipment_site": self.shipment_site,
            "shipment_start_date": self.shipment_start_date.isoformat() if self.shipment_start_date else None,
            "shipment_end_date": self.shipment_end_date.isoformat() if self.shipment_end_date else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None  # ← 追加！
        }
    
# surveyingToolモデル
class SurveyingTool(db.Model):
    __tablename__ = 'surveying_tools'

    id = db.Column(db.Integer, primary_key=True)
    tool_type = db.Column(db.String(100), nullable=True)
    name = db.Column(db.String(100), nullable=False)              # 機材名
    manufacturer = db.Column(db.String(100), nullable=True)       # メーカー
    serial_number = db.Column(db.String(100), nullable=True)      # 管理番号
    inspection_date = db.Column(db.Date, nullable=True)           # 点検日
    pdf_filename = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=True)  # 状態 (True=未使用、False=出庫中)
    state = db.Column(db.String(50))
    shipment_location = db.Column(db.String(255), nullable=True)   # 出庫先 会社名
    shipment_site = db.Column(db.String(255), nullable=True)       # 出庫現場
    shipment_start_date = db.Column(db.Date, nullable=True)        # 出庫開始期間
    shipment_end_date = db.Column(db.Date, nullable=True)          # 出庫終了期間
    pdf_filename = db.Column(db.String(255), nullable=True)

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


    def __repr__(self):
        return f'<SurveyingTool {self.name} ({self.serial_number})>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "tool_type": self.tool_type,
            "name": self.name,
            "manufacturer": self.manufacturer,
            "serial_number": self.serial_number,
            "inspection_date": self.inspection_date.isoformat() if self.inspection_date else None,
            "is_active": self.is_active,
            "state": self.state,
            'pdf_filename': self.pdf_filename,
            "shipment_location": self.shipment_location,
            "shipment_site": self.shipment_site,
            "shipment_start_date": self.shipment_start_date.isoformat() if self.shipment_start_date else None,
            "shipment_end_date": self.shipment_end_date.isoformat() if self.shipment_end_date else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

# systemToolモデル
class SystemTool(db.Model):
    __tablename__ = 'system_tools'

    id = db.Column(db.Integer, primary_key=True)
    tool_type = db.Column(db.String(100), nullable=True)
    name = db.Column(db.String(100), nullable=False)              # 機材名
    manufacturer = db.Column(db.String(100), nullable=True)       # メーカー
    serial_number = db.Column(db.String(100), nullable=True)      # 管理番号
    is_active = db.Column(db.Boolean, default=True, nullable=True)  # 状態 (True=未使用、False=出庫中)
    state = db.Column(db.String(50))                               # 状態（例：正常、故障など）
    shipment_location = db.Column(db.String(255), nullable=True)   # 出庫先 会社名
    shipment_site = db.Column(db.String(255), nullable=True)       # 出庫現場
    shipment_start_date = db.Column(db.Date, nullable=True)        # 出庫開始期間
    shipment_end_date = db.Column(db.Date, nullable=True)          # 出庫終了期間
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<SystemTool {self.name} ({self.serial_number})>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "tool_type": self.tool_type,
            "name": self.name,
            "manufacturer": self.manufacturer,
            "serial_number": self.serial_number,
            "is_active": self.is_active,
            "state": self.state,
            "shipment_location": self.shipment_location,
            "shipment_site": self.shipment_site,
            "shipment_start_date": self.shipment_start_date.isoformat() if self.shipment_start_date else None,
            "shipment_end_date": self.shipment_end_date.isoformat() if self.shipment_end_date else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
# partsモデル
class Part(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    part_type = db.Column(db.String(120), nullable=True)
    part_name = db.Column(db.String(120), nullable=False)
    manufacturer = db.Column(db.String(120), nullable=True)
    model_number = db.Column(db.String(120), nullable=True)
    new_stock = db.Column(db.Integer, default=0)
    used_stock = db.Column(db.Integer, default=0)  # 追加
    remarks = db.Column(db.String(255), nullable=True)
    is_shipped = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "part_type": self.part_type,
            "part_name": self.part_name,
            "manufacturer": self.manufacturer,
            "model_number": self.model_number,
            "new_stock": self.new_stock,
            "used_stock": self.used_stock,
            "remarks": self.remarks,
            "is_shipped": self.is_shipped,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

# 過去ログ機械モデル
class ShipmentHistory(db.Model):
    __tablename__ = 'shipment_history'

    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('construction_machine.id'), nullable=False)
    shipment_location = db.Column(db.String(255))
    shipment_site = db.Column(db.String(255))
    shipment_start_date = db.Column(db.Date)
    shipment_end_date = db.Column(db.Date)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 関連付け（必要なら）
    machine = db.relationship('ConstructionMachine', backref='shipment_histories')

    def to_dict(self):
        return {
            'id': self.id,
            'machine_id': self.machine_id,
            'shipment_location': self.shipment_location,
            'shipment_site': self.shipment_site,
            'shipment_start_date': self.shipment_start_date.isoformat() if self.shipment_start_date else None,
            'shipment_end_date': self.shipment_end_date.isoformat() if self.shipment_end_date else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

# 過去ログ測量器モデル
class SurveyingShipmentHistory(db.Model):
    __tablename__ = 'surveying_shipment_history'

    id = db.Column(db.Integer, primary_key=True)
    tool_id = db.Column(db.Integer, db.ForeignKey('surveying_tools.id'), nullable=False)
    shipment_location = db.Column(db.String(100))
    shipment_site = db.Column(db.String(100))
    shipment_start_date = db.Column(db.Date)
    shipment_end_date = db.Column(db.Date)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'tool_id': self.tool_id,
            'shipment_location': self.shipment_location,
            'shipment_site': self.shipment_site,
            'shipment_start_date': self.shipment_start_date.isoformat() if self.shipment_start_date else None,
            'shipment_end_date': self.shipment_end_date.isoformat() if self.shipment_end_date else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

# 過去ログシステムモデル
class SystemShipmentHistory(db.Model):
    __tablename__ = 'system_shipment_history'
    id = db.Column(db.Integer, primary_key=True)
    
    system_id = db.Column(db.Integer, db.ForeignKey('system_tools.id'), nullable=False)
    shipment_location = db.Column(db.String(255))
    shipment_site = db.Column(db.String(255))
    shipment_start_date = db.Column(db.Date)
    shipment_end_date = db.Column(db.Date)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 必要に応じてリレーションも設定
    system_tool = db.relationship('SystemTool', backref=db.backref('shipment_histories', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'system_id': self.system_id,
            'shipment_location': self.shipment_location,
            'shipment_site': self.shipment_site,
            'shipment_start_date': self.shipment_start_date.isoformat() if self.shipment_start_date else None,
            'shipment_end_date': self.shipment_end_date.isoformat() if self.shipment_end_date else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
