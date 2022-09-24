from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField

##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Título", validators=[DataRequired()])
    subtitle = StringField("Subtitulo", validators=[DataRequired()])
    category = SelectField(u"Categoría", choices=['Viajes', 'Escalada', 'Montañismo', 'Otra'])
    img_url = StringField("URL de la imagen", default="http://drive.google.com/uc?export=view&id=", validators=[DataRequired(), URL()])
    body = CKEditorField("Contenido", validators=[DataRequired()])
    submit = SubmitField("Subir Post")
