from flask import Flask, render_template , request ,redirect
from flask import session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import json
import os
from werkzeug.utils import secure_filename
from datetime import datetime



with open ('config.json','r') as c :
    param = json.load(c)['param']

local_server = True

app = Flask(__name__)
app.secret_key = 'super-secret-key'

app.config ['UPLOAD_FOLDER'] = param['upload_location']

if(local_server):
    app.config["SQLALCHEMY_DATABASE_URI"] = param['local_uri']
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = param['prod_uri']
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # to suppress a warning

db = SQLAlchemy(app)

class Contacts(db.Model):
 sno = db.Column(db.Integer, primary_key=True , autoincrement=True)
 name = db.Column(db.String(80), nullable=False)
 phone_num = db.Column(db.String(12), nullable=False)
 msg = db.Column(db.String(120), nullable=False)
 date = db.Column(db.String(12), nullable=True)
 email = db.Column(db.String(20), nullable=False)

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(140), nullable=False)
    tagline = db.Column(db.String(140), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file  = db.Column(db.String(12), nullable=True)



@app.route('/')
def home():
    posts = Posts.query.filter_by().all()[0:5]
    return render_template('index.html', page_class='home',param=param,posts=posts)



@app.route("/post/<post_slug>",methods=['GET'])

def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    #print(post.content)  # Add this line to inspect the content value

    return render_template('post.html', page_class='post_route',param=param,post=post)

@app.route("/edit/<sno>",methods=['GET',"POST"])
def edit(sno):
    if "user" in session and session['user'] == param['admin_user']:
        if  request.method == "POST":
            
            box_title = request.form.get("title")
            tline = request.form.get("tline")
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date = datetime.now()
        
            if sno == "0":
                post = Posts(title=box_title, tagline = tline, slug=slug,date=date , content = content , img_file = img_file)
                db.session.add(post)
                db.session.commit()
               
            else:
                post= Posts.query.filter_by(sno=sno).first()
                post.title= box_title
                post.tagline=tline
                post.slug=slug
                post.img_file= img_file
                post.date= date
                db.session.commit()
                return redirect('/edit/'+sno)
        post= Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html',param=param,post=post,sno=sno)



@app.route('/about')
def about():

    return (render_template('about.html', page_class='about',param=param))


@app.route("/dashboard", methods = ['GET', 'POST'])
def dashboard():

    # checking user already login or not
    if "user" in session and session['user']==param['admin_user']:
     
      posts = Posts.query.all()

      return render_template("dashboard.html", param=param , posts= posts)
    
    if (request.method=='POST'):
        username = request.form.get('uname')
        userpass = request.form.get('pass')

        if (username == param['admin_user'] and userpass == param['admin_pass']):
             # session 
            session['user']=username
            posts = Posts.query.all()
            return render_template("dashboard.html", param=param , posts= posts)
        else :
            return 'incorrect password'
    return render_template("login.html",page_class='dashboard',param = param )
@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    if "user" in session and session['user']==param['admin_user']:
        if (request.method=='POST'):
            f = request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
        return "Uploaded succesfully"

@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/dashboard')

@app.route("/delet/<sno>",methods=['GET',"POST"])
def delet(sno):
    if "user" in session and session['user'] == param['admin_user']:
        post= Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')



@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if (request.method=='POST'):
        '''ADD ENTRY TO THE DATABASE'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts (name=name, phone_num=phone, msg=message, date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        
    return render_template('contact.html', page_class='contact',param = param)
@app.route('/post')
def blog():
    return render_template('post.html', page_class='post',param = param)


if __name__ == '__main__':
    app.run(debug=True)
