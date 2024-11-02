from flask import Flask
from flask import redirect,url_for,render_template, request, flash,session,jsonify
import json, requests, time
from datetime import datetime, timedelta

app = Flask(__name__)

app.config["SECRET_KEY"]="3d24d4166799d413ef8522accb97ff35da6534982ae31565625efdc42429369b"

app_url="analysis.inticure.com/0"

base_url = 'https://api.inticure.online/'

#api urlss
questionnaire_api="api/analysis/questionnaire?category_id="
analysis_submit_api="api/analysis/analysis_submit"
language_api="api/administrator/languages_viewset"
otp_verify_api="api/analysis/otp_verify"
category_api="api/analysis/category"
payments_api="api/analysis/payments"
create_user = "api/analysis/create_user"
get_location_api = "api/administrator/get-location"
#function to fetch location

@app.route('/get-user-country', methods=['GET'])
def get_user_country():
    # Get the user's IP address
    if request.headers.getlist("X-Forwarded-For"):
        ip_address = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip_address = request.remote_addr  # Fall back to remote_addr
    print(ip_address)
    try:
        # Fetch data from ip-api.com using the user's IP address
        response = requests.get(f"http://ip-api.com/json/{ip_address}")
        data = response.json()
        country_code = data.get('countryCode', 'Unknown')
        country = data.get('country', 'Unknown')
        return jsonify({
            'countryCode': country_code,
            'country': country
        })
    except Exception as e:
        print(f"Error fetching user location: {e}")
        return jsonify({
            'error': 'Unable to fetch location'
        }), 500

@app.route("/<int:category_id>")
def category(category_id):
    try:
        print("category",category_id)
        session['category_id']=category_id

        # deleting any email or mobile number in session
        session.pop('email',None)
        session.pop('mobile_num',None)
        
        # ip_address = request.remote_addr
        # # print('hello     ',ip_address)
        # country = get_country(ip_address)
        # print("country",country)
        # session['country']=country
        # print("welcome")
        # if country == 'IN':
        #     return redirect(url_for('phone_signup'))
        # else:
        return redirect(url_for('email_signup_US'))
    except Exception as e:
        print(e)
        return render_template("error.html")

@app.route("/get_started")
def get_started():
    return render_template('new_welcome_page.html')

@app.route("/", methods = ['GET','POST'])
def home():
    if request.method == 'POST':
        print(request.form)
        session['country'] = request.form['country']
        return redirect(url_for('email_signup_US'))
    return render_template('select_residence.html')

@app.route("/gender" , methods=['POST','GET'])
def customer_gender():
    try:
        if session['category_id'] :
            del session['category_id']
    except:
        pass

    print("customer gender page")
    if request.method == 'POST':
   
        gender = request.form.get('gender')
        print(gender)
        
        if gender:
            session['gender'] = gender
        if 'category_id' in session:
            category_id=session['category_id']
            if category_id == 0:
                return redirect(url_for('select_category'))
            else:
                return redirect(url_for('analysis',category_id=category_id,gender=gender))
        return redirect(url_for('select_category',gender=gender))
  
    return render_template('gender_split_screen.html')


@app.route("/select_category", methods=['GET','POST'])
def select_category():
    print("select category page")
    if 'gender' in session:
        gender=session['gender']
        print(gender)
    headers = {
            "Content-Type":"application/json"
        }
    category_req=requests.post(base_url+category_api,headers=headers)
    print("category api:",category_req.status_code)
    category_resp=json.loads(category_req.text)
    print(category_resp)
    categories=category_resp['data']
    if request.method == 'POST':
        print(gender)
        category = request.form['category']
        print("category",category)
        session['category_id']=category
        return redirect(url_for('analysis',category_id=category,gender=gender))
    return render_template('select_category.html',categories=categories)

@app.route("/analysis/<string:gender>", methods=['GET','POST'])
def analysis(gender):
    print(request)
    try:
        headers = {
            "Content-Type":"application/json"
        }
        questionnaire_api="api/analysis/questionnaire?category_id="
        #converting category_id to string to pass it through questionnaire api
        # category_id_str=(f"{category_id}")
        # print(base_url+questionnaire_api+category_id_str+'&customer_gender='+gender)
        # print(base_url+questionnaire_api+'&customer_gender='+gender)
        questionnaire_response=requests.get(base_url+questionnaire_api+'&customer_gender='+gender)
        # print(questionnaire_response.status_code)
        questionnaire_data=json.loads(questionnaire_response.text)
        questionnaire_list=questionnaire_data['data']
        # print(questionnaire_list)
        #category id is stored to session
        # category_id=category_id
        # session['category_id']=category_id
        #length of questionnaire list is taken to be used in template
        #for data_page
        question_list_length=len(questionnaire_list)
        # print("question length:",question_list_length)
        # language api callaa
        language_api_request=requests.get(base_url+language_api,headers=headers)
        # print("language api:",language_api_request.status_code)
        
        language_api_response=json.loads(language_api_request.text)
        languages=language_api_response['data']
        print('questionnaire_list:  ',questionnaire_list)
        print('question_list_length:  ',question_list_length)
        print('languages:  ',languages)
        return render_template('analysis.html',questionnaire_list=questionnaire_list,question_list_length=question_list_length,
        languages=languages)
    except Exception as e:
        print(e)
    return render_template('analysis.html')

# @app.route("/<int:category_id>")
# def welcome(category_id):
#     # ******* removing any email and mobile num data before starting analysis survey ********
#     session.pop('email',None)
#     session.pop('mobile_num',None)
#     # session.pop('country',None)
    
#     session['category_id']=category_id
#     # ****** location fetching *********
#     ip_address = request.remote_addr
#     country = get_country(ip_address)
#     print("country",country)
#     session['country']=country
#     print("welcome")
#     # if country in ('IN'):
#     #     print("phone login")
#     # else:
#     #     return redirect(url_for('analysis',category_id=category_id))
#     return render_template('new_welcome_page.html',category_id=category_id)


#this view is to store analysis data coming from ajax
@app.route("/data", methods=['POST','GET'])
def data_analysis():
    print("analysis data")
    questions_data = {}
    if request.method == "POST":
        questions_data = request.get_json()
        print(session)
        session['questions_data']=questions_data 
        print(session)
        print('questions_data',questions_data)   
        return questions_data    
    return render_template("blankpage.html")

@app.route("/disclaimer",methods=['POST','GET'])
def disclaimer():
    print("disclaimer")
    return render_template('disclaimer_page.html')

@app.route("/email_signup", methods=['POST','GET'])
def email_signup():
    print("email signup last page")

    print(session)
    if 'country' in session:
        country = session['country']
        print(country)
    if country == 'IN' or country == 'India':
        print('Inside IN')
        headers={
            'content-type': 'application/json'
        }
        if request.method == "POST":
            print("post")
            email = request.form['email_address']
            print("email:",email)
            session['email']=email
            return redirect(url_for('new_appointment_preview',invoice_id=0))

    else:
        print('Outside IN')
        return redirect(url_for('new_appointment_preview',invoice_id=0))

    return render_template('email_signup.html')

@app.route("/verify",methods=['POST','GET'])
def email_verification_message():
    print("email otp india")
    if 'email' in session:
        email=session['email']
    if request.method=='POST':
        otp=request.form['otp']
        payload={
                "email":email,
                "otp":otp
            }
        headers={
            'content-type': 'application/json'
        }
        json_data=json.dumps(payload)
        otp_generate=requests.post(base_url+otp_verify_api, data=json_data, headers=headers)
        print(otp_generate.status_code)
        otp=json.loads(otp.text)
        print(otp)
        if otp_generate.status_code == 200:
            # return redirect('http://localhost:8002/')
            return redirect('https://customers.inticure.online/')
        else:
            flash("Invalid otp, email not verified","error")
            return redirect(url_for('email_verification_message'))
    return render_template('verification_message.html')

last_execution_times = {}

# Define a rate limit period (10 seconds in this case)
RATE_LIMIT_PERIOD = 10

def is_rate_limited(user_id):
    """Check if the user is rate-limited (executed within the last 10 seconds)."""
    current_time = time.time()
    
    if user_id in last_execution_times:
        last_time = last_execution_times[user_id]
        if current_time - last_time < RATE_LIMIT_PERIOD:
            return True
    
    # Update the last execution time
    last_execution_times[user_id] = current_time
    return False

@app.route("/thank_you_page", methods=['POST','GET'])
def thank_you_page():
    doctor_not_available = 1
    print('line 309  ' , session)

    if is_rate_limited(session['temp_data_id']):
        return redirect(url_for('finished'))

    questions_data=''
    try:
        questions_data=session['questions_data']

        print("thankyou page")
        headers={
            'content-type': 'application/json'
        }
     
        try:
            print('entereed into thankeyooieau')
            appointment_date_str = questions_data['appointment_date']
            appointment_time_str = questions_data['appointment_time']
            print(appointment_date_str)
            print(appointment_time_str)

            # Convert the appointment_date_str to a date object
            appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()
            print(appointment_date)
            # Convert the appointment_time_str to a time object
            appointment_time = datetime.strptime(appointment_time_str, '%I:%M%p').time()
            print(appointment_time)
            # Combine the date and time to create a datetime object for the appointment
            appointment_datetime = datetime.combine(appointment_date, appointment_time)
            print(appointment_datetime)
            # Get the current time
            current_time = datetime.now()

            # Add 3 hours to the current time
            current_time_plus_3_hours = current_time + timedelta(hours=3)
            print(current_time_plus_3_hours)
            # Compare the appointment datetime with the current time plus 3 hours
            if appointment_datetime > current_time_plus_3_hours:
                print("The appointment is more than 3 hours from the current time.")
            else:
                print("The appointment is not more than 3 hours from the current time.")
                err = "Time is Not valid! You can choose another time by login"
                session['err'] = err

                return redirect(url_for('show_error'))
        except Exception as e:
            print(e)

        print('questions_data is going ot print line 356 - ',questions_data)
        if 'email' not in session and 'email_contact' in session and 'email_contact' != "" :
            email = session['email_contact']
        elif 'email' in session and session['email'] != "":
            email = session['email']
        else:
            email = None

        if 'email_contact' in questions_data and questions_data['email_contact'] != "":
            email=questions_data['email_contact']
            print(email,'line 359')
        try:
            if 'appointment_date' in questions_data:
                appointment_date=questions_data['appointment_date']
                print(appointment_date)
            if 'appointment_time' in questions_data:
                appointment_time=questions_data['appointment_time']
                print("appointment time", appointment_time)
            if 'questions' in questions_data:
                questions=questions_data['questions']
                print('line 369 ',questions)
        
            language_pref=questions_data['language_pref']
            print(language_pref)

            gender_pref=questions_data['gender_pref']
            print(gender_pref)
            doctor_flag=questions_data['doctor_flag']
            first_name=questions_data['first_name']
            last_name=questions_data['last_name']
            message=questions_data['message']
            dob=questions_data['dob']
        except Exception as e:
            print(e)
        print("questions data - 380",questions_data)
        if questions_data['email_contact'] == "":
            print('email taken from last page - 379')
            email = session['email']
            print(email)
        print('sldkjflasdkmclasdvlsdkdjglasmidujoapsdvmaoishjgaoksdfa   ',questions_data)
        category_id = ''
        gender = ''
        other_gender = ''
        if 'category_id' in session:
            category_id=session['category_id']
            print(category_id)
        if 'mobile_num' in session:
            mobile_num=session['mobile_num']
            print("phone",mobile_num)
        elif 'whatsapp_contact' in session:
            mobile_num=session['whatsapp_contact']
            print("phone not available",mobile_num)
        else:
            mobile_num = ""
        if 'gender' in session:
            gender=session['gender']
        if 'other_gender' in session:
            other_gender=session['other_gender']
        if 'dob' in questions_data:
            dob=questions_data['dob']
        country = ''
        if 'country' in session:
            country=session['country']

        if 'first_name' in questions_data:
            first_name=questions_data['first_name']
        if 'last_name' in questions_data:
            last_name=questions_data['last_name']
        if 'message' in questions_data:
            message=questions_data['message']
        print("questions data line 419",questions_data)   
        print(questions_data['questions'])    
        user_id = "" 
        if 'user_id' in session:
            user_id = session['user_id']
        data={
            "new_user":1,
            "user_id":user_id,
            "category_id": category_id,
            "questions":questions,
            "appointment_date":appointment_date,
            "appointment_time":appointment_time,
            "email":email,
            "language_pref":language_pref,
            "gender_pref":gender_pref,
            "doctor_flag":doctor_flag,
            "mobile_num":mobile_num,
            "customer_dob":dob,
            "customer_gender":gender,
            "first_name":first_name,
            "last_name":last_name,
            "customer_message":message
        }
        print('line 439 ', data)
        if country != 'unknown':
            data['customer_location'] = country
        try:
            if other_gender:
                data['other_gender'] = other_gender
            else:
                other_gender = ''
        except Exception as e:
            print(e)


        api_data=json.dumps(data)
        print("api_data in last page:",api_data)
        try:
            analysis_submit=requests.post(base_url+analysis_submit_api,data=api_data,headers=headers)
            print('submission check')
            print(analysis_submit.status_code)
            print(analysis_submit)
            print('submission checked')
            analysis_submit_response=json.loads(analysis_submit.text)
            'ssss'
            print(analysis_submit_response,'458')
        except Exception as e:
            print(e)
            analysis_submit_response['response_code'] = 400
            analysis_submit_response['message'] = 'Invalid details'

        if analysis_submit_response['response_code']==200:
            session.clear()
            print("analysis submitted account created")
            return redirect(url_for('finished'))
        elif analysis_submit_response['response_code']==409:
            print("User/Email exists")
            session.clear()
            return redirect(url_for('user_exists'))
        else:
            print('okkk')
            err = analysis_submit_response['message']
            session['err'] = err
            flash(err, 'error') 
            return redirect(url_for('analysis',gender = session['gender']))
    
    except Exception as e:
        print(e)
        return render_template("error.html")

@app.route("/finished")
def finished():
    return render_template('thank_you_page.html')

@app.route("/new_appointment_preview/<int:invoice_id>",methods=['GET','POST'])
def new_appointment_preview(invoice_id):
    print("new appointment preview")
    print(invoice_id)
    print(session)
    headers={
        "Content-Type":"application/json"
        }
    escalated_one_res = None
    if 'country' in session and session['country'] != "":
        data = {
            'location' : session['country']
        }
        api_data = json.dumps(data)
        location_req = requests.post(base_url+get_location_api,headers=headers,data=api_data)
        location_resp = json.loads(location_req.text)
        print(location_resp)
        session['loc_id'] = location_resp['location_id']
    #category list api call
    questions_data=session['questions_data']
    category_req=requests.post(base_url+category_api,headers=headers)
    email = ''
    if 'email_contact' not in questions_data or questions_data['email_contact'] == "":
        print('email taken from last page - 379')
        if 'email' in session:
            email = session['email']
    else:
        email = questions_data['email_contact']
    if email != "":
        user_api_data = {
            'first_name': questions_data['first_name'],
            'last_name':questions_data['last_name'],
            'email': email
        }
    else:
        if 'whatsapp_contact' in questions_data and questions_data['whatsapp_contact'] != "":
            user_api_data = {
                'first_name': questions_data['first_name'],
                'last_name':questions_data['last_name'],
                'email': session['whatsapp_contact']
            }
            email = ''
    for i in session:
        print(i)
    if 'whatsapp_contact' in questions_data and questions_data['whatsapp_contact'] != "":
        user_api_data = {
        'first_name': questions_data['first_name'],
        'last_name':questions_data['last_name'],
        'email': email,
        'whatsapp_contact':questions_data['whatsapp_contact']
        }
    api_data=json.dumps(user_api_data)
    print(api_data)
    user_req = requests.post(base_url+create_user,data=api_data,headers=headers)
    user_req_res = json.loads(user_req.text)
    print(user_req_res)
    if 'user_id' in user_req_res:
        session['user_id'] = user_req_res['user_id']
    print("category api:",category_req.status_code)
    category_resp=json.loads(category_req.text)
    print(category_resp)
    categories=category_resp['data']
    print('507', categories)
    if 'category_title' in session:
        category_title = session['category_title']
        print(category_title)
    else:
        category_title = ''
        for i in categories:
            print(i)
            if int(i['id']) == int(session['category_id']):
                category_title = i['title']
                break
        print(category_title)
        session['category_title'] = category_title

    new_appointment_specialization = 'no specialization'
    if 'new_data' in session:
        new_data=session['new_data']
        print("new appointment")
        print("preview",new_data)
        user_id=user_req_res['user_id']
    else:
        new_data = {
                'appointment_date': session['questions_data']['appointment_date'],
                'appointment_status': 2,
                'appointment_time': session['questions_data']['appointment_date'],
                'category_id': session['category_id'],
                'doctor_flag':1,
                'followup_id':'',
                'gender_pref': session['questions_data']['gender_pref'],
                'language_pref': session['questions_data']['language_pref'],
                'new_user':0,
                'remarks':'',
                'specialization': 'no specialization',
                'type_booking':'regular',
                'user_id': user_req_res['user_id']
            }
    payment = ''
    
    if 'loc_id' in session:
        location_id = session['loc_id']
        
        if request.method == 'POST':
            print("post")
            coupon = request.form['coupon']
        else:
            print("no coupon")
            coupon = ""
        
        payload={
                "user_id":user_req_res['user_id'],
                "appointment_id": '',
                "specialization":new_appointment_specialization,
                "coupon_code":"",
                "location_id":location_id,
                "session_type":'single'
            }
        api_data=json.dumps(payload)
        print(api_data)
        payments_request=requests.post(base_url+payments_api,data=api_data,headers=headers)
        payment_response=json.loads(payments_request.text)   
        print("payments api",payments_request.status_code)
        print(payment_response)
        payment=payment_response['payment']
        temp_data_id = payment_response['temp_data_id']
        print('temp_data_id: ',temp_data_id)
        session['temp_data_id']= temp_data_id
        session['appointment_flag'] = 'first_appointment'
        print(session)
        new_data['session_type'] = 'single'
        new_data['duration'] = payment_response['duration']
        if 'email' in session:
            new_data['email'] = session['email']
        if 'first_name' and 'last_name' in session['questions_data']:
            new_data['name'] = session['questions_data']['first_name'] +' '+session['questions_data']['last_name']

        print(session)

    return render_template('new_appointment_preview.html',new_data=new_data,categories=categories,payment=payment,appointment_flag='first_appointment')

@app.route("/phone_verify" , methods=['POST','GET'])
def phone_verification_message():
    print("phone otp-line-516")
    headers={
        'content-type': 'application/json'
        }
    if request.method == 'POST':
        print("post")
        if 'mobile_num' in session:
            mobile_num=session['mobile_num']
        otp=request.form['otp']
        if request.form['form_type'] == 'next':
            print('next')
            otp=request.form['otp']
            
            payload={
                "mobile_num":mobile_num,
                "otp":otp
            }
            json_data=json.dumps(payload)
            otp_generate=requests.post(base_url+otp_verify_api, data=json_data, headers=headers)
            print(otp_generate.status_code)
            otp=json.loads(otp_generate.text)
            print(otp)
            if otp['response_code']==400:
                flash("Incorrect otp","error")
                return redirect(url_for('phone_verification_message'))
             
            return redirect(url_for('get_started'))
            
        if request.form['form_type'] == 'resend':
            # otp=request.form['otp']
            
            payload={
                "mobile_num":mobile_num,
                # "otp":""
            }
            json_data=json.dumps(payload)
            otp_generate=requests.post(base_url+otp_verify_api, data=json_data, headers=headers)
            print(otp_generate.status_code)
            otp=json.loads(otp_generate.text)
            print(otp)
            return render_template('phone_otp_verify.html')
        #     return redirect(url_for('phone_verification_message'))
        # return redirect(url_for('analysis',category_id=category_id))
        # return redirect(url_for('otp_success'))
    return render_template('phone_otp_verify.html')
    return render_template('phone_verification.html')

# beginning of analysis for outside india
@app.route("/email_signup_", methods=['POST','GET'])
def email_signup_US():
    # ******* removing any email and mobile num data before starting analysis survey ********
    print(session)
    session.pop('email',None)
    session.pop('mobile_num',None)
    print(session)
    headers={
        'content-type': 'application/json'
        }
    if request.method == 'POST':
        print('post')
        print(request.data)
        email=request.form.get('contact') 
        country_for_contact = request.form.get('country')
        country = session['country']
        code = request.form.get('code')
        print(email, country_for_contact, code)
        if '@' in email:

            session['email']= email
            session['country_for_contact'] = country_for_contact
            # payload={
            #     "email":email,
            #     "country":country
            # }
            # json_data=json.dumps(payload)
            
            # print(json_data)
            # otp_generate=requests.post(base_url+otp_verify_api, data=json_data, headers=headers)
            # print(otp_generate.status_code)
            # otp_req=json.loads(otp_generate.text)
            # print(otp_req)
            # if otp_req['response_code'] == 400:
            #     flash("Something went wrong..","error")
            #     return redirect(url_for('email_signup_US'))
            #     # return redirect(url_for('user_exists'))
            # elif otp_req['response_code']==409:
            #     return redirect('https://customers.inticure.online/')
            return redirect(url_for('get_started'))
        else:
            if len(email) != 10:
                flash("number must be length of 10 (No need to include any country code)","info")
                return redirect(url_for('email_signup_US'))
            session['mobile_num']=code +' ' +email
            session['country_for_contact']=country_for_contact
            payload={
                "mobile_num":email,
                "country":country,
                "country_for_contact":country_for_contact,
                "code":code
            }
            # json_data=json.dumps(payload)
            # otp_generate=requests.post(base_url+otp_verify_api, data=json_data, headers=headers)
            # print(otp_generate.status_code)
            # otp_req=json.loads(otp_generate.text)
            # print(otp_req)
            # if otp_req['response_code']==400:
            #     flash("Something went wrong..","error")
            #     return redirect(url_for('phone_signup'))
            # elif otp_req['response_code']==409:
            #     return redirect('https://customers.inticure.online/')
            return redirect(url_for('get_started'))
            # return redirect(url_for('phone_verification_message'))
    return render_template('email_verify.html', selected_country = session['country'])

@app.route("/email_signup_otp_" , methods=['POST','GET'])
def email_signup_otp_():
    print("email otp outside IN")
    headers={
        'content-type': 'application/json'
        }
    if request.method == 'POST':
        print("post")
        if 'email' in session:
            email=session['email']
            print(email)
        # otp=request.form['otp']
        if request.form['form_type'] == 'next':
            print('next')
            otp=request.form['otp']
            
            payload={
                "email":email,
                "otp":otp
            }
            json_data=json.dumps(payload)
            otp_generate=requests.post(base_url+otp_verify_api, data=json_data, headers=headers)
            print(otp_generate.status_code)
            otp=json.loads(otp_generate.text)
            print(otp)
            if otp['response_code']==400:
                flash("Incorrect otp","error")
                return render_template('email_otp_verify.html')
                # return redirect(url_for('category',category_id=0))
            return redirect(url_for('get_started'))    
        
        if request.form['form_type'] == 'resend':
            # otp=request.form['otp']
            
            payload={
                "email":email,
                
            }
            json_data=json.dumps(payload)
            otp_generate=requests.post(base_url+otp_verify_api, data=json_data, headers=headers)
            print(otp_generate.status_code)
            otp_resp=json.loads(otp_generate.text)
            print(otp_resp)
            return redirect(url_for('email_signup_otp_'))

    # return render_template('email_signup_otp.html')
    return render_template('email_otp_verify.html')


# @app.route("/gender_dob" , methods=['POST','GET'])
# def gender_and_dob():
#     print("gender & dob page")
#     if request.method == 'POST':
#         gender=request.form['gender']
#         other_gender=request.form['other_gender']
#         dob=request.form['dob']
#         session['gender']=gender
#         session['other_gender']=other_gender
#         session['dob']=dob        
#         if 'category_id' in session:
#             category_id=session['category_id']
#         return redirect(url_for('analysis',category_id=category_id,gender=gender))
#     return render_template('gender_and_dob.html')

@app.route("/name" , methods=['POST','GET'])
def name():
    print("name page")
    if request.method == 'POST':
        first_name=request.form['first_name']
        last_name=request.form['last_name']
        message=request.form['message']
        session['first_name']=first_name
        session['last_name']=last_name
        session['message']=message        
        
        return redirect(url_for('disclaimer'))
    return render_template('name.html')

@app.route("/error_user_exists")
def user_exists():
    return render_template('user_exists.html')

@app.route("/error")
def error():
    return render_template('error.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/logout", methods=['GET','POST'])
def logout():
    return redirect(url_for('login'))

@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')


@app.route('/invalid')
def show_error():
    err = 'ERROR'
    if session['err'] is not None:
        err=session['err']
    return render_template('show_error.html',err=err)


if __name__ == '__main__':
    app.run(debug = True,port=8006)