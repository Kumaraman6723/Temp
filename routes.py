from flask import render_template, request, redirect, url_for, session, flash, jsonify
from models import fetch_email, recover_passkey, fetch_users, get_db_connection
from email_service import send_email
from forms import RegisterForm, VerificationForm, OTPForm, ForgetPass
from utils import otpmaker, check_password
from config import appConf, SITE_KEY, SECRET_KEY
from werkzeug.security import generate_password_hash
from authlib.integrations.flask_client import OAuth
from authlib.integrations.base_client import OAuthError
import requests
import json
import pytz
import time
from datetime import datetime, timedelta

def register_routes(app, oauth):
    # Login route
    @app.route("/", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            store = fetch_users()
            token = request.form.get('cf-turnstile-response')
            ip = request.remote_addr

            # Verify Cloudflare Turnstile
            form_data = {
                'secret': SECRET_KEY,
                'response': token,
                'remoteip': ip
            }
            response = requests.post('https://challenges.cloudflare.com/turnstile/v0/siteverify', data=form_data)
            outcome = response.json()

            if not outcome['success']:
                flash('The provided Turnstile token was not valid!', 'error')
                return redirect(url_for('login'))

            email = request.form["email"]
            password = request.form["password"]
            user = next((x for x in store if x[0] == email), None)

            if user and check_password(user[1], password):
                session["login_email"] = email
                return redirect(url_for('two_step'))
            else:
                flash("Invalid email or password", "error")

        return render_template("login.html", site_key=SITE_KEY)

    # Home route
    @app.route("/home")
    def home():
        return render_template("home.html", session=session.get("user"),
                               pretty=json.dumps(session.get("user"), indent=4))

    # Google OAuth routes
    @app.route("/signin-google")
    def googleCallback():
        try:
            token = oauth.myApp.authorize_access_token()
        except OAuthError:
            return redirect(url_for("login"))

        # Fetch user info and person data
        user_info_response = requests.get(
            f'https://www.googleapis.com/oauth2/v1/userinfo?access_token={token["access_token"]}',
            headers={'Authorization': f'Bearer {token["access_token"]}'}
        )
        user_info = user_info_response.json()

        person_data_response = requests.get(
            "https://people.googleapis.com/v1/people/me?personFields=genders,birthdays",
            headers={"Authorization": f"Bearer {token['access_token']}"}
        )
        person_data = person_data_response.json()

        token["user_info"] = user_info
        token["person_data"] = person_data
        session["user"] = token
        return redirect(url_for("home"))

    @app.route("/google-login")
    def googleLogin():
        session.clear()
        redirect_uri = url_for("googleCallback", _external=True)
        return oauth.myApp.authorize_redirect(redirect_uri=redirect_uri)

    # Logout route
    @app.route("/logout")
    def logout():
        if "user" in session:
            token = session["user"].get("access_token")
            if token:
                requests.post("https://accounts.google.com/o/oauth2/revoke", params={"token": token})
        session.clear()
        return redirect(url_for("login"))

    # Registration route
    @app.route("/register", methods=["GET", "POST"])
    def register():
        form = RegisterForm()
        if form.validate_on_submit():
            hash_and_salted_password = generate_password_hash(
                form.password.data, method='pbkdf2:sha256', salt_length=8)
            
            session.update({
                "first_name": form.first_name.data,
                "last_name": form.last_name.data,
                "email": form.email.data,
                "password": hash_and_salted_password,
                "EMAIL": form.email.data,
                "contact": form.contact.data
            })

            if session["email"] in fetch_email():
                flash("This email is already registered. Please use a different email.", "danger")
            else:
                return redirect(url_for("mail_otp"))

        return render_template("register.html", form=form)

    # Password verification route
    @app.route("/verification", methods=["GET", "POST"])
    def verify_pass():
        form = VerificationForm()
        if form.validate_on_submit():
            email = form.email.data
            if email in fetch_email():
                session["verify_email"] = email
                return redirect(url_for('two_step_forget'))
            flash("This email is not registered.", "danger")
        return render_template("verify_pass.html", form=form)

    # Dashboard route
    @app.route("/DashBoard", methods=["GET", "POST"])
    def DashBoard():
        return render_template("DashBoard.html")

    # Contact route
    @app.route("/contact", methods=["GET", "POST"])
    def contact():
        if request.method == "POST":
            data = request.form
            send_email(data["email"], f"Name: {data['name']}\nPhone: {data['phone']}\nMessage: {data['message']}", "New Message")
            return render_template("contact.html", msg_sent=True)
        return render_template("contact.html", msg_sent=False)

    # Helper functions
    def is_otp_expired():
        current_time = time.time()
        expiry_time = session.get('OTP_EXPIRY')
        if isinstance(expiry_time, (int, float)):
            return current_time > expiry_time
        elif isinstance(expiry_time, str):
            try:
                expiry_datetime = datetime.fromisoformat(expiry_time)
                return datetime.now() > expiry_datetime
            except ValueError:
                return True
        return True

    def send_new_otp(email, subject="New Message"):
        otp = otpmaker()
        send_email(email, f"OTP: {otp}", subject)
        session["otp"] = otp
        session['OTP_EXPIRY'] = time.time() + 30

    # Two-step verification routes
    @app.route("/two-step", methods=["GET", "POST"])
    def two_step():
        form = OTPForm()
        email = session.get("login_email")

        if request.method == "GET" or (request.method == "POST" and 'resend_otp' in request.form):
            if not session.get('OTP_SENT', False) or is_otp_expired() or 'resend_otp' in request.form:
                send_new_otp(email, "Email Verification")
                session['OTP_SENT'] = True
                if request.method == "POST":
                    return "", 204  # Return empty response for AJAX request

        if request.method == "POST" and 'resend_otp' not in request.form:
            otp_input = request.form["otp"]
            if is_otp_expired():
                flash("OTP has expired. Try again", "danger")
                return redirect(url_for("login"))
            elif otp_input == session.get("otp"):
                session.clear()
                return redirect(url_for("DashBoard"))
            else:
                flash("Incorrect OTP", "danger")

        return render_template("2FA.html", form=form)

    @app.route("/two-step-forget", methods=["GET", "POST"])
    def two_step_forget():
        form = OTPForm()
        email = session.get("verify_email")

        if request.method == "GET" or (request.method == "POST" and 'resend_otp' in request.form):
            if not session.get('otp') or is_otp_expired() or 'resend_otp' in request.form:
                send_new_otp(email)
                if request.method == "POST":
                    return "", 204

        if request.method == "POST" and 'resend_otp' not in request.form:
            if form.validate_on_submit():
                otp = form.otp.data
                if is_otp_expired():
                    flash("OTP has expired. Try Again", "danger")
                    return redirect(url_for("verify_pass"))
                elif otp == session.get("otp"):
                    session['forget_password_verified'] = True
                    return redirect(url_for("forgot_pass"))
                else:
                    flash("Incorrect OTP", "danger")

        return render_template("forgot_otp.html", form=form)

    # Forgot password route
    @app.route("/forgot", methods=["GET", "POST"])
    def forgot_pass():
        if not session.get('forget_password_verified'):
            flash("Please verify your email first.", "danger")
            return redirect(url_for('verify_pass'))

        form = ForgetPass()
        email = session.get("verify_email")
        
        if request.method == "POST" and form.validate_on_submit():
            hash_and_salted_password = generate_password_hash(
                form.password.data, method='pbkdf2:sha256', salt_length=8
            )
            recover_passkey(hash_and_salted_password, email)
            session.pop("verify_otp", None)
            session.pop("forget_password_verified", None)
            flash("Password Changed. Please log in.", "success")
            return redirect(url_for('login'))
        
        return render_template("forgot_password.html", form=form)

    # Email OTP verification route
    @app.route("/email-otp", methods=["GET", "POST"])
    def mail_otp():
        form = OTPForm()
        email = session["email"]

        if request.method == "GET" or (request.method == "POST" and 'resend_otp' in request.form):
            if not session.get('otp') or is_otp_expired() or 'resend_otp' in request.form:
                send_new_otp(email)
                if request.method == "POST":
                    return "", 204

        if request.method == "POST" and 'resend_otp' not in request.form:
            if form.validate_on_submit():
                otp = form.otp.data
                if is_otp_expired():
                    flash("OTP has expired. Please try Again", "danger")
                    return redirect(url_for("register"))
                elif otp == session.get("otp"):
                    # Save user data to database
                    conn = get_db_connection()
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO auth (Email, Password, first_name, last_name, Contact) VALUES (%s, %s, %s, %s, %s)",
                        (session["email"], session["password"], session["first_name"], session["last_name"], session["contact"])
                    )
                    conn.commit()
                    conn.close()
                    flash("Registration successful! Please log in.", "success")
                    return redirect(url_for("login"))
                else:
                    flash("Incorrect OTP", "danger")

        return render_template("email_verify.html", form=form)