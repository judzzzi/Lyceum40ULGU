from flask import Flask, render_template, redirect
from data import db_session
from data.users import User
from forms.user import RegisterForm, LoginForm
from flask_login import LoginManager, login_user, login_required, logout_user

db_session.global_init("db/blogs.db")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'qwerty123'
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def index():
    dat = []

    for i in range(0, 11 + 1):
        with open(f"static/text_posts/posttitles.txt", 'r', encoding='UTF-8') as f:
            ptitles = f.readlines()
        with open(f"static/text_posts/post{i + 1}.txt", 'r', encoding='UTF-8') as f:
            ptext = f.read(222)
        dat.append((ptitles[i], f'/static/img/img{i}.jpeg', ptext, i))
    return render_template('index.html', data=dat)


@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/post/<int:postnum>')
def viewpost(postnum):
    img = postnum
    with open(f"static/text_posts/post{postnum + 1}.txt", 'r', encoding='UTF-8') as f:
        t = f.read()
    with open(f"static/text_posts/posttitles.txt", 'r', encoding='UTF-8') as f:
        ptitles = f.readlines()
    return render_template('post.html', title=ptitles[postnum], item=img, text=t)


@app.route('/raspis')
def raspis():
    return render_template('rasp.html')


@app.route('/pupils_reg', methods=['GET', 'POST'])
def pupils_reg():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('pupils_reg.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('pupils_reg.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            surname=form.surname.data,
            classes=form.classes.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
    return render_template('pupils_reg.html', form=form)


@app.route('/admin_enter', methods=['GET', 'POST'])
def admin_enter():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect("/")
        return render_template('admin_enter.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('admin_enter.html', form=form)


@app.route('/items')
def print_items():
    db_sess = db_session.create_session()
    user = db_sess.query(User)
    return render_template("print_items.html", user=user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == "__main__":
    app.run(port=8081, host='127.0.0.1')
