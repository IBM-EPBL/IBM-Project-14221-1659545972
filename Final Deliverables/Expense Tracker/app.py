import bcrypt
import ibm_db
from flask import Flask, redirect, render_template, request, session, url_for

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
    password = request.form['password']

    if not email or not password:
      return render_template('register.html')
    
#hash = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())

    print("hash : "+ hash);
    query = "SELECT * FROM USER WHERE email=?"
    stmt = ibm_db.prepare(conn, query)
    print(email)
    ibm_db.bind_param(stmt,1,email)
    ibm_db.execute(stmt)
    useravailable = ibm_db.fetch_assoc(stmt)
    
    # if not useravailable:
    #   insert_sql = "INSERT INTO users(EMAIL,PASSWORD,CREATED_ON) VALUES(?,?,CURRENT TIMESTAMP)"
    #   prep_stmt = ibm_db.prepare(conn, insert_sql)
    #   ibm_db.bind_param(prep_stmt, 1, email)
    #   ibm_db.bind_param(prep_stmt, 2, hash)
    #   ibm_db.execute(prep_stmt)
    #   return render_template('home.html')
    # else:
    #   return render_template('register.html')

  return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
      print(request.form)
      email = request.form['email']
      password = request.form['password']
      print(email,password)
      if not email or not password:
        return render_template('login ')
      query = "SELECT * FROM users WHERE EMAIL=?"
      stmt = ibm_db.prepare(conn, query)
      ibm_db.bind_param(stmt,1,email)
      ibm_db.execute(stmt)
      useravailable = ibm_db.fetch_assoc(stmt)
      print(useravailable,password)

      if not useravailable:
        return render_template('login.html')
      
      match = bcrypt.checkpw(password.encode('utf-8'),useravailable['PASSWORD'].encode('utf-8'))
      print("mathc",match)
      if not match:
        return render_template('login.html',error='Invalid Credentials')
        
      session['email'] = useravailable['EMAIL']
      return redirect(url_for('home'))

    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)