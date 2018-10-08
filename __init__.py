'''
Author: Debjyoti Guha
Date: 08/10/2018
Description:  A Python-Flask app for booking seminar-hall and Live announcements.
The project requires so much of effort if you want to re-use it please mention the Authors in your project.
'''
from flask import Flask, render_template, request, redirect, url_for, flash, session
import pymysql

app = Flask(__name__)
app.secret_key = 'many random bytes'

db = pymysql.connect(host="localhost", user="root", passwd="", db="seminar")
cur = db.cursor()


@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('choose.html')
    else:
        return redirect('/index')


@app.route('/admin')
def dash1():
    return render_template('admin.html')


@app.route('/user')
def dash():
    return render_template('user.html')

@app.route('/register')
def dash2():
    return render_template('register.html')


@app.route('/addannoun')
def addannoun():
    if not session.get('logged_in'):
        return render_template('choose.html')
    if session.get('username') == 'admin':
        return render_template('admin/addannoun.html')


@app.route('/viewannoun')
def viewannoun():
    if not session.get('logged_in'):
        return render_template('choose.html')
    if session.get('username') == 'admin':
        cur.execute("SELECT  * FROM announcements")
        data = cur.fetchall()
        return render_template('admin/allannoun.html', announcements=data)
    cur.execute("SELECT  * FROM announcements")
    data = cur.fetchall()
    return render_template('user/allannoun.html', announcements=data)


@app.route('/announce', methods=['POST'])
def announce():
    if not session.get('logged_in'):
        return render_template('choose.html')
    if session.get('username') == 'admin':
        if request.method == "POST":
            text = request.form['text']
            sub = request.form['sub']
            date = request.form['date']
            active = 1
            cur.execute("INSERT INTO announcements (sub, txt, date, active) VALUES ( %s, %s, %s, %s)", (sub, text, date, active))
            #flash("Data Inserted Successfully")
            db.commit()
            return redirect(url_for('viewannoun'))


@app.route('/removeann/<string:id_data>', methods=['GET'])
def removeann(id_data):
    if not session.get('logged_in'):
        return render_template('choose.html')
    #flash("Record Has Been Deleted Successfully")
    cur.execute("DELETE FROM announcements WHERE id=%s", (id_data,))
    db.commit()
    return redirect(url_for('viewannoun'))


@app.route('/approve')
def approve():
    if not session.get('logged_in'):
        return render_template('choose.html')
    if session.get('username') == 'admin':
        cur.execute("SELECT  * FROM applications")
        data = cur.fetchall()
        return render_template('admin/approve.html', applications=data)


@app.route('/edituser')
def edituser():
    if not session.get('logged_in'):
        return render_template('choose.html')
    if session.get('username') == 'admin':
        cur.execute("SELECT  * FROM admin")
        data = cur.fetchall()
        return render_template('admin/updateuser.html', applications=data)
    cur.execute("SELECT  * FROM users where username=%s", (session['id']))
    data = cur.fetchall()
    # cur.close()
    return render_template('user/updateuser.html', applications=data)


@app.route('/apply')
def apply():
    if not session.get('logged_in'):
        return render_template('choose.html')
    if session.get('username') == 'admin':
        cur.execute("SELECT  * FROM admin")
        data = cur.fetchall()
        return render_template('admin/apply.html', applications=data)
    cur.execute("SELECT  * FROM applications where userid=%s", (session['id']))
    data = cur.fetchall()
    # cur.close()
    return render_template('user/apply.html', applications=data)


@app.route('/accept/<string:id_data>', methods=['GET'])
def accept(id_data):
    if not session.get('logged_in'):
        return render_template('choose.html')
    #flash("Approved")
    cur.execute("UPDATE applications SET accepted=1 WHERE id=%s", (id_data,))
    db.commit()
    return redirect(url_for('approve'))


@app.route('/reject/<string:id_data>', methods=['GET'])
def reject(id_data):
    if not session.get('logged_in'):
        return render_template('choose.html')
    #flash("Rejected")
    cur.execute("UPDATE applications SET accepted=2 WHERE id=%s", (id_data,))
    db.commit()
    return redirect(url_for('approve'))


@app.route('/adminlogin', methods=['POST'])
def do_admin_login():
    username = request.form['username']
    password = request.form['password']
    cur.execute("SELECT * from admin where username='" + username + "' and password='" + password + "'")
    data = cur.fetchone()
    if data is None:
        flash('wrong credentials!')
        return dash1()
    else:
        session['logged_in'] = True
        session['username'] = username
        session['password'] = data[2]
        session['email'] = data[3]
        session['phone'] = data[4]
        session['id'] = data[0]
    return home()


@app.route('/userlogin', methods=['POST'])
def do_user_login():
    username = request.form['username']
    password = request.form['password']
    cur.execute("SELECT * from users where username='" + username + "' and password='" + password + "'")
    data = cur.fetchone()
    if data is None:
        flash('wrong credentials!')
        return dash()
    else:
        session['logged_in'] = True
        session['username'] = username
        session['password'] = data[2]
        session['email'] = data[3]
        session['phone'] = data[4]
        session['id'] = data[0]
    return home()


@app.route('/userregister', methods=['POST'])
def userregister():
    if session.get('logged_in'):
        return home()
    if request.method == "POST":
        name = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']
        cur.execute("INSERT INTO users ( username, password, email, phone) VALUES (%s, %s, %s, %s)", (name, password, email, phone))
        flash(" user Registered Successfully")
        db.commit()
        return redirect(url_for('dash'))


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()


@app.route('/index')
def index():
    if not session.get('logged_in'):
        return render_template('choose.html')
    if session.get('username') == 'admin':
        cur.execute("SELECT  * FROM applications")
        data = cur.fetchall()
        return render_template('admin/index.html', applications=data)
    cur.execute("SELECT  * FROM applications where userid=%s  AND name=%s", (session['id'], session['username']))
    data = cur.fetchall()
    # cur.close()
    return render_template('user/index.html', applications=data)


@app.route('/insert', methods=['POST'])
def insert():
    if not session.get('logged_in'):
        return render_template('choose.html')
    if request.method == "POST":
        datef = request.form['datef']
        datet = request.form['datet']
        list = request.form.getlist('hall')
        hall = ", ".join(str(x) for x in list)
        comment = request.form['comment']
        cur.execute("INSERT INTO applications (userid, name, datef, datet, email, phone, hall, comment) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (session['id'], session['username'], datef, datet, session['email'], session['phone'], hall, comment))
        #flash("Data Inserted Successfully")
        db.commit()
        return redirect(url_for('index'))


@app.route('/delete/<string:id_data>', methods=['GET'])
def delete(id_data):
    if not session.get('logged_in'):
        return render_template('choose.html')
    #flash("Record Has Been Deleted Successfully")
    cur.execute("DELETE FROM applications WHERE id=%s", (id_data,))
    db.commit()
    return redirect(url_for('index'))


@app.route('/updateaccount', methods=['POST', 'GET'])
def updateaccount():
    if not session.get('logged_in'):
        return render_template('choose.html')
    if request.method == 'POST':
        id_data = session['id']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']
        if session.get('username') == 'admin':
            cur.execute("""
                UPDATE admin
                SET  password=%s, email=%s, phone=%s
                WHERE id=%s
                """, (password, email, phone, id_data))
            db.commit()
            session['logged_in'] = False
            return redirect(url_for('index'))
        cur.execute("""
            UPDATE users
            SET  password=%s, email=%s, phone=%s
            WHERE id=%s
            """, (password, email, phone, id_data))
        #flash("Data Updated Successfully")
        db.commit()
        session['logged_in'] = False
        return redirect(url_for('index'))


@app.route('/update', methods=['POST', 'GET'])
def update():
    if not session.get('logged_in'):
        return render_template('choose.html')
    if request.method == 'POST':
        id_data = request.form['id_data']
        name = session['username']
        email = session['email']
        phone = session['phone']
        datef = request.form['datef']
        datet = request.form['datet']
        hall = request.form['hall']
        comment = request.form['comment']
        cur.execute("""
               UPDATE applications
               SET datef=%s, datet=%s, hall=%s, comment=%s
               WHERE id=%s
            """, (datef, datet, hall, comment, id_data))
        #flash("Data Updated Successfully")
        db.commit()
        return redirect(url_for('index'))


@app.errorhandler(403)
def forbidden(error):
    return render_template('errors/403.html', title='Forbidden'), 403


@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html', title='Page Not Found'), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('errors/500.html', title='Server Error'), 500


if __name__ == "__main__":
    app.run(debug=True)
