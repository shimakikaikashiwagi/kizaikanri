from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from models import db, ConstructionMachine, User, SurveyingTool, SystemTool, Part
from datetime import datetime
from flask import request, jsonify
from models import ShipmentHistory
from models import SurveyingShipmentHistory
from models import SystemShipmentHistory

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

# システム一覧ページ
@app.route('/system_list')
def system_list():
    system_systems = SystemTool.query.order_by(
        SystemTool.tool_type.asc(),     # 種類で昇順（存在すれば）
        SystemTool.name.asc(),          # 名前で昇順
        SystemTool.serial_number.asc()  # 管理番号で昇順
    ).all()
    return render_template('system_list.html', system_systems=system_systems)

# パーツ一覧ページ
@app.route('/parts_list')
def parts_list():
    parts = Part.query.order_by(Part.id.desc()).all()
    return render_template('parts_list.html', parts=parts)

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
            is_active=True,
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

# システム新規登録
@app.route('/add_system_tool', methods=['GET', 'POST'])
def add_system_tool():
    if request.method == 'POST':
        # フォームからデータを取得
        system_type = request.form.get('system_type')
        system_name = request.form.get('system_name')
        manufacturer = request.form.get('manufacturer')
        serial_number = request.form.get('serial_number')

        # モデルに格納してDBに追加
        new_system = SystemTool(
        tool_type=system_type,
        name=system_name,
        manufacturer=manufacturer,
        serial_number=serial_number,
        is_active=True  # 初期状態は未使用
    )

        db.session.add(new_system)
        db.session.commit()
        flash('システム機器を登録しました。', 'success')
        return redirect(url_for('system_list'))

    return render_template('add_system_tool.html')

# 部品新規登録
@app.route('/add_parts', methods=['GET', 'POST'])
@login_required
def add_parts():
    if request.method == 'POST':
        part_type = request.form.get('part_type', '').strip()
        part_name = request.form.get('part_name', '').strip()
        manufacturer = request.form.get('manufacturer', '').strip()
        model_number = request.form.get('model_number', '').strip()
        new_stock_str = request.form.get('new_stock', '0').strip()
        used_stock_str = request.form.get('used_stock', '0').strip()
        remarks = request.form.get('remarks', '').strip()

        try:
            new_stock = int(new_stock_str)
            used_stock = int(used_stock_str)
            if new_stock < 0 or used_stock < 0:
                raise ValueError("在庫数は0以上で入力してください。")
        except ValueError:
            flash('在庫数の入力に誤りがあります。0以上の整数を入力してください。')
            return redirect(url_for('add_parts'))

        new_part = Part(
            part_type=part_type,
            part_name=part_name,
            manufacturer=manufacturer,
            model_number=model_number,
            new_stock=new_stock,
            used_stock=used_stock,
            remarks=remarks
        )

        try:
            db.session.add(new_part)
            db.session.commit()
            flash('部品を登録しました。')
            return redirect(url_for('parts_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'登録中にエラーが発生しました: {str(e)}')

    return render_template('add_parts.html')


# 状態切替（machine）
@app.route('/machine/<int:machine_id>/toggle', methods=['POST'])
@login_required
def toggle_active(machine_id):
    machine = ConstructionMachine.query.get_or_404(machine_id)
    machine.is_active = not machine.is_active
    db.session.commit()
    flash('状態が変更されました。')
    return redirect(url_for('machine_list', type='construction'))

# 状態切替（surveying）
@app.route('/toggle_surveying_active/<int:tool_id>/toggle', methods=['POST'])
@login_required
def toggle_surveying_active(tool_id):
    tool = SurveyingTool.query.get_or_404(tool_id)
    tool.is_active = not tool.is_active
    db.session.commit()
    flash('測量器の状態を変更しました。')
    return redirect(url_for('surveying_list'))

# 機械削除（machine）
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

# 測量器削除
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

# システム削除
@app.route('/delete_system_tool/<int:system_id>', methods=['POST'])
@login_required
def delete_system_tool(system_id):
    system_tool = SystemTool.query.get_or_404(system_id)
    try:
        db.session.delete(system_tool)
        db.session.commit()
        flash('システム機器を削除しました。', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'削除中にエラーが発生しました: {str(e)}', 'danger')
    return redirect(url_for('system_list'))

# 部品削除
@app.route('/delete_part/<int:part_id>', methods=['POST'])
@login_required
def delete_part(part_id):
    part = Part.query.get_or_404(part_id)
    try:
        db.session.delete(part)
        db.session.commit()
        flash('部品を削除しました。', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'削除中にエラーが発生しました: {str(e)}', 'danger')
    return redirect(url_for('parts_list'))

# 機械出庫先詳細更新
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

        # ShipmentHistoryに履歴追加
        history = ShipmentHistory(
            machine_id=machine_id,
            shipment_location=company_name,
            shipment_site=shipment_site,
            shipment_start_date=start_date,
            shipment_end_date=end_date,
        )
        db.session.add(history)

        db.session.commit()
        flash('出庫先情報を更新しました。')
    except Exception as e:
        db.session.rollback()
        flash(f'出庫先更新中にエラーが発生しました: {str(e)}')

    return redirect(url_for('machine_list', type='construction'))

# 測量器の出庫先詳細更新
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

        # メインの出庫先情報更新
        tool.shipment_location = company_name
        tool.shipment_site = shipment_site
        tool.shipment_start_date = start_date
        tool.shipment_end_date = end_date

        # 履歴テーブルに履歴追加
        history = SurveyingShipmentHistory(
            tool_id=tool_id,
            shipment_location=company_name,
            shipment_site=shipment_site,
            shipment_start_date=start_date,
            shipment_end_date=end_date,
        )
        db.session.add(history)

        db.session.commit()
        flash('測量器の出庫先情報を更新しました。')
    except Exception as e:
        db.session.rollback()
        flash(f'測量器の出庫先更新中にエラーが発生しました: {str(e)}')

    return redirect(url_for('surveying_list'))

# システム機器の出庫先詳細更新
@app.route('/update_system_shipment_location/<int:system_id>', methods=['POST'])
@login_required
def update_system_shipment_location(system_id):
    tool = SystemTool.query.get_or_404(system_id)

    def to_none(value):
        return value.strip() if value and value.strip() else None

    company_name = to_none(request.form.get('company_name', ''))
    shipment_site = to_none(request.form.get('shipment_site', ''))
    start_date_str = request.form.get('start_date', '')
    end_date_str = request.form.get('end_date', '')

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None

        # 出庫先情報を SystemTool に更新
        tool.shipment_location = company_name
        tool.shipment_site = shipment_site
        tool.shipment_start_date = start_date
        tool.shipment_end_date = end_date

        # 履歴追加（SystemShipmentHistoryに保存）
        history = SystemShipmentHistory(
            system_id=system_id,
            shipment_location=company_name,
            shipment_site=shipment_site,
            shipment_start_date=start_date,
            shipment_end_date=end_date,
        )
        db.session.add(history)

        db.session.commit()
        flash('システム機器の出庫先情報を更新しました。', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'システム機器の出庫先更新中にエラーが発生しました: {str(e)}', 'danger')

    return redirect(url_for('system_list'))

# 測量器の点検日変更
@app.route('/change_surveying_inspection/<int:tool_id>', methods=['POST'])
def change_surveying_inspection(tool_id):
    tool = SurveyingTool.query.get_or_404(tool_id)
    inspection_date_str = request.form.get('inspection_date')

    if inspection_date_str:
        tool.inspection_date = datetime.strptime(inspection_date_str, '%Y-%m-%d').date()
    else:
        tool.inspection_date = None  # 空白ならNone（NULL）をセット

    db.session.commit()
    return redirect(url_for('surveying_list'))

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


# 機械編集モード
@app.route('/update_machine/<int:machine_id>', methods=['POST'])
def update_machine(machine_id):
    data = request.get_json()
    machine = ConstructionMachine.query.get_or_404(machine_id)

    machine.name = data.get('name', machine.name)
    machine.manufacturer = data.get('manufacturer', machine.manufacturer)
    machine.serial_number = data.get('serial_number', machine.serial_number)

    db.session.commit()
    return jsonify({'status': 'success'})

# 測量器編集モード
@app.route('/update_surveying_tool/<int:tool_id>', methods=['POST'])
def update_surveying_tool(tool_id):
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'Invalid JSON'}), 400

    tool = SurveyingTool.query.get_or_404(tool_id)

    tool.tool_type = data.get('tool_type', tool.tool_type)
    tool.name = data.get('name', tool.name)
    tool.manufacturer = data.get('manufacturer', tool.manufacturer)
    tool.serial_number = data.get('serial_number', tool.serial_number)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

    return jsonify({'status': 'success'})

# システム編集モード
@app.route('/update_system_tool/<int:system_id>', methods=['POST'])
def update_system_tool(system_id):
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'Invalid JSON'}), 400

    tool = SystemTool.query.get_or_404(system_id)

    tool.tool_type = data.get('tool_type', tool.tool_type)
    tool.name = data.get('name', tool.name)
    tool.manufacturer = data.get('manufacturer', tool.manufacturer)
    tool.serial_number = data.get('serial_number', tool.serial_number)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

    return jsonify({'status': 'success'})

# 部品編集モード
@app.route('/update_part/<int:part_id>', methods=['POST'])
@login_required
def update_part(part_id):
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'Invalid JSON'}), 400

    part = Part.query.get_or_404(part_id)

    # 文字列系
    part.part_name = data.get('part_name', part.part_name)
    part.manufacturer = data.get('manufacturer', part.manufacturer)
    part.model_number = data.get('model_number', part.model_number)
    part.remarks = data.get('remarks', part.remarks)
    part.is_shipped = data.get('is_shipped', part.is_shipped)

    # 数値系は型チェックと範囲チェックを追加
    try:
        new_stock = int(data.get('new_stock', part.new_stock))
        used_stock = int(data.get('used_stock', part.used_stock))
        if new_stock < 0 or used_stock < 0:
            raise ValueError('在庫数は0以上でなければなりません。')
        part.new_stock = new_stock
        part.used_stock = used_stock
    except (ValueError, TypeError) as e:
        return jsonify({'status': 'error', 'message': '在庫数は0以上の整数で入力してください。'}), 400

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

    return jsonify({'status': 'success'})


# 機械状態編集
@app.route('/update_state/<int:machine_id>', methods=['POST'])
def update_state(machine_id):
    machine = ConstructionMachine.query.get(machine_id)
    if not machine:
        flash("機械が見つかりません。")
        return redirect(url_for('machine_list', type='construction'))
    
    new_state = request.form.get('state')
    if new_state == "空白":
        machine.is_active = True
        machine.state = None
    elif new_state == "出庫中":
        machine.is_active = False
        machine.state = None
    elif new_state == "予定":
        machine.is_active = True  # ここを確認
        machine.state = "予定"
    else:
        # 想定外の値
        flash("無効な状態です。")
    
    db.session.commit()
    return redirect(url_for('machine_list', type='construction'))

# 測量器状態編集
@app.route('/update_surveying_state/<int:tool_id>', methods=['POST'])
def update_surveying_state(tool_id):
    tool = SurveyingTool.query.get(tool_id)
    if not tool:
        flash("測量器が見つかりません。")
        return redirect(url_for('surveying_list'))

    new_state = request.form.get('state')
    if new_state == "空白":
        tool.is_active = True
        tool.state = None
    elif new_state == "出庫中":
        tool.is_active = False
        tool.state = None
    elif new_state == "予定":
        tool.is_active = True
        tool.state = "予定"
    else:
        flash("無効な状態です。")

    db.session.commit()
    return redirect(url_for('surveying_list'))

# システム状態編集
@app.route('/update_system_state/<int:system_id>', methods=['POST'])
@login_required
def update_system_state(system_id):
    system_tool = SystemTool.query.get_or_404(system_id)

    try:
        state = request.form.get('state', '').strip()

        # 状態ごとの処理
        if state == '出庫中':
            system_tool.is_active = False
            system_tool.state = '出庫中'
        elif state == '予定':
            system_tool.is_active = True
            system_tool.state = '予定'
        else:
            system_tool.is_active = True
            system_tool.state = None  # 未設定や空白など

        db.session.commit()
        flash('システム機器の状態を更新しました。', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'状態更新中にエラーが発生しました: {str(e)}', 'danger')

    return redirect(url_for('system_list'))

# 機械過去ログ
@app.route('/shipment_history/<int:machine_id>')
def shipment_history(machine_id):
    history_records = get_shipment_history(machine_id)  # 過去ログをDBから取得
    return render_template('shipment_history.html', history=history_records)

def get_shipment_history(machine_id):
    return ShipmentHistory.query.filter_by(machine_id=machine_id).order_by(ShipmentHistory.updated_at.desc()).all()

# 測量器過去ログ
@app.route('/surveying_shipment_history/<int:tool_id>')
def surveying_shipment_history(tool_id):
    history_records = get_surveying_shipment_history(tool_id)
    return render_template('surveying_shipment_history.html', history=history_records)

def get_surveying_shipment_history(tool_id):
    return SurveyingShipmentHistory.query.filter_by(tool_id=tool_id)\
        .order_by(SurveyingShipmentHistory.updated_at.desc()).all()

# システム過去ログ
@app.route('/system_shipment_history/<int:system_id>')
def system_shipment_history(system_id):
    history_records = _get_system_shipment_history(system_id)
    return render_template('system_shipment_history.html', history=history_records, system_id=system_id)

def _get_system_shipment_history(system_id):
    return SystemShipmentHistory.query.filter_by(system_id=system_id)\
        .order_by(SystemShipmentHistory.updated_at.desc()).all()


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
