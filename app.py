from flask import Flask, render_template, flash, request
from wtforms import Form, StringField, PasswordField
from wtforms.validators import EqualTo, InputRequired, Length
from devices import all_devices
import secrets
from flask_celery import make_celery


DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = make_celery(app)
class ReusableForm(Form):
    username = StringField('Name:', validators=[InputRequired()])
    password = PasswordField('Password:', validators=[InputRequired(), Length(min=3)])
    confirm_password = PasswordField('confirm_password:', validators=[EqualTo('password')])


@app.route("/", methods=['GET', 'POST'])
def user_create():
    form = ReusableForm(request.form)
    if request.method == 'POST' and form.validate():
        mk_user = form.username.data
        mk_pass = form.password.data
        print('DEBUG: Valid attemp!\n')
        print('DEBUG: Username: ', mk_user)
        print('DEBUG: Password: ', mk_pass)
        flash('Initiating router connections for ' + mk_user)
        call_routers.delay(mk_user, mk_pass)
        print('Done.')
    else:
        flash('Error: Check the passwords')
        print('DEBUG: INvalid attemp!\n')
        print(form.username.data)
        print(form.password.data)
        print(form.confirm_password.data)
    return render_template('index.html', form=form)


@celery.task(name='app.call_routers')
def call_routers(mk_user, mk_pass):
    return all_devices(mk_user, mk_pass)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
