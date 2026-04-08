from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models.user import User

class RegistrationForm(FlaskForm):
    username = StringField('用戶名稱', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('電郵地址', validators=[DataRequired(), Email()])
    password = PasswordField('密碼', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('確認密碼', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('註冊')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('用戶名稱已被使用。')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('電郵地址已被註冊。')

class LoginForm(FlaskForm):
    username = StringField('用戶名稱', validators=[DataRequired()])
    password = PasswordField('密碼', validators=[DataRequired()])
    submit = SubmitField('登入')