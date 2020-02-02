from flask import Flask, render_template, request
import sqlite3
from werkzeug import secure_filename
from flask import Flask, render_template, request,make_response,Response
from werkzeug import secure_filename
from hashlib import sha256
import pandas as pd
import hashlib
import base64
import pandas as pd
import gmplot
import numpy as np
from hashlib import sha256
import os, io
from google.cloud import vision
import base64
import requests
import json
from sklearn.model_selection import train_test_split

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"ServiceAccountToken.json"
client = vision.ImageAnnotatorClient()
s_no=1
x=False
app = Flask(__name__)

def create_model(ah,atemp,pH,rain):
    data=pd.read_csv('cpdata.csv')
    label= pd.get_dummies(data.label).iloc[: , 1:]
    data= pd.concat([data,label],axis=1)
    data.drop('label', axis=1,inplace=True)
    train=data.iloc[:, 0:4].values
    test=data.iloc[: ,4:].values
    X_train,X_test,y_train,y_test=train_test_split(train,test,test_size=0.3)
    from sklearn.preprocessing import StandardScaler
    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)
    from sklearn.tree import DecisionTreeRegressor
    clf=DecisionTreeRegressor()
    clf.fit(X_train,y_train)
    l=[]
    l.append(ah)
    l.append(atemp)
    l.append(pH)
    l.append(rain)
    predictcrop=[l]
    predictcrop=sc.transform(predictcrop)
    crops=['wheat','mungbean','Tea','millet','maize','lentil','jute','cofee','cotton','ground nut','peas','rubber','sugarcane','tobacco','kidney beans','moth beans','coconut','blackgram','adzuki beans','pigeon peas','chick peas','banana','grapes','apple','mango','muskmelon','orange','papaya','watermelon','pomegranate']
    cr='rice'
    predictions = clf.predict(predictcrop)
    count=0
    for i in range(0,30):
        if(predictions[0][i]==1):
            c=crops[i]
            count=count+1
            break;
        i+=1
    if(count==0):
        return cr
    else:
        return c

@app.route('/')
def home():
   return "Home Page"

def verify_from_database(username,password):
    users=dict()
    conn=sqlite3.connect('agriculture.db')
    c=conn.cursor()
    var=False
    c.execute('SELECT * FROM login')
    data=c.fetchall()
    for row in data:
        users[row[0]]=row[1]
    for key,value in users.items():
        if username == key and password == value:
            var=True
    if var == False:
        print('Invalid Username or password')
        return False
    else:
        print('Login Successful!')
        return True
    c.close()
    conn.close()

def write_to_register(email,name,aadhar,designation,tehsil,bdate,password,csv_path):
    conn = sqlite3.connect('agriculture.db')
    c = conn.cursor()
    c.execute("INSERT INTO register(email, name, aadhar, designation,tehsil,bdate,password) VALUES (?, ?, ?, ?, ?, ?, ?)",
          (email, name, aadhar, designation,tehsil,bdate,password,csv_path))

    conn.commit()
    c.close()
    conn.close()

def get_location():
    import re
    import json
    import urllib.request


    url = 'http://ipinfo.io/json'
    response = urllib.request.urlopen(url)
    data = json.load(response)
    x=data['loc'].split(',')
    lat=x[0]
    long=x[1]
    return (lat,long)
def get_temp_hum():
    new2=requests.get('https://weather.ls.hereapi.com/weather/1.0/report.json?product=observation&latitude={}&longitude={}&oneobservation=true&apiKey=oKkfu_gp7HWQNffIFEWveyk2UJgCoFjpFCO55DWpyHo'.format(get_location()[0],get_location()[1])).json()
    temperature=new2['observations']['location'][0]['observation'][0]['temperature']
    humidity=new2['observations']['location'][0]['observation'][0]['humidity']
    return temperature,humidity

def write_to_land_records(name,area,district,taluka,village,phone,aadhar,file_path,file_path_csv):
    conn = sqlite3.connect('agriculture.db')
    c = conn.cursor()
    c.execute("INSERT INTO land_records(name, area, district, taluka,village,phone,aadhar,file_path,csv_path) VALUES (?, ?, ?, ?, ?, ?, ?,?,?)",
          (name, area, district, taluka,village,phone,aadhar,file_path,file_path_csv))

    conn.commit()
    c.close()
    conn.close()

def get_survey_number():
    cases_dict=dict()
    conn=sqlite3.connect('agriculture.db')
    c=conn.cursor()
    c.execute('SELECT survey_no FROM land_records')
    data = c.fetchall()
    c.close()
    conn.close()
    return data[-1][0]



def write_to_documents(survey_no,file_path,ocr_path,block,hash):
    conn = sqlite3.connect('agriculture.db')
    c = conn.cursor()
    c.execute("INSERT INTO documents(survey_no, file_path, ocr_path, block,hash) VALUES (?, ?, ?, ?, ?)",
          (survey_no, file_path, ocr_path, block,hash))

    conn.commit()
    c.close()
    conn.close()

def write_to_feedback(name,email,phone,complaint):
    conn = sqlite3.connect('agriculture.db')
    c = conn.cursor()
    c.execute("INSERT INTO feedback(name, email, phone, complaint) VALUES (?, ?, ?, ?)",
          (name, email, phone,complaint))

    conn.commit()
    c.close()
    conn.close()


def read_from_db():
    cases_dict=dict()
    conn=sqlite3.connect('agriculture.db')
    c=conn.cursor()
    c.execute('SELECT survey_no,name,area,district,phone FROM land_records')
    data = c.fetchall()
    c.close()
    conn.close()
    #print(data)
    return data


def read_for_view(survey_no):
    cases_dict=dict()
    conn=sqlite3.connect('agriculture.db')
    c=conn.cursor()
    c.execute('SELECT * FROM land_records WHERE survey_no = "{}"'.format(survey_no))
    data = c.fetchall()
    print(data)
    c.close()
    conn.close()
    return data


@app.route('/register')
def register():
   return render_template('register.html')

@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
    global x
    if request.method == 'POST':
        res=request.form
        email=res['email']
        password=res['password']
        print(res)
        x=verify_from_database(email,password)
    if x==True:
        new_data=read_from_db()
        return render_template('dashboard.html',new_data=new_data)
    else:
        return 'Invalid Username or Password'

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        res=request.form
        email=res['email']
        name=res['name']
        aadhar=res['aadhar']
        designation=res['designation']
        tehsil=res['tehsil']
        bdate=res['bdate']
        password=res['password']
        write_to_register(email,name,aadhar,designation,tehsil,bdate,password)
        return render_template('login.html')
    return render_template('login.html')

@app.route('/crop')
def crop():
   return render_template('form_basic.html')


@app.route('/certificate')
def certificate():
   return render_template('7_12.html')


@app.route('/landing')
def landing():
    global x
    x=False
    return render_template('landing.html')

@app.route('/certificateresult',methods=['GET','POST'])
def certificateresult():
    if request.method == 'POST':
        res=request.form
        f = request.files['fileToUpload']
        f.save(secure_filename(f.filename))
        f_csv=request.files['csv_file']
        f_csv.save(secure_filename(f_csv.filename))
        file_path=r'/home/yash/TechGits/'+f.filename
        file_path_csv=r'/home/yash/TechGits/'+f_csv.filename
        print(res)
        name=res['name']
        area=res['area']
        district=res['district']
        taluka=res['taluka']
        village=res['village']
        phone=res['phone']
        aadhar=res['aadhar']
        write_to_land_records(name,area,district,taluka,village,phone,aadhar,file_path,file_path_csv)
        survey_no=get_survey_number()
        print(survey_no)
        image_path = '/home/yash/TechGits/'+f.filename
        print(image_path)
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()
        image = vision.types.Image(content=content)
        response = client.text_detection(image=image)  # returns TextAnnotation
        df = pd.DataFrame(columns=['locale', 'description'])
        print(df)
        texts = response.text_annotations
        for text in texts:
            df = df.append(
                dict(
                    locale=text.locale,
                    description=text.description
                ),
                ignore_index=True
            )

        print(df['description'][0])
        print(type(df['description'][0]))
        new_file=f.filename+'.txt'
        print(new_file)
        file1 = open(new_file,"w")
        file1.write(df['description'][0])
        file1.close()
        ocr_path='/home/yash/TechGits/'+new_file
        hash=sha256(df['description'][0].encode()).hexdigest()
        dictToSend = {'sender':'de8327a07f724e1b8834dd1f2fce62f9','recipient':'someone-other-address','amount':hash}
        res = requests.post('http://localhost:8000/transactions/new',json=dictToSend)
        print('response from server:',res.text)
        res1 = requests.get('http://localhost:8000/mine')
        print(res1)
        data=res1.json()
        block=res.text
        write_to_documents(survey_no,file_path,ocr_path,block,hash)
    return render_template('geomapoutput.html')

@app.route('/cropresult',methods=['GET','POST'])
def cropresult():
    if request.method == 'POST':
        print(request.form)
        if  request.form['form1'] == 'predict':
            res=request.form
            x=create_model(float(res['hum']),float(res['temp']),float(res['ph']),float(res['rainfall']))
            crop_image_path='../static/crop_images/{}.jpg'.format(x)
            return render_template('form_basic.html',predicted_crop=x,crop_image_path=crop_image_path)
        elif request.form['form1'] =='take_my_location':
            temp,hum=get_temp_hum()
            x=create_model(float(hum),float(temp),float(7.0),float(100))
            print(float(hum),float(temp),float(7.0),float(100))
            crop_image_path='../static/crop_images/{}.jpg'.format(x)
            return render_template('form_basic.html',predicted_crop=x,crop_image_path=crop_image_path)
@app.route('/view/<survey_no>')
def view(survey_no):
    new_data=read_for_view(survey_no)
    global s_no

    return render_template('view.html',data=new_data)
@app.route('/feedback',methods=['GET','POST'])
def feedback():
    if request.method == 'POST':
        res=request.form
        name=res['name']
        email=res['email']
        complaint=res['complaint']
        phone=res['phone']
        write_to_feedback(name,email,phone,complaint)
        return render_template('feedback.html')
    return render_template('feedback.html')

@app.route('/geomap')
def geomap():
    df=pd.read_csv('final.csv')
    latitude_list = list(df['latitude'])
    longitude_list=list(df['longitude'])
    gmap5 = gmplot.GoogleMapPlotter(21.91005,  77.95589, zoom=20)
    #gmap5 = gmplot.GoogleMapPlotter(30.3164945, 78.03219179999999, 13)
    gmap5.scatter( latitude_list, longitude_list, '# FF0000',  marker = False)
    #gmap5.polygon(latitude_list, longitude_list, color = 'cornflowerblue')
    gmap5.polygon(latitude_list, longitude_list,  color = 'cornflowerblue')
    #gmap5.draw(r"C:\Users\USER\Desktop\map15.html")
    gmap5.draw(r"/home/yash/TechGits/templates/map15.html")
    return render_template('map15.html')

if __name__ == '__main__':
    app.run(debug = True,host='0.0.0.0')
