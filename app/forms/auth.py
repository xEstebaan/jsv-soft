from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
    correo = StringField("Correo", validators=[DataRequired(), Email()])
    contrasena = PasswordField("Contraseña", validators=[DataRequired()])
    recordar = BooleanField("Recordarme")
    submit = SubmitField("Iniciar Sesión")


class RegistrationForm(FlaskForm):
    primer_nombre = StringField(
        "Primer Nombre", validators=[DataRequired(), Length(max=50)]
    )
    segundo_nombre = StringField("Segundo Nombre", validators=[Length(max=50)])
    primer_apellido = StringField(
        "Primer Apellido", validators=[DataRequired(), Length(max=255)]
    )
    segundo_apellido = StringField("Segundo Apellido", validators=[Length(max=255)])
    documento = StringField("Documento", validators=[DataRequired(), Length(max=30)])
    correo = StringField("Correo", validators=[DataRequired(), Email()])
    celular = StringField("Celular", validators=[Length(max=50)])
    contrasena = PasswordField("Contraseña", validators=[DataRequired(), Length(min=6)])
    confirmar_contrasena = PasswordField(
        "Confirmar Contraseña", validators=[DataRequired(), EqualTo("contrasena")]
    )
    submit = SubmitField("Registrarse")
