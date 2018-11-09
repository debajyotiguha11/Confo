"""
Author: Debjyoti Guha
Date: 08/10/2018
Description:  A Python-Flask app for booking seminar-hall and Live announcements.
The project requires so much of effort if you want to re-use it please mention the Authors in your project.
"""
from flask import Flask, render_template, request, redirect, url_for, flash, session
import pymysql
import hashlib

app = Flask(__name__)
app.secret_key = 'many random bytes'

try:
    db = pymysql.connect(host="localhost", user="root", passwd="", db="seminar")
    cur = db.cursor()

except:
    print("!---- YOUR SERVER IS NOT RUNNING ----!")
    exit(0)


@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('index.html')
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


@app.route('/feedback')
def feedback():
    if not session.get('logged_in'):
        return render_template('index.html')
    if session.get('username') == 'admin':
        cur.execute(
            "SELECT  u.name,f.datef,u.email,h.hname,feedback FROM feedback f, users u, hall h where f.uid = u.uid and f.hid = h.hid order by f.datef DESC")
        data = cur.fetchall()
        return render_template('admin/feedbacks.html', result=data)
    return render_template('user/feedback.html')


@app.route('/submit', methods=['POST'])
def submit():
    if not session.get('logged_in'):
        return render_template('index.html')
    if request.method == "POST":
        datef = request.form['datef']
        hall = int(request.form['hall'])
        fk = request.form['feedback']
        cur.execute("INSERT INTO feedback (uid,hid,feedback,datef) values (%s, %s, %s, %s)",
                    (session['id'], hall, fk, datef))
        db.commit()
        return render_template('user/thanks.html')


@app.route('/search')
def search():
    return render_template('user/search.html')


@app.route('/result', methods=['POST'])
def result():
    if not session.get('logged_in'):
        return render_template('index.html')
    if request.method == "POST":
        datef = request.form['datef']
        datet = request.form['datet']
        cap = int(request.form['hall'])
        cur.execute(
            "select hname,facility,capacity,description,price from hall h where capacity >= %s and hid not in (select hid from booking where accepted = 1 and datef between %s and %s) order by capacity",
            (cap, datef, datet))
        data = cur.fetchall()
        return render_template('user/result.html', result=data)


@app.route('/addannoun')
def addannoun():
    if not session.get('logged_in'):
        return render_template('index.html')
    if session.get('username') == 'admin':
        return render_template('admin/addannoun.html')


@app.route('/viewannoun')
def viewannoun():
    if not session.get('logged_in'):
        return render_template('index.html')
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
        return render_template('index.html')
    if session.get('username') == 'admin':
        if request.method == "POST":
            text = request.form['text']
            sub = request.form['sub']
            date = request.form['date']
            active = 1
            cur.execute("INSERT INTO announcements (sub, comment, datef, active, aid) VALUES ( %s, %s, %s, %s, %s)",
                        (sub, text, date, active, session['id']))
            # flash("Data Inserted Successfully")
            db.commit()
            return redirect(url_for('viewannoun'))


@app.route('/removeann/<string:id_data>', methods=['GET'])
def removeann(id_data):
    if not session.get('logged_in'):
        return render_template('index.html')
    # flash("Record Has Been Deleted Successfully")
    cur.execute("DELETE FROM announcements WHERE id=%s", (id_data,))
    db.commit()
    return redirect(url_for('viewannoun'))


@app.route('/approve')
def approve():
    if not session.get('logged_in'):
        return render_template('index.html')
    if session.get('username') == 'admin':
        cur.execute(
            "SELECT  name,datef,datet,email,ph,hname,comment,accepted,bid,paid FROM booking b,users u, hall h where b.uid=u.uid and b.hid=h.hid and accepted = 0")
        data = cur.fetchall()
        return render_template('admin/approve.html', applications=data)


@app.route('/edituser')
def edituser():
    if not session.get('logged_in'):
        return render_template('index.html')
    if session.get('username') == 'admin':
        cur.execute("SELECT  * FROM admin")
        data = cur.fetchall()
        return render_template('admin/updateadmin.html', applications=data)
    cur.execute("SELECT  * FROM users where uid=%s", (session['id']))
    data = cur.fetchall()
    # cur.close()
    return render_template('user/updateuser.html', applications=data)


@app.route('/apply')
def apply():
    if not session.get('logged_in'):
        return render_template('index.html')
    cur.execute("SELECT  * FROM hall")
    data = cur.fetchall()
    return render_template('user/apply.html', result=data)


@app.route('/accept/<string:id_data>', methods=['GET'])
def accept(id_data):
    if not session.get('logged_in'):
        return render_template('index.html')
    # flash("Approved")
    cur.execute("UPDATE booking SET accepted=1 WHERE bid=%s", (id_data))
    db.commit()
    return redirect(url_for('approve'))


@app.route('/reject/<string:id_data>', methods=['GET'])
def reject(id_data):
    if not session.get('logged_in'):
        return render_template('index.html')
    # flash("Rejected")
    cur.execute("UPDATE booking SET accepted=2 WHERE bid=%s", (id_data))
    db.commit()
    return redirect(url_for('approve'))


@app.route('/adminlogin', methods=['POST'])
def do_admin_login():
    username = request.form['username']
    p = request.form['password']
    password = hashlib.md5(p.encode()).hexdigest()
    cur.execute("SELECT * from admin where name='" + username + "' and pass='" + password + "'")
    data = cur.fetchone()
    if data is None:
        flash('wrong credentials!')
        return dash1()
    else:
        session['logged_in'] = True
        session['username'] = username
        session['email'] = data[3]
        session['phone'] = data[4]
        session['id'] = data[0]
    return home()


@app.route('/userlogin', methods=['POST'])
def do_user_login():
    username = request.form['username']
    p = request.form['password']
    password = hashlib.md5(p.encode()).hexdigest()
    cur.execute("SELECT * from users where name='" + username + "' and pass='" + password + "'")
    data = cur.fetchone()
    if data is None:
        flash('wrong credentials!')
        return dash()
    else:
        session['logged_in'] = True
        session['username'] = username
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
        p = request.form['password']
        password = hashlib.md5(p.encode()).hexdigest()
        email = request.form['email']
        phone = request.form['phone']
        cur.execute("INSERT INTO users ( name, pass, email, ph) VALUES (%s, %s, %s, %s)",
                    (name, password, email, phone))
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
        return render_template('index.html')
    if session.get('username') == 'admin':
        cur.execute(
            "SELECT  name,datef,email,hname,comment,accepted,bid,datet,paid FROM booking b,users u, hall h where b.hid = h.hid and b.uid = u.uid")
        data = cur.fetchall()
        return render_template('admin/index.html', applications=data)
    cur.execute(
        "SELECT  name,datef,email,hname,comment,accepted,bid,datet,paid FROM booking b,users u, hall h where b.hid = h.hid and b.uid = u.uid and b.uid=%s",
        (session['id']))
    data = cur.fetchall()
    # cur.close()
    return render_template('user/index.html', applications=data)


@app.route('/addhall')
def addhall():
    if not session.get('logged_in'):
        return render_template('index.html')
    if session.get('username') == 'admin':
        return render_template('admin/addhall.html')


@app.route('/halls')
def halls():
    if not session.get('logged_in'):
        return render_template('index.html')
    if session.get('username') == 'admin':
        cur.execute("SELECT * from hall ORDER BY capacity")
    data = cur.fetchall()
    return render_template('admin/halls.html', result=data)


@app.route('/hallinsert', methods=['POST'])
def hallinsert():
    if not session.get('logged_in'):
        return render_template('index.html')
    if session.get('username') == 'admin':
        if request.method == "POST":
            hname = request.form['hname']
            facility = request.form['facility']
            capacity = request.form['capacity']
            description = request.form['description']
            price = request.form['price']
            cur.execute("INSERT INTO hall (hname, facility, capacity, description, price) VALUES (%s, %s, %s, %s, %s)",(hname, facility, capacity,description, price))
            # flash("hall Inserted Successfully")
            db.commit()
            return redirect(url_for('halls'))


@app.route('/deletehall/<string:id_data>', methods=['GET'])
def deletehall(id_data):
    if not session.get('logged_in'):
        return render_template('index.html')
    if session.get('username') == 'admin':
        # flash("Record Has Been Deleted Successfully")
        cur.execute("DELETE FROM hall WHERE hid=%s", (id_data))
        db.commit()
        return redirect(url_for('halls'))


@app.route('/insert', methods=['POST'])
def insert():
    if not session.get('logged_in'):
        return render_template('index.html')
    if request.method == "POST":
        datef = request.form['datef']
        datet = request.form['datet']
        hall = request.form['hall']
        comment = request.form['comment']
        cur.execute(
            "INSERT INTO booking (uid, datef, datet, hid, comment,accepted,paid) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (session['id'], datef, datet, hall, comment, 0, 0))
        # flash("Data Inserted Successfully")
        db.commit()
        return redirect(url_for('index'))


@app.route('/delete/<string:id_data>', methods=['GET'])
def delete(id_data):
    if not session.get('logged_in'):
        return render_template('index.html')
    # flash("Record Has Been Deleted Successfully")
    cur.execute("DELETE FROM booking WHERE bid=%s", (id_data))
    db.commit()
    return redirect(url_for('index'))


@app.route('/pay/<string:id_data>', methods=['GET'])
def pay(id_data):
    if not session.get('logged_in'):
        return render_template('index.html')
    cur.execute("UPDATE booking set paid = %s where bid = %s and uid = %s", (1, id_data, session['id']))
    db.commit()
    return redirect(url_for('index'))


@app.route('/payment/<string:id_data>', methods=['GET'])
def payment(id_data):
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        cur.execute(
            "SELECT  name,datef,email,hname,comment,h.price,b.bid FROM booking b,users u, hall h where b.hid = h.hid and b.uid = u.uid and b.uid=%s and b.bid=%s",
            (session['id'], id_data))
        data = cur.fetchall()
        return render_template('user/payment.html', result=data)


@app.route('/paymentdetails/<string:id_data>', methods=['GET'])
def paymentdetails(id_data):
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        cur.execute(
            "select name,email,ph,h.hname,h.price,datef,comment FROM booking b,users u, hall h where b.hid = h.hid and b.uid = u.uid and b.uid=%s and b.bid=%s",
            (session['id'], id_data))
        data = cur.fetchall()
        return render_template('user/paymentdetails.html', result=data)


@app.route('/updateaccount', methods=['POST', 'GET'])
def updateaccount():
    if not session.get('logged_in'):
        return render_template('index.html')
    if request.method == 'POST':
        id_data = session['id']
        p = request.form['password']
        password = hashlib.md5(p.encode()).hexdigest()
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        if session.get('username') == 'admin':
            cur.execute("""
                UPDATE admin
                SET  name=%s, pass=%s, email=%s, ph=%s
                WHERE aid=%s
                """, (name, password, email, phone, id_data))
            db.commit()
            session['logged_in'] = False
            return redirect(url_for('index'))
        cur.execute("""
            UPDATE users
            SET  name=%s, pass=%s, email=%s, ph=%s
            WHERE uid=%s
            """, (name, password, email, phone, id_data))
        # flash("Data Updated Successfully")
        db.commit()
        session['logged_in'] = False
        return redirect(url_for('index'))


@app.route('/update', methods=['POST', 'GET'])
def update():
    if not session.get('logged_in'):
        return render_template('index.html')
    if request.method == 'POST':
        id_data = request.form['id_data']
        datef = request.form['datef']
        datet = request.form['datet']
        comment = request.form['comment']
        cur.execute("""
               UPDATE booking
               SET datef=%s, datet=%s, comment=%s
               WHERE bid=%s
            """, (datef, datet, comment, id_data))
        # flash("Data Updated Successfully")
        db.commit()
        return redirect(url_for('index'))


@app.route('/hallupdate', methods=['POST', 'GET'])
def hallupdate():
    if not session.get('logged_in'):
        return render_template('index.html')
    if request.method == 'POST':
        id_data = request.form['id_data']
        name = request.form['name']
        facility = request.form['facility']
        capacity = request.form['capacity']
        description = request.form['description']
        price = request.form['price']
        cur.execute("""
               UPDATE hall
               SET hname=%s, facility=%s, capacity=%s, description=%s, price=%s
               WHERE hid=%s
            """, (name, facility, capacity, description, price, id_data))
        # flash("Data Updated Successfully")
        db.commit()
        return redirect(url_for('halls'))


@app.route('/remove/<string:id_data>', methods=['GET'])
def remove(id_data):
    if not session.get('logged_in'):
        return render_template('index.html')
    cur.execute("DELETE FROM users WHERE uid=%s", (id_data))
    db.commit()
    session['logged_in'] = False
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
