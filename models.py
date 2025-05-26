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


# ConstructionMachineモデル
class ConstructionMachine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)           # 機械名
    manufacturer = db.Column(db.String(100), nullable=True)     # メーカー名（任意）
    serial_number = db.Column(db.String(100), unique=True, nullable=False)  # シリアル番号（必須）
    location = db.Column(db.String(100), nullable=True)         # 場所（任意）
    is_active = db.Column(db.Boolean, default=True)  
    state = db.Column(db.String(20), nullable=True)            # 使用中かどうか
    image_path = db.Column(db.String(200), nullable=True)       # 画像ファイルパス（任意）
    shipment_location = db.Column(db.String(100), nullable=True)  # 出庫先（新たに追加）
    shipment_site = db.Column(db.String(100))  
    shipment_start_date = db.Column(db.Date)          # 開始日付
    shipment_end_date = db.Column(db.Date)            # 終了日付

    def __repr__(self):
        return f'<ConstructionMachine {self.name}>'
    
# surveyingToolモデル
class SurveyingTool(db.Model):
    __tablename__ = 'surveying_tools'

    id = db.Column(db.Integer, primary_key=True)
    tool_type = db.Column(db.String(100), nullable=True)
    name = db.Column(db.String(100), nullable=False)              # 機材名
    manufacturer = db.Column(db.String(100), nullable=True)       # メーカー
    serial_number = db.Column(db.String(100), nullable=True)      # 管理番号
    inspection_date = db.Column(db.Date, nullable=True)           # 点検日
    is_active = db.Column(db.Boolean, default=True, nullable=True)  # 状態 (True=未使用、False=出庫中)
    state = db.Column(db.String(50))
    shipment_location = db.Column(db.String(255), nullable=True)   # 出庫先 会社名
    shipment_site = db.Column(db.String(255), nullable=True)       # 出庫現場
    shipment_start_date = db.Column(db.Date, nullable=True)        # 出庫開始期間
    shipment_end_date = db.Column(db.Date, nullable=True)          # 出庫終了期間

    def __repr__(self):
        return f'<SurveyingTool {self.name} ({self.serial_number})>'

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

    def __repr__(self):
        return f'<SystemTool {self.name} ({self.serial_number})>'
    
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
