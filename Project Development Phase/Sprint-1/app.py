import bcrypt
import ibm_db
from flask import Flask, redirect, render_template, request, session, url_for

from werkzeug.security import generate_password_hash, check_password_hash

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=6667d8e9-9d4d-4ccb-ba32-21da3bb5aafc.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=30376;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=ghy30781;PWD=vEm8kL0VlhXjKtx7",'','')

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/',methods=['GET'])
def home():
    if 'email' not in session:
      return redirect(url_for('login'))
    return render_template('home.html')

@app.route("/register",methods=['GET','POST'])
def register():
  if request.method == 'POST':
    email = request.form['email']
    password = request.form['pass']
    name = request.form['name']

    if not email or not password or not name:
      return render_template('register.html',error="enter all the details")
    
    hash = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
    
    query = "SELECT * FROM users WHERE email=?"
    stmt = ibm_db.prepare(conn, query)
    print(email)
    ibm_db.bind_param(stmt,1,email)
    ibm_db.execute(stmt)
    useravailable = ibm_db.fetch_assoc(stmt)
    
    if not useravailable:
      insert_sql = "INSERT INTO users VALUES(?,?,?,CURRENT TIMESTAMP)"
      prep_stmt = ibm_db.prepare(conn, insert_sql)
      ibm_db.bind_param(prep_stmt, 1, email)
      ibm_db.bind_param(prep_stmt, 2, hash)
      ibm_db.bind_param(prep_stmt, 3, name)
      ibm_db.execute(prep_stmt)
      return redirect(url_for('login'))
    else:
      return render_template('register.html')

  return render_template('register.html')

@app.route("/login",methods=['GET','POST'])
def login():
    if request.method == 'POST':
      email = request.form['your_name']
      password = request.form['your_pass']

      if not email or not password:
        return render_template('login.html',error='Please fill all fields')
      query = "SELECT * FROM users WHERE email=?"
      stmt = ibm_db.prepare(conn, query)
      ibm_db.bind_param(stmt,1,email)
      ibm_db.execute(stmt)
      isUser = ibm_db.fetch_assoc(stmt)
      print(isUser,password)

      if not isUser:
        return render_template('login.html',error='Mail not found')

      dbpassword = isUser['PASSWORD']
      
      isPasswordMatch = bcrypt.checkpw(password.encode('utf-8'),dbpassword.encode('utf-8'))
      # isPasswordMatch = check_password_hash(isUser['PASSWORD'],password)
      
      print("pwd from db:"+isUser['PASSWORD'])
      print("pwd from usr:"+password)

      if not isPasswordMatch:
        return render_template('login.html',error='Password Wrong')

      session['email'] = isUser['EMAIL']
      return redirect(url_for('home'))

    return render_template('login.html',name='Home')

@app.route('/profile',methods=['GET','POST'])
def profile():
    if 'email' not in session:
      return redirect(url_for('login'))
    return render_template('userProfile.html')

@app.route('/analytics',methods=['GET','POST'])
def analytics():
    if 'email' not in session:
      return redirect(url_for('login'))
    return render_template('analytics.html')

@app.route('/logout')
def logout():
  session.pop('email',None)
  return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)