from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, URL, InputRequired, Length, Email
from flask_ckeditor import CKEditorField


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Título", validators=[DataRequired()])
    subtitle = StringField("Subtitulo", validators=[DataRequired()])
    category = SelectField(u"Categoría", choices=['Viajes', 'Escalada', 'Montañismo', 'Otra'])
    img_url = StringField("URL de la imagen", default="https://drive.google.com/uc?export=view&id=", validators=[DataRequired(), URL()])
    body = CKEditorField("Contenido", validators=[DataRequired()])
    submit = SubmitField("Subir Post")


class ContactForm(FlaskForm):
    name = StringField('Nombre', validators=[InputRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[InputRequired(), Length(min=6, max=50), Email()])
    message = TextAreaField('Mensaje', validators=[InputRequired()])
    submit = SubmitField('Enviar')
