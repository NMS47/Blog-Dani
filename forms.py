from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, URL, InputRequired, Length, Email
from flask_ckeditor import CKEditorField


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Título", validators=[DataRequired()])
    subtitle = StringField("Subtitulo", validators=[DataRequired()])
    category = SelectField(u"Categoría", choices=['Viajes', 'Escalada', 'Montañismo', 'Otra'])
    img_url = StringField("URL de la imagen", default="http://drive.google.com/uc?export=view&id=", validators=[DataRequired(), URL()])
    body = CKEditorField("Contenido", validators=[DataRequired()])
    submit = SubmitField("Subir Post")


class ContactForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[InputRequired(), Length(min=6, max=30), Email()])
    phone = StringField('Phone', validators=[Length(min=8, max=20)])
    message = TextAreaField('Message', validators=[InputRequired(), Length(min=10, max=100)])
    submit = SubmitField('Enviar')
