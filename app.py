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



app = Flask(__name__)  # instance of the flask

# config database

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'bimal'
app.config['MYSQL_DB'] = 'eloc_database'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# init mysql
mysql = MySQL(app)

# index page 

@app.route('/',methods=['GET','POST'])
def index():
    # crete cursor
    cur=mysql.connection.cursor()
    #execute 
    result=cur.execute("SELECT * FROM blogpost_tbl ORDER BY blog_id DESC LIMIT 2")
    data=cur.fetchall()
    # commit
    mysql.connection.commit()
    # close connection
    cur.close()
    
    if 'contact_form' in request.form:
        full_name=request.form['full_name']
        contact_email=request.form['email']
        contactno=request.form['contactno']
        address=request.form['address']
        message=request.form['message']
        date=datetime.date.today()
        # create cursor
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO contact_us(full_name,contact_email,contact_mobileno,contact_address,contact_message,date)VALUES(%s,%s,%s,%s,%s,%s)",
                    (full_name,contact_email,contactno,address,message,date))
        #commit to db
        mysql.connection.commit()
        #close connection
        cur.close()
        return redirect(url_for('index'))
    
    if 'news_btn' in request.form:
        news_email=request.form['news_email']
        status='Active'
        # create cursor
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO newslater(email_id,status)VALUES(%s,%s)",
                    (news_email,status))
        #commit to db
        mysql.connection.commit()
        #close connection
        cur.close()
        return redirect(url_for('index'))

    return render_template('index.html',data=data)
# read blog

@app.route('/read_blog/<string:id>',methods=['GET','POST'])
def read_blog(id):
    # crete cursor
    cur=mysql.connection.cursor()
    #execute 
    result=cur.execute("SELECT * FROM blogpost_tbl WHERE blog_id=%s",[id])
    data=cur.fetchone()
    # commit
    mysql.connection.commit()
    # close connection
    cur.close()
    if 'contact_form' in request.form:
        full_name=request.form['full_name']
        contact_email=request.form['email']
        contactno=request.form['contactno']
        address=request.form['address']
        message=request.form['message']
        date=datetime.date.today()
        # create cursor
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO contact_us(full_name,contact_email,contact_mobileno,contact_address,contact_message,date)VALUES(%s,%s,%s,%s,%s,%s)",
                    (full_name,contact_email,contactno,address,message,date))
        #commit to db
        mysql.connection.commit()
        #close connection
        cur.close()
        return redirect(url_for('index'))
    
    if 'news_btn' in request.form:
        news_email=request.form['news_email']
        status='Active'
        # create cursor
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO newslater(email_id,status)VALUES(%s,%s)",
                    (news_email,status))
        #commit to db
        mysql.connection.commit()
        #close connection
        cur.close()
        return redirect(url_for('index'))
    return render_template('read_blog.html',data=data)

@app.route('/ViewAllBlogs',methods=['GET','POST'])
def viewAll_Blogs():
    # crete cursor
    cur=mysql.connection.cursor()
    #execute 
    result=cur.execute("SELECT * FROM blogpost_tbl ORDER BY blog_id DESC")
    data=cur.fetchall()
    # commit
    mysql.connection.commit()
    # close connection
    cur.close()
    if 'contact_form' in request.form:
        full_name=request.form['full_name']
        contact_email=request.form['email']
        contactno=request.form['contactno']
        address=request.form['address']
        message=request.form['message']
        date=datetime.date.today()
        # create cursor
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO contact_us(full_name,contact_email,contact_mobileno,contact_address,contact_message,date)VALUES(%s,%s,%s,%s,%s,%s)",
                    (full_name,contact_email,contactno,address,message,date))
        #commit to db
        mysql.connection.commit()
        #close connection
        cur.close()
        return redirect(url_for('index'))
    
    if 'news_btn' in request.form:
        news_email=request.form['news_email']
        status='Active'
        # create cursor
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO newslater(email_id,status)VALUES(%s,%s)",
                    (news_email,status))
        #commit to db
        mysql.connection.commit()
        #close connection
        cur.close()
        return redirect(url_for('index'))
    return render_template('viewall_blog.html',data=data)


# login page
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        useremail=request.form['useremail']
        password_candidate=request.form['password']
        # create cursor 
        cur = mysql.connection.cursor()
        # get user by name
        result = cur.execute("SELECT * FROM login_tbl WHERE username = %s", [useremail])
        if result > 0:
            # get stored password 
            data = cur.fetchone()
            password = data['password']
            user_type=data['user_flag']
            session['user_type']=user_type
            if password == password_candidate:
                #passed user password
                session['logged_in'] = True
                session['useremail'] = useremail
                if user_type =='user':
                    return redirect(url_for('user_dashboard'))
                if user_type =='party':
                    return redirect(url_for('party_dashboard'))
                if user_type=='admin':
                    return redirect(url_for('admin_dashboard'))
            else:
                error = 'Invalid Username or Password !'
                return render_template('sign-in.html', error=error)
                # close connection
                cur.close()
        else:
            error = 'Sorry! You are not registered with us.'
            return render_template('sign-in.html', error=error)
    return render_template('sign-in.html')

# is logged in funcation to check user is logged in or not 
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You are not authroized, please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

# forgot password
@app.route('/forgot_password/')
def forgot_password():
    return render_template('forgot_password.html')

# sign-up page

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        fullname=request.form['fullname']
        email=request.form['email']
        mobno=request.form['mobno']
        password=request.form['password']
        user_flag='user'
        
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
        return redirect(url_for('signdone'))
    return render_template('sign-up.html')

# thank you  sign-up page
@app.route('/signdone')
def signdone():
    return render_template('thankyou.html')


# party sign-up page
@app.route('/party',methods=['GET','POST'])
def party():
        if request.method == 'POST':
            email=request.form['email']
            password=request.form['password']
            fullname=request.form['fullname']
            mobno=request.form['mobno']
            address=request.form['address']
            usage_type=request.form['gender']
            user_flag='party'
            if usage_type=='CommercialUsage':
                return render_template('payment.html')

        # create cursor
            cur = mysql.connection.cursor()
        # execute query
            cur.execute("INSERT INTO party_profile(full_name,email,mobno,address,usage_type)VALUES (%s,%s,%s,%s,%s)",
                    (fullname,email,mobno,address,usage_type))
            cur.execute("INSERT INTO login_tbl(username,password,user_flag) VALUES(%s,%s,%s)",
                    (email,password,user_flag))
        # commit to db
            mysql.connection.commit()

        #close the connection
            cur.close()

        return render_template('party_sign-up.html')

# take a tour map page
@app.route('/map')
def showMap():
    return render_template('map/map.html')

# places in map 

@app.route('/places',methods=['GET','POST'])
def showPlaces():
    if request.method=='POST':
        searcheloc=request.form['search']
        # create cursor
        cur = mysql.connection.cursor()
        # get data by eloc id
        result = cur.execute("SELECT * FROM eloc_master_tbl WHERE eloc_id = %s", [searcheloc])
        data = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return render_template('map/places.html',data=data)
    return render_template('map/places.html')

# nearby in map 

@app.route('/nearby')
def showNearby():
    return render_template('map/nearby.html')

# directions in map 

@app.route('/directions')
def showDirections():
    return render_template('map/directions.html')

@app.route('/showMap')
def showplacesMap():
    return render_template('map/places/examples/places.html')

# party Module Start From here 

# party dashboard
@app.route('/party/dashboard')
@is_logged_in
def party_dashboard():
    return render_template('/party/party_dashboard.html')

# party API Key 
# API key generation and data inserted into apikeymaster_tbl
@app.route('/party/apikey', methods=['GET', 'POST'])
@is_logged_in
def party_apikey():
    if request.method == 'POST':
        def my_random_string(string_length=10):
            """Returns a random string of length string_length."""
            random = str(
                uuid.uuid4())  # Convert UUID format to a Python string.
            random = random.upper()  # Make all characters uppercase.
            random = random.replace("-", "")  # Remove the UUID '-'.
            return random[0:string_length]  # Return the random string.
        project = request.form['project']
        project_id = project+'-'+my_random_string(6)
        project_name = project
        creation_date = datetime.date.today()
        api_key = uuid.uuid4()
        created_by = session['useremail']
        status = 'Active'

        # create cursor
        cur = mysql.connection.cursor()
        # execute query
        cur.execute("INSERT INTO apikeymaster_tbl (project_id,project_name,creation_date,api_key,created_by,status)VALUES (%s,%s,%s,%s,%s,%s)",
                    (project_id, project_name, creation_date, api_key, created_by, status))
        # commit to db
        mysql.connection.commit()

        #close the connection
        cur.close()
    return render_template('/party/apikey.html')


# API KEY DATA from apikey master table
@app.route('/party/api_manage')
@is_logged_in
def party_apikey_manage():
        # display api key data from database to table
        # create cursor
    cur=mysql.connection.cursor() 
    # fetch api data from database

    party=session['useremail']
    
    result = cur.execute("SELECT * FROM apikeymaster_tbl WHERE created_by = %s", [party])

    apidata=cur.fetchall()
    
    if result > 0:
        return render_template('/party/apikey_manage.html',apidata=apidata)
    else:
        msg='No API  data found in database'
        return render_template('/party/apikey_manage.html',msg=msg) 
     # close connection
    cur.close()
    return render_template('/party/apikey_manage.html',apidata=apidata)

# delete api key 
@app.route('/party/delete_apikey/<string:id>')
@is_logged_in
def delete_apikey(id):
    # crete cursor
    cur=mysql.connection.cursor()
    #execute 
    cur.execute("DELETE FROM apikeymaster_tbl WHERE id=%s",[id])
    # commit
    mysql.connection.commit()
    # close connection
    cur.close()
    return redirect(url_for('party_apikey_manage'))

# API Key class
class ApiKeyForm(Form):
    id=StringField()
    project_id=StringField()
    project_name=StringField()
    creation_date=StringField()
    api_key=StringField()
    created_by=StringField()
    status=StringField()
# edit apikey
@app.route('/party/edit_apikey/<string:id>', methods=['GET','POST'])
@is_logged_in
def edit_apikey(id):
    # create cursor 
    cur=mysql.connection.cursor()
    #get agent by id
    result=cur.execute("SELECT * FROM apikeymaster_tbl WHERE id=%s",[id])

    apikey=cur.fetchone()
    # get form
    form=ApiKeyForm(request.form)
    # populate agent form fields
    #form.id.data=apikey['id']
    form.project_id.data=apikey['project_id']
    form.project_name.data=apikey['project_name']
    form.creation_date.data=apikey['creation_date']
    form.api_key.data=apikey['api_key']
    form.created_by.data=apikey['created_by']
    form.status.data=apikey['status']

    if 'delbtn' in request.form:
        cur=mysql.connection.cursor()
        cur.execute("DELETE FROM apikeymaster_tbl WHERE id=%s",[id])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('party_apikey_manage'))

    if request.method == 'POST':
        project_name=request.form['project_name']
        # create cursor 
        cur = mysql.connection.cursor()
        # execute
        cur.execute("UPDATE apikeymaster_tbl SET project_name=%s WHERE id=%s",(project_name,id))
        # commit
        mysql.connection.commit()
        # close connection
        cur.close()
        flash('API Key info updated and saved successfully','success')
        return redirect(url_for('party_apikey_manage'))
    return render_template('/party/edit_apikey.html',form=form)

# API key generation and data inserted into apikeymaster_tbl
@app.route('/party/feedback', methods=['GET', 'POST'])
@is_logged_in
def party_feedback():
    if request.method == 'POST':
        feedback_body = request.form['feedback_body']
        date = datetime.date.today()
        feedback_by = session['useremail']
        status = 'Active'
        # create cursor
        cur = mysql.connection.cursor()
        # execute query
        cur.execute("INSERT INTO feedback_tbl (feedback_body,date,feedback_by,status)VALUES (%s,%s,%s,%s)",
                    (feedback_body, date,feedback_by, status))
        # commit to db
        mysql.connection.commit()

        #close the connection
        cur.close()
        return redirect(url_for('party_feedback'))
    return render_template('/party/feedback.html')


# Party module ends here


# common functions for all module start from here 

# get eloc 
@app.route('/common/geteloc', methods=['GET','POST'])
@is_logged_in
def getEloc():
    if request.method == 'POST':
        residency_type = request.form['resident']
        hnobldg = request.form['hnobldg']
        street = request.form['street']
        landmark = request.form['landmark']
        area = request.form['area']
        village_town = request.form['villagetown']
        pincode = request.form['pincode']
        cur=mysql.connection.cursor()
        #get data by pincode
        result=cur.execute("SELECT * FROM pincode_data WHERE pincode=%s",[pincode])
        data=cur.fetchone()
        lat = request.form['lat']
        lng = request.form['lng']
        formatted_add=hnobldg+', '+street+', '+landmark+', '+area+', '+village_town+', '+pincode+', '+data['district']+', '+data['state']
        runningadd = formatted_add
        generated_by = session['useremail']
        eloc_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        # create cursor
        cur = mysql.connection.cursor()
        # data insert into location registeration table
        cur.execute("INSERT INTO eloc_master_tbl(eloc_id,hno,street,landmark,area,village_town,pincode,lat,lng,runningadd,residency_type,generated_by)VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (eloc_id, hnobldg, street, landmark, area,village_town, pincode, lat,lng, runningadd,residency_type,generated_by))
        # commit to db
        mysql.connection.commit()

        #close the connection
        cur.close()
        return render_template('/common/geteloc.html',msg=eloc_id)
        return redirect(url_for('getEloc'))
    return render_template('/common/geteloc.html')

# add Places
@app.route('/common/addplaces', methods=['GET','POST'])
@is_logged_in
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
@app.route('/common/eloclog',methods=['GET','POST'])
@is_logged_in
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
# get QR code image from database 
@app.route('/common/get_qrimg')
def get_qrimg():
    img_buf = cStringIO.StringIO()
    # filename='static/abc.png'
    img = random_qr()
    img.save(img_buf)
    img_buf.seek(0)
    return send_file(img_buf, mimetype='image/png')

# QR Code
@app.route('/common/generateQR')
@is_logged_in
def generateQRCode():
    return render_template('/common/qrcode.html')

# Address Card with QR Code
@app.route('/common/generateCard')
@is_logged_in
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
@app.route('/common/printCard')
@is_logged_in
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
@app.route('/common/nearby')
@is_logged_in
def nearBy():
    return render_template('/common/nearbyplaces.html')

# Search eLoc
@app.route('/common/searcheloc',methods=['GET','POST'])
@is_logged_in
def searchEloc():
    if request.method == 'POST':
        eloc = request.form['eloc_id']
        cur=mysql.connection.cursor()
        result = cur.execute("SELECT * FROM eloc_master_tbl left join pincode_data using(pincode) WHERE eloc_id = %s", [eloc])
        if result > 0:
            data=cur.fetchone()
            #commit to db
            mysql.connection.commit()
            #close connection
            cur.close()
            return render_template('/common/searcheloc.html',data=data)
        else:
            error='No data found in database, Please enter correct eLoc ID'
            return render_template('/common/searcheloc.html',err=error)
    return render_template('/common/searcheloc.html')

# directions
@app.route('/common/directions')
@is_logged_in
def getDirections():
    return render_template('/common/directions.html')


# Location History
@app.route('/common/locationhistory')
@is_logged_in
def locationHistory():
    return render_template('/common/locationhistory.html')

# common functions for all module ends here 

# user module start from here 
# user dashboard
@app.route('/user/dashboard')
@is_logged_in
def user_dashboard():
    return render_template('/user/user_dashboard.html')

# user module ends here

# admin module start from here 

# admin dashboard
@app.route('/admin/dashboard')
@is_logged_in
def admin_dashboard():
    return render_template('/admin/admin_dashboard.html')

# Admin Blog Post Generation
@app.route('/admin/blogpost')
@is_logged_in
def blogPost():
    user_email=session['useremail']
    # create cursor
    cur=mysql.connection.cursor()
    result=cur.execute("SELECT * FROM blogpost_tbl WHERE post_by=%s",[user_email])
    data=cur.fetchall()
    #commit to db
    mysql.connection.commit()
    #close connection
    cur.close()
    return render_template('/admin/blogpost.html',data=data)

# New Blog Post
@app.route('/admin/newblog',methods=['GET','POST'])
@is_logged_in
def newBlogPost():
    if request.method=='POST':
        title=request.form['title']
        blogbody=request.form['body']
        created_by=session['useremail']
        # create cursor
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO blogpost_tbl(blog_title,blog_body,post_by)VALUES(%s,%s,%s)",
                    (title,blogbody,created_by))
        #commit to db
        mysql.connection.commit()
        #close connection
        cur.close()
        return redirect(url_for('newBlogPost'))
    return render_template('/admin/newblog.html')

# delete blog post 
@app.route('/admin/delete_blogpost/<string:id>')
@is_logged_in
def delete_blogPost(id):
    # crete cursor
    cur=mysql.connection.cursor()
    #execute 
    cur.execute("DELETE FROM blogpost_tbl WHERE blog_id=%s",[id])
    # commit
    mysql.connection.commit()
    # close connection
    cur.close()
    return redirect(url_for('blogPost'))

# view blog post 
@app.route('/admin/view_blogpost/<string:id>')
@is_logged_in
def view_blogPost(id):
    # crete cursor
    cur=mysql.connection.cursor()
    #execute 
    result=cur.execute("SELECT * FROM blogpost_tbl WHERE blog_id=%s",[id])
    data=cur.fetchone()
    # commit
    mysql.connection.commit()
    # close connection
    cur.close()
    return render_template('/admin/viewblog.html',data=data)

# edit blog post data 
@app.route('/admin/edit_blogpost/<string:id>', methods=['GET','POST'])
@is_logged_in
def edit_blogPost(id):
    # create cursor 
    cur=mysql.connection.cursor()
    #get agent by id
    result=cur.execute("SELECT * FROM blogpost_tbl WHERE blog_id=%s",[id])

    data=cur.fetchone()
    # commit
    mysql.connection.commit()
    # close connection
    cur.close()
    if request.method=='POST':
        blog_title=request.form['title']
        blog_body=request.form['body']
        # create cursor
        cur= mysql.connection.cursor()
        cur.execute("UPDATE blogpost_tbl SET blog_title=%s,blog_body=%s WHERE blog_id=%s",(blog_title,blog_body,id))
        # commit
        mysql.connection.commit()
        # close connection
        cur.close()
        return redirect(url_for('blogPost'))
    return render_template('/admin/editblog.html',data=data)


# API KEY DATA from apikey master table
@app.route('/admin/api_manage', methods=['GET', 'POST'])
@is_logged_in
def admin_apikey_manage():
    if request.method == 'POST':
        project_name = request.form['project_name']
        purpose=request.form['purpose']
        creation_date = datetime.date.today()
        api_key = uuid.uuid4()
        created_by = session['useremail']
        status = 'Active'
        # create cursor
        cur = mysql.connection.cursor()
        # execute query
        cur.execute("INSERT INTO admin_apikey_master (project_name,purpose,creation_date,api_key,created_by,status)VALUES (%s,%s,%s,%s,%s,%s)",
                    (project_name,purpose,creation_date, api_key, created_by, status))
        # commit to db
        mysql.connection.commit()
        #close the connection
        cur.close()
        # display api key data from database to table
        # create cursor
        return redirect(url_for('admin_apikey_manage'))
    cur=mysql.connection.cursor() 
    # fetch api data from database

    user_email=session['useremail']
    
    result = cur.execute("SELECT * FROM admin_apikey_master WHERE created_by = %s and status='Active'", [user_email])

    apidata=cur.fetchall()
    
    if result > 0:
        return render_template('/admin/admin_apikey.html',apidata=apidata)
    else:
        msg='No API  data found in database'
        return render_template('/admin/admin_apikey.html',msg=msg) 
     # close connection
    cur.close()
    return render_template('/admin/admin_apikey.html',apidata=apidata)

# delete api key 
@app.route('/admin/delete_apikey/<string:id>')
@is_logged_in
def admind_delete_apikey(id):
    # crete cursor
    cur=mysql.connection.cursor()
    #execute 
    cur.execute("DELETE FROM admin_apikey_master WHERE apikeyid=%s",[id])
    # commit
    mysql.connection.commit()
    # close connection
    cur.close()
    return redirect(url_for('admin_apikey_manage'))

# edit apikey
@app.route('/admin/edit_apikey/<string:id>', methods=['GET','POST'])
@is_logged_in
def admin_edit_apikey(id):
    # create cursor 
    cur=mysql.connection.cursor()
    #get agent by id
    result=cur.execute("SELECT * FROM admin_apikey_master WHERE apikeyid=%s and status='Active'",[id])

    apikey=cur.fetchone()

    if 'updatebtn' in request.form:
        project_name=request.form['project_name']
        purpose=request.form['purpose']
        # create cursor 
        cur = mysql.connection.cursor()
        # execute
        cur.execute("UPDATE admin_apikey_master SET project_name=%s,purpose=%s WHERE apikeyid=%s",(project_name,purpose,id))
        # commit
    if 'changebtn' in request.form:
        cur.execute("UPDATE admin_apikey_master SET status='De-Activate' WHERE apikeyid=%s",(id))

        mysql.connection.commit()
        # close connection
        cur.close()
        flash('API Key info updated and saved successfully','success')
        return redirect(url_for('admin_apikey_manage'))
    return render_template('/admin/edit_apikey.html',apikey=apikey)

# admin module ends here 

# api code starts from here 

# api eloc search 
@app.route('/api/search/eloc/',methods=['GET'])
def api_elocSearch():
    if request.method=='GET':
        key=request.args['key']
        eloc=request.args['eloc']
        r = {}
        if key=="" and eloc=="":
            error="Invalid request"
            r['status']='Failed'
            r['error']=error
        else:
            cur = mysql.connection.cursor()
            # get get eloc data from eloc_master table
            result = cur.execute("select * from apikeymaster_tbl where api_key = %s", [key])
            if result > 0:
                result=cur.execute("select eloc_master_tbl.eloc_id,eloc_master_tbl.hno,eloc_master_tbl.street,eloc_master_tbl.landmark,eloc_master_tbl.area,eloc_master_tbl.village_town,pincode_data.pincode,pincode_data.district,pincode_data.state,eloc_master_tbl.lat,eloc_master_tbl.lng,eloc_master_tbl.residency_type from eloc_master_tbl,pincode_data where eloc_master_tbl.pincode=pincode_data.pincode and eloc_id =%s", [eloc])
                #result = cur.execute("select * from eloc_master_tbl inner join pincode_data using(pincode) where eloc_id = %s", [eloc])
                data = cur.fetchone()
                print data
                r['status'] = "Success"
                r['result'] = data
            else:
                api_error="API key is invalid"
                r['status']='Failed'
                r['api_error']=api_error
    return demjson.encode(r)


# api place search 
@app.route('/api/search/places/',methods=['GET','POST'])
def api_placesSearch():

    return demjson.encode(r)

# api pincode search 
@app.route('/api/search/pincode/',methods=['GET','POST'])
def api_pincodeSearch():
    if request.method=='GET':
        key=request.args['key']
        pincode=request.args['pincode']
        r = {}
        if key=="" and pincode=="":
            error="Invalid request"
            r['status']='Failed'
            r['error']=error
        else:
            cur = mysql.connection.cursor()
            # get get eloc data from eloc_master table
            result = cur.execute("select * from apikeymaster_tbl where api_key = %s", [key])
            if result > 0:
                result = cur.execute("select * from  pincode_data  where PINCODE = %s", [pincode])
                data = cur.fetchone()
                r['status'] = "Success"
                r['result'] = data
            else:
                api_error="API key is invalid"
                r['status']='Failed'
                r['api_error']=api_error
    return demjson.encode(r)


# api code ends here

# checking app is running or not and defining secrete key for session
if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug=True)
