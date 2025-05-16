from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from models import db, ConstructionMachine, User, SurveyingTool
from datetime import datetime
import os
print(os.path.abspath("equipment.db"))

app = Flask(__name__)

# アプリ設定
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///equipment.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your_secret_key"

# DB初期化とマイグレーション
db.init_app(app)
migrate = Migrate(app, db)

# LoginManager設定
login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ログイン処理
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        flash('ログインに失敗しました')
    return render_template('login.html')

# トップページ
@app.route('/')
@login_required
def index():
    return render_template('index.html')

# ログアウト処理
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# 機械一覧ページ
@app.route('/machine_list')
@login_required
def machine_list():
    type_param = request.args.get('type')
    machines = []

    if type_param == 'construction':
        machines = ConstructionMachine.query.order_by(
            ConstructionMachine.name.asc(),
            ConstructionMachine.serial_number.asc()
        ).all()

    return render_template('machine_list.html', type=type_param, machines=machines)

# 測量器一覧ページ
@app.route('/surveying_list')
@login_required
def surveying_list():
    surveying_tools = SurveyingTool.query.order_by(
        SurveyingTool.tool_type.asc(),     # 種類で昇順（存在すれば）
        SurveyingTool.name.asc(),          # 名前で昇順
        SurveyingTool.serial_number.asc()  # 管理番号で昇順
    ).all()
    return render_template('surveying_list.html', surveying_tools=surveying_tools)

# 建設機械の新規登録
@app.route('/construction_machines/add', methods=['GET', 'POST'])
@login_required
def add_construction_machine():
    if request.method == 'POST':
        # フォーム値取得
        machine_type = request.form.get('machine_type', '').strip()
        manufacturer = request.form.get('manufacturer', '').strip()
        rental_number = request.form.get('rental_number', '').strip()
        location = request.form.get('location', '').strip()

        # 必須チェックやバリデーションがあればここで追加

        new_machine = ConstructionMachine(
            name=machine_type,
            manufacturer=manufacturer,
            serial_number=rental_number,
            location=location,
            is_active=True
        )

        try:
            db.session.add(new_machine)
            db.session.commit()
            flash('建設機械を登録しました。')
            return redirect(url_for('machine_list', type='construction'))
        except Exception as e:
            db.session.rollback()
            flash(f'エラーが発生しました: {str(e)}')

    return render_template('add_construction_machine.html')

# 測量器新規登録
@app.route('/add_surveying_tool', methods=['GET', 'POST'])
@login_required
def add_surveying_tool():
    if request.method == 'POST':
        tool_type = request.form.get('tool_type', '').strip()
        tool_name = request.form.get('tool_name', '').strip()
        manufacturer = request.form.get('manufacturer', '').strip()
        management_number = request.form.get('management_number', '').strip()
        inspection_date_str = request.form.get('inspection_date', '').strip()
        state_str = request.form.get('state', '').strip()
        shipment_location = request.form.get('shipment_location', '').strip()
        shipment_site = request.form.get('shipment_site', '').strip()
        start_date_str = request.form.get('start_date', '').strip()
        end_date_str = request.form.get('end_date', '').strip()

        try:
            inspection_date = datetime.strptime(inspection_date_str, '%Y-%m-%d').date() if inspection_date_str else None
            shipment_start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
            shipment_end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
        except ValueError:
            flash('日付の形式が正しくありません。')
            return redirect(url_for('add_surveying_tool'))

        is_active = True if state_str == 'True' else False

        new_tool = SurveyingTool(
            name=tool_name,
            manufacturer=manufacturer,
            serial_number=management_number,
            inspection_date=inspection_date,
            is_active=is_active,
            shipment_location=shipment_location,
            shipment_site=shipment_site,
            shipment_start_date=shipment_start_date,
            shipment_end_date=shipment_end_date,
            tool_type=tool_type 
        )

        try:
            db.session.add(new_tool)
            db.session.commit()
            flash('測量器を登録しました。')
            return redirect(url_for('surveying_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'登録中にエラーが発生しました: {str(e)}')

    return render_template('add_surveying_tool.html')

# 状態切替（アクティブ・非アクティブ）
@app.route('/machine/<int:machine_id>/toggle', methods=['POST'])
@login_required
def toggle_active(machine_id):
    machine = ConstructionMachine.query.get_or_404(machine_id)
    machine.is_active = not machine.is_active
    db.session.commit()
    flash('状態が変更されました。')
    return redirect(url_for('machine_list', type='construction'))

@app.route('/toggle_surveying_active/<int:tool_id>', methods=['POST'])
@login_required
def toggle_surveying_active(tool_id):
    tool = SurveyingTool.query.get_or_404(tool_id)
    tool.is_active = not tool.is_active
    db.session.commit()
    flash('測量器の状態を変更しました。')
    return redirect(url_for('surveying_list'))

# 機械削除
@app.route('/machine/<int:machine_id>/delete', methods=['POST'])
@login_required
def delete_machine(machine_id):
    machine = ConstructionMachine.query.get_or_404(machine_id)
    try:
        db.session.delete(machine)
        db.session.commit()
        flash('機械を削除しました。')
    except Exception as e:
        db.session.rollback()
        flash(f'削除中にエラーが発生しました: {str(e)}')
    return redirect(url_for('machine_list', type='construction'))

# 場所変更
@app.route('/update_location/<int:machine_id>', methods=['POST'])
@login_required
def update_location(machine_id):
    new_location = request.form.get('location', '').strip()
    machine = ConstructionMachine.query.get_or_404(machine_id)
    try:
        machine.location = new_location
        db.session.commit()
        flash('場所が変更されました。')
    except Exception as e:
        db.session.rollback()
        flash(f'場所の更新中にエラーが発生しました: {str(e)}')
    return redirect(url_for('machine_list', type='construction'))

# 出庫先詳細更新
@app.route('/update_shipment_location/<int:machine_id>', methods=['POST'])
@login_required
def update_shipment_location(machine_id):
    machine = ConstructionMachine.query.get_or_404(machine_id)

    def to_none(value):
        return value.strip() if value and value.strip() else None

    company_name = to_none(request.form.get('company_name', ''))
    shipment_site = to_none(request.form.get('shipment_site', ''))
    start_date_str = request.form.get('start_date', '')
    end_date_str = request.form.get('end_date', '')

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None

        machine.shipment_location = company_name
        machine.shipment_site = shipment_site
        machine.shipment_start_date = start_date
        machine.shipment_end_date = end_date

        db.session.commit()
        flash('出庫先情報を更新しました。')
    except Exception as e:
        db.session.rollback()
        flash(f'出庫先更新中にエラーが発生しました: {str(e)}')

    return redirect(url_for('machine_list', type='construction'))

# 測量器：出庫先詳細更新
@app.route('/update_surveying_shipment_location/<int:tool_id>', methods=['POST'])
@login_required
def update_surveying_shipment_location(tool_id):
    tool = SurveyingTool.query.get_or_404(tool_id)

    def to_none(value):
        return value.strip() if value and value.strip() else None

    company_name = to_none(request.form.get('company_name', ''))
    shipment_site = to_none(request.form.get('shipment_site', ''))
    start_date_str = request.form.get('start_date', '')
    end_date_str = request.form.get('end_date', '')

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None

        tool.shipment_location = company_name
        tool.shipment_site = shipment_site
        tool.shipment_start_date = start_date
        tool.shipment_end_date = end_date

        db.session.commit()
        flash('測量器の出庫先情報を更新しました。')
    except Exception as e:
        db.session.rollback()
        flash(f'測量器の出庫先更新中にエラーが発生しました: {str(e)}')

    return redirect(url_for('surveying_list'))

# 測量器：点検日の更新
@app.route('/change_surveying_inspection/<int:tool_id>', methods=['POST'])
def change_surveying_inspection(tool_id):
    tool = SurveyingTool.query.get_or_404(tool_id)
    inspection_date_str = request.form.get('inspection_date')
    if inspection_date_str:
        tool.inspection_date = datetime.strptime(inspection_date_str, '%Y-%m-%d').date()
        db.session.commit()
    return redirect(url_for('surveying_list'))


# 測量器：削除
@app.route('/delete_surveying_tool/<int:tool_id>', methods=['POST'])
@login_required
def delete_surveying_tool(tool_id):
    tool = SurveyingTool.query.get_or_404(tool_id)

    try:
        db.session.delete(tool)
        db.session.commit()
        flash('測量器を削除しました。')
    except Exception as e:
        db.session.rollback()
        flash(f'削除中にエラーが発生しました: {str(e)}')

    return redirect(url_for('surveying_list'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # adminユーザー初期作成
        if not User.query.filter_by(username='admin').first():
            user = User(username='admin')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()

    app.run(debug=True)
