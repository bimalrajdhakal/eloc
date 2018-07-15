from flask import Flask, render_template, flash, redirect, request, url_for, session, logging,send_file
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,TextField,PasswordField
from functools import wraps
import uuid
import qrcode
import cStringIO
import random,string
import datetime
import demjson



api = Flask(__name__)  # instance of the flask

# config database

api.config['MYSQL_HOST'] = 'localhost'
api.config['MYSQL_USER'] = 'root'
api.config['MYSQL_PASSWORD'] = 'bimal'
api.config['MYSQL_DB'] = 'eloc_database'
api.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# init mysql
mysql = MySQL(api)


# login page
@api.route('/eloc/api/login',methods=['GET','POST'])
def login():
    if request.method=='GET':
        useremail=request.args['useremail']
        password_candidate=request.args['password']
        # create cursor 
        cur = mysql.connection.cursor()
        # get user by name
        result = cur.execute("SELECT * FROM login_tbl WHERE user_flag='user' and username = %s", [useremail])
        r = {}
        if result > 0:
            # get stored password 
            data = cur.fetchone()
            password = data['password']
            user_type=data['user_flag']
            session['user_type']=user_type
            if password == password_candidate:
                #passed user password
                r['status'] = "Success"
                #r['result'] = data
                # connection close
                cur.close()
                return demjson.encode(r)
            else:
                error = 'Invalid Username or Password !'
                r['status']='Failed'
                r['error']=error
                return demjson.encode(r)
        else:
            error = 'Sorry! You are not registered with us.'
            r['status']='NF'
            r['error']=error
            return demjson.encode(r)
    # close connection
        cur.close()
    return demjson.encode(r)

# sign-up page

@api.route('/eloc/api/signup',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        fullname=request.form['fullname']
        email=request.form['email']
        mobno=request.form['mobno']
        password=request.form['password']
        user_flag='user'
        r = {}
        # create cursor
        cur = mysql.connection.cursor()
        # execute query
        cur.execute("INSERT INTO profile_tbl(fullname,email,mobno)VALUES (%s,%s,%s)",
                    (fullname,email,mobno))
        cur.execute("INSERT INTO login_tbl(username,password,user_flag) VALUES(%s,%s,%s)",
                    (email,password,user_flag))
        # commit to db
        mysql.connection.commit()

        #close the connection
        cur.close()
        r['status'] = "Success"
    return demjson.encode(r)


# common functions for all module start from here 

# get eloc 
@api.route('/eloc/api/geteloc', methods=['GET','POST'])
def getEloc():
    if request.method == 'POST':
        residency_type = request.form['resident']
        hnobldg = request.form['hnobldg']
        street = request.form['street']
        landmark = request.form['landmark']
        area = request.form['area']
        village_town = request.form['villagetown']
        pincode = request.form['pincode']
        useremail = request.form['useremail']
        cur=mysql.connection.cursor()
        #get data by pincode
        result=cur.execute("SELECT * FROM pincode_data WHERE pincode=%s",[pincode])
        data=cur.fetchone()
        lat = request.form['lat']
        lng = request.form['lng']
        formatted_add=hnobldg+', '+street+', '+landmark+', '+area+', '+village_town+', '+pincode+', '+data['district']+', '+data['state']
        runningadd = formatted_add
        generated_by = useremail
        lat = request.form['lat']
        lng = request.form['lng']
        eloc_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        r = {}
        # create cursor
        cur = mysql.connection.cursor()
        # data insert into location registeration table
        cur.execute("INSERT INTO eloc_master_tbl(eloc_id,hno,street,landmark,area,village_town,pincode,lat,lng,runningadd,residency_type,generated_by)VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (eloc_id, hnobldg, street, landmark, area,village_town, pincode, lat,lng, runningadd,residency_type,generated_by))
        # commit to db
        mysql.connection.commit()

        #close the connection
        cur.close()
        r['status'] = "Success"
        r['eloc_id']= eloc_id
    return demjson.encode(r)

# add Places
@api.route('/common/addplaces', methods=['GET','POST'])
def addPlaces():
    if request.method == 'POST':
        poicat = request.form['poicat']
        hnobldg = request.form['hnobldg']
        street = request.form['street']
        landmark = request.form['landmark']
        area = request.form['area']
        village_town = request.form['villagetown']
        pincode = request.form['pincode']
        lat = request.form['lat']
        lng = request.form['lng']
        runningadd = request.form['runningadd']
        generated_by = session['useremail']
        place_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        # create cursor
        cur = mysql.connection.cursor()
        # data insert into places registeration table
        cur.execute("INSERT INTO places_master_tbl(place_id,hno,street,landmark,area,village_town,pincode,lat,lng,runningadd,poi_cat)VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (place_id, hnobldg, street, landmark, area,village_town, pincode, lat,lng, runningadd,poicat))
        # commit to db
        mysql.connection.commit()

        #close the connection
        cur.close()
        return redirect(url_for('addPlaces'))

    return render_template('/common/addplaces.html')

# eloc log
@api.route('/common/eloclog',methods=['GET','POST'])
def elocLog():
    user_email=session['useremail']
    cur=mysql.connection.cursor()
    result=cur.execute("SELECT * FROM eloc_log_master WHERE created_by=%s",[user_email])
    data=cur.fetchall()
    #commit to db
    mysql.connection.commit()
    #close connection
    cur.close()

    # category add modal request
    if 'cat_add_btn' in request.form:
        cat_name=request.form['cat_name']
        cat_eloc=request.form['cat_eloc']
        # create cursor
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO eloc_log_master(log_category,eloc_address,created_by)VALUES(%s,%s,%s)",
                    (cat_name,cat_eloc,user_email))
        #commit to db
        mysql.connection.commit()
        #close connection
        cur.close()
        return redirect(url_for('elocLog'))
    # work eloc modal request
    if 'work_eloc_btn' in request.form:
        work_eloc=request.form['work_eloc']
        log_category='Work'
        # create cursor
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO eloc_log_master(log_category,eloc_address,created_by)VALUES(%s,%s,%s)",
                    (log_category,work_eloc,user_email))
        #commit to db
        mysql.connection.commit()
        #close connection
        cur.close()
        return redirect(url_for('elocLog'))
    # Home eloc modal request
    if 'home_eloc_btn' in request.form:
        home_eloc=request.form['home_eloc']
        log_category='Home'
        # create cursor
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO eloc_log_master(log_category,eloc_address,created_by)VALUES(%s,%s,%s)",
                    (log_category,home_eloc,user_email))
        #commit to db
        mysql.connection.commit()
        #close connection
        cur.close()
        return redirect(url_for('elocLog'))
    return render_template('/common/eloclog.html',data=data)


def random_qr():
    qr = qrcode.QRCode(version=1,error_correction=qrcode.constants.ERROR_CORRECT_L,
                       box_size=3,
                       border=2)
    generated_by = session['useremail']

    cur = mysql.connection.cursor()
    # get data by eloc id
    result = cur.execute("SELECT * FROM eloc_master_tbl right join pincode_data using(pincode) WHERE generated_by = %s", [generated_by])
    data = cur.fetchone()
    qrdata=demjson.encode(data)
    mysql.connection.commit()
    cur.close()
    qr.add_data(qrdata)
    qr.make(fit=True)
    img = qr.make_image()
    return img

# QR Code
@api.route('/eloc/api/generateQR',methods=['GET','POST'])
def generateQRCode():
    if request.method == 'GET':
        generated_by = request.args['useremail']
        cur = mysql.connection.cursor()
        r = {}
        # get data by eloc id
        result = cur.execute("SELECT * FROM eloc_master_tbl left join pincode_data using(pincode) WHERE generated_by = %s limit 1", [generated_by])
        elocdata = cur.fetchall()
        
        #qrdata=demjson.encode(elocdata)
        mysql.connection.commit()
        r['status'] = "Success"
        r['elocresult'] = elocdata
        #r['qrdata'] = qrdata
        cur.close()
    return demjson.encode(r)

# Search eLoc Id 
@api.route('/eloc/api/searchEloc',methods=['GET','POST'])
def searchElocId():
    if request.method == 'GET':
        eloc_id = request.args['eloc_id']
        print eloc_id
        cur = mysql.connection.cursor()
        r = {}
        # get data by eloc id
        result = cur.execute("SELECT * FROM eloc_master_tbl left join pincode_data using(pincode) WHERE eloc_id = %s", [eloc_id])
        elocdata = cur.fetchall()
        mysql.connection.commit()
        r['status'] = "Success"
        r['elocresult'] = elocdata
        cur.close()
    return demjson.encode(r)

# Address Card with QR Code
@api.route('/common/generateCard')
def generateCard():
    generated_by = session['useremail']

    cur = mysql.connection.cursor()
    # get data by eloc id
    result = cur.execute("SELECT * FROM eloc_master_tbl left join pincode_data using(pincode) WHERE generated_by = %s", [generated_by])
    data = cur.fetchone()
    mysql.connection.commit()
    cur.close()

    return render_template('/common/addresscard.html',data=data)

# Print Address Card with QR Code
@api.route('/common/printCard')
def printCard():
    generated_by = session['useremail']

    cur = mysql.connection.cursor()
    # get data by eloc id
    result = cur.execute("SELECT * FROM eloc_master_tbl left join pincode_data using(pincode) WHERE generated_by = %s", [generated_by])
    data = cur.fetchone()
    mysql.connection.commit()
    cur.close()

    return render_template('/common/print_card.html',data=data)

# Near by Places
@api.route('/common/nearby')
def nearBy():
    return render_template('/common/nearbyplaces.html')

# Search eLoc
@api.route('/common/searcheloc')
def searchEloc():
    return render_template('/common/searcheloc.html')

# directions
@api.route('/common/directions')
def getDirections():
    return render_template('/common/directions.html')


# Location History
@api.route('/common/locationhistory')
def locationHistory():
    return render_template('/common/locationhistory.html')

# common functions for all module ends here 


if __name__ == '__main__':
    api.secret_key = 'secret123'
    api.run('192.168.43.86',debug=True,port=5000)