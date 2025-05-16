
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class EquipmentForm(FlaskForm):
    name = StringField('機材名', validators=[DataRequired()])
    location = StringField('場所', validators=[DataRequired()])
    status = StringField('状態（入庫／出庫）', validators=[DataRequired()])
    submit = SubmitField('保存')
