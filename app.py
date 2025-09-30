from flask import Flask, request, render_template_string
from google import genai
import hashlib
import os

app: Flask = Flask(__name__)  # type: ignore
USER_FILE = 'user_passwords'

register_html = '''
<!DOCTYPE html>
<html>
<head><title>Register</title></head>
<body>
  <h2>Register</h2>
  <form method="POST">
    Email: <input type="email" name="email" required><br>
    Password: <input type="password" name="password" required><br>
    <input type="submit" value="Register">
  </form>
  {% if message %}<p>{{ message }}</p>{% endif %}
  <a href="/login">Go to Login</a>
</body>
</html>
'''

login_html = '''
<!DOCTYPE html>
<html>
<head><title>Login</title></head>
<body>
  <h2>Login</h2>
  <form method="POST">
    Email: <input type="email" name="email" required><br>
    Password: <input type="password" name="password" required><br>
    <input type="submit" value="Login">
  </form>
  {% if message %}<p>{{ message }}</p>{% endif %}
  <a href="/register">Go to Register</a>
</body>
</html>
'''

@app.route('/register', methods=['GET', 'POST'])  # type: ignore
def register() -> str:  # type: ignore
    message = ''
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']
        hashed = hashlib.sha256(password.encode()).hexdigest()
        # Store as email:hashed_password\n
        # Prevent duplicate registration
        if os.path.exists(USER_FILE):
            with open(USER_FILE, 'r') as f:
                for line in f:
                    if line.split(':')[0] == email:
                        message = 'Email already registered.'
                        return render_template_string(register_html, message=message)
        with open(USER_FILE, 'a') as f:
            f.write(f"{email}:{hashed}\n")
        message = 'Registration successful.\n\n'

        # The client gets the API key from the environment variable `GEMINI_API_KEY`.
        client = genai.Client()
        respLLM = client.models.generate_content(model="gemini-2.5-flash", contents="Explain how hashing works with SHA-256 as an example, in 3 paragraphs or less.")
        # message += f"<br><br>Response from Gemini-2.5-Flash:<br>{respLLM.text}"
        message += respLLM.text
    return render_template_string(register_html, message=message)

@app.route('/login', methods=['GET', 'POST'])  # type: ignore
def login() -> str:  # type: ignore
    message = ''
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']
        hashed = hashlib.sha256(password.encode()).hexdigest()
        found = False
        if os.path.exists(USER_FILE):
            with open(USER_FILE, 'r') as f:
                for line in f:
                    stored_email, stored_hash = line.strip().split(':')
                    if stored_email == email:
                        found = True
                        if stored_hash == hashed:
                            message = 'You have logged in.'
                        else:
                            message = 'Login failed.'
                        break
        if not found:
            message = 'Login failed.'
    return render_template_string(login_html, message=message)

@app.route('/')  # type: ignore
def home() -> str:  # type: ignore
    return '<a href="/register">Register</a> | <a href="/login">Login</a>'

if __name__ == '__main__':
    app.run(debug=True)  # type: ignore
