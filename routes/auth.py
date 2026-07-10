from flask import Blueprint, session, request, render_template, redirect, url_for
# from  db import initedDB

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    print(dict(session), request.method)
    if 'user_id' in session:
        return redirect(url_for('main.index'))
   
    if request.method == 'POST':
        print(1)
        if 1:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            print(2)
            if username == 'q' and password == '1':
                session.clear()
                session['user_id'] = 1
                session['username'] = username
                session['logged_in'] = True
                
                return redirect(url_for('main.index'))
            else:
                error = 'Неверный логин или пароль'
                return render_template('login.html', error=error)
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return "logged out\n"

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        pass
    return render_template('register.html')

