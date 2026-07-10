import re
from flask import Blueprint, session, request, render_template, redirect, url_for
from db import initedDB, User

auth_bp = Blueprint('auth', __name__)

def is_strong_password(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    return True

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        user = initedDB.get_user_by_login(username)
        if user and user.check_password(password):
            session.clear()
            session['user_id'] = username
            session['username'] = username
            session['logged_in'] = True
            return redirect(url_for('main.index'))
        else:
            error = 'Неверный логин или пароль'
            return render_template('login.html', error=error, username=username)
            
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        login_val = request.form.get('login', '').strip()
        email_val = request.form.get('email', '').strip()
        password_val = request.form.get('password', '').strip()
        password_confirm_val = request.form.get('password_confirm', '').strip()
        
        form_data = {'login': login_val, 'email': email_val}

        if not login_val or not email_val or not password_val:
            error = "Все поля обязательны для заполнения"
            return render_template('register.html', error=error, form_data=form_data)

        if password_val != password_confirm_val:
            error = "Пароли не совпадают"
            return render_template('register.html', error=error, form_data=form_data)
            
        if not is_strong_password(password_val):
            error = "Пароль слишком простой (минимум 8 символов, заглавная и строчная буквы, цифра)"
            return render_template('register.html', error=error, form_data=form_data)
            
        if initedDB.get_user_by_login(login_val):
            error = "Пользователь с таким логином уже существует"
            return render_template('register.html', error=error, form_data=form_data)
            
        new_user = User(login=login_val, email=email_val, password=password_val)
        if initedDB.add_new_user(new_user):
            return redirect(url_for('auth.login'))
        else:
            error = "Ошибка при регистрации"
            return render_template('register.html', error=error, form_data=form_data)
        
    return render_template('register.html')