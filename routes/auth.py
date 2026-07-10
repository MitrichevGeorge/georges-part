import re

from flask import (
    Blueprint,
    session,
    request,
    render_template,
    redirect,
    url_for,
)

from db import initedDB, User

auth_bp = Blueprint("auth", __name__)


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


def current_user():
    if not session.get("logged_in"):
        return None

    return initedDB.get_user_by_login(session["username"])


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if session.get("logged_in"):
        return redirect(url_for("main.index"))

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        user = initedDB.get_user_by_login(username)

        if user and user.check_password(password):

            session.clear()

            session["logged_in"] = True
            session["user_id"] = username
            session["username"] = username

            return redirect(url_for("main.index"))

        return render_template(
            "login.html",
            error="Неверный логин или пароль",
            username=username,
        )

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if session.get("logged_in"):
        return redirect(url_for("main.index"))

    if request.method == "POST":

        login = request.form.get("login", "").strip()
        email = request.form.get("email", "").strip()

        password = request.form.get("password", "").strip()
        password2 = request.form.get("password_confirm", "").strip()

        form_data = {
            "login": login,
            "email": email,
        }

        if not login or not email or not password:
            return render_template(
                "register.html",
                error="Все поля обязательны.",
                form_data=form_data,
            )

        if password != password2:
            return render_template(
                "register.html",
                error="Пароли не совпадают.",
                form_data=form_data,
            )

        if not is_strong_password(password):
            return render_template(
                "register.html",
                error="Слишком простой пароль.",
                form_data=form_data,
            )

        if initedDB.get_user_by_login(login):
            return render_template(
                "register.html",
                error="Такой пользователь уже существует.",
                form_data=form_data,
            )

        user = User(
            login=login,
            email=email,
            password=password,
        )

        if initedDB.add_new_user(user):
            return redirect(url_for("auth.login"))

        return render_template(
            "register.html",
            error="Ошибка регистрации.",
            form_data=form_data,
        )


@auth_bp.route("/profile")
def profile():

    user = current_user()

    if not user:
        return redirect(url_for("auth.login"))

    return render_template(
        "profile.html",
        user=user,
    )


@auth_bp.route("/profile/edit", methods=["POST"])
def edit_profile():

    user = current_user()

    if not user:
        return redirect(url_for("auth.login"))


    new_login = request.form.get(
        "login",
        ""
    ).strip()


    new_email = request.form.get(
        "email",
        ""
    ).strip()



    if not new_login or not new_email:

        return render_template(
            "profile.html",
            user=user,
            error="Все поля обязательны."
        )



    if new_login != user.login:

        exists = initedDB.get_user_by_login(
            new_login
        )

        if exists:

            return render_template(
                "profile.html",
                user=user,
                error="Такой логин уже занят."
            )



    initedDB.update_user(
        old_login=user.login,
        login=new_login,
        email=new_email
    )



    session["username"] = new_login
    session["user_id"] = new_login



    return redirect(
        url_for("auth.profile")
    )



@auth_bp.route("/profile/password", methods=["POST"])
def change_password():

    user = current_user()

    if not user:
        return redirect(url_for("auth.login"))



    old_password = request.form.get(
        "old_password",
        ""
    )

    new_password = request.form.get(
        "new_password",
        ""
    )

    repeat_password = request.form.get(
        "repeat_password",
        ""
    )



    if not user.check_password(old_password):

        return render_template(
            "profile.html",
            user=user,
            error="Старый пароль неверный."
        )



    if new_password != repeat_password:

        return render_template(
            "profile.html",
            user=user,
            error="Новые пароли не совпадают."
        )



    if not is_strong_password(new_password):

        return render_template(
            "profile.html",
            user=user,
            error="Пароль слишком простой."
        )



    initedDB.update_password(
        user.login,
        new_password
    )


    return redirect(
        url_for("auth.profile")
    )




@auth_bp.route(
    "/profile/delete",
    methods=[
        "GET",
        "POST"
    ]
)
def delete_account():

    user = current_user()


    if not user:
        return redirect(
            url_for("auth.login")
        )



    if request.method == "POST":


        confirm = request.form.get(
            "confirm",
            ""
        )

        password = request.form.get(
            "password",
            ""
        )



        if confirm != "Я УВЕРЕН":

            return render_template(
                "delete_account.html",
                user=user,
                error="Введите текст подтверждения правильно."
            )



        if not user.check_password(password):

            return render_template(
                "delete_account.html",
                user=user,
                error="Неверный пароль."
            )



        initedDB.delete_user(
            user.login
        )



        session.clear()


        return redirect(
            url_for("auth.register")
        )



    return render_template(
        "delete_account.html",
        user=user
    )