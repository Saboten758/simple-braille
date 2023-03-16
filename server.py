from flask import Flask,render_template,request,flash, redirect, url_for
# from flask import session
# from firebase_admin import auth,credentials
import os
# import firebase
import  alphaToBraille
import textwrap
import fitz
from flask import send_file
import pyttsx3
import win32com.client
import pythoncom
# from google.oauth2.credentials import Credentials
# from google.oauth2 import id_token
# from google.auth.transport import requests as google_requests
# from google.auth.exceptions import GoogleAuthError

from fpdf import FPDF

# import firebase_admin
# from firebase_admin import credentials

# cred = credentials.Certificate('braille-12edc-firebase-adminsdk-znugp-d057bdf37c (1).json')
# firebase_admin.initialize_app(cred)

if os.path.exists('upload.pdf'):
    alphaToBraille.n="NO FILE"
    os.remove('upload.pdf')  
         
def is_pdf_empty(filepath):
    try:
        with fitz.open(filepath) as pdf:
            if pdf.page_count == 0:
                return True
            else:
                page = pdf.load_page(0)
                text = page.get_text("text")
                if len(text.strip()) == 0:
                    return True
                else:
                    return False
    except Exception as e:
        return True
            
def reader(filename):
    doc = fitz.open(filename)
    text = ""
    for page in doc:
        text+=page.get_text()
    return text
    
def text_to_pdf(text, filename):
    a4_width_mm = 210
    pt_to_mm = 0.35
    fontsize_pt = 10
    fontsize_mm = fontsize_pt * pt_to_mm
    margin_bottom_mm = 10
    character_width_mm = 7 * pt_to_mm
    width_text = a4_width_mm / character_width_mm

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(True, margin=margin_bottom_mm)
    pdf.add_font('DejaVu','',r'DejaVuSansCondensed.ttf',uni=True)
    pdf.add_page()
    pdf.set_font('DejaVu','', size=fontsize_pt)
    splitted=text.split('\n')
    for line in splitted:
        lines = textwrap.wrap(line, width_text)

        if len(lines) == 0:
            pdf.ln()

        for wrap in lines:
            pdf.cell(0, fontsize_mm, wrap, ln=1)
    pdf.output(filename, 'F') 

    
def text_to_speech(text, filename):
    win32com.client.Dispatch("SAPI.SpVoice",pythoncom.CoInitialize())
    engine = pyttsx3.init()
    engine.setProperty('rate', 190) 
    engine.setProperty('volume', 1) 
    engine.save_to_file(text, filename)
    engine.runAndWait()
    
def pdf_out(filename): 
      
    text=reader(filename)
    
    text=(alphaToBraille.translate(text))
    
    text_to_pdf(text, "BrailleHeads-convt.pdf")
    
    
    
app=Flask(__name__)
app.secret_key = 'my_secret_key'


@app.route('/')
def home():
    return render_template('front.html',name=alphaToBraille.n)

# @app.route('/google/callback')
# def google_callback():
#     # Get the authorization code from the URL parameter
#     code = request.args.get('code')
    
#     # Exchange the authorization code for an access token
#     try:
#         credentials = Credentials.from_authorized_user_info(
#             info=id_token.verify_oauth2_token(
#                 code,
#                 google_requests.Request(),
#                 firebaseConfig['web']['client_id']
#             ),
#             scopes=['openid', 'email', 'profile']
#         )
#     except GoogleAuthError as e:
#         return 'Failed to exchange authorization code for access token: {}'.format(e), 400

#     access_token = credentials.token

#     # Use the access token to authenticate the user
#     id_info = id_token.verify_oauth2_token(
#         access_token,
#         google_requests.Request(),
#         firebaseConfig['web']['client_id']
#     )
#     uid = id_info['sub']

#     # Save the user ID in the session
#     session['uid'] = uid

#     # Redirect to the dashboard page
#     return redirect('/dashboard')

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    pdf_file = request.files['pdf_file']
    alphaToBraille.n=pdf_file.filename
    pdf_file.save("upload.pdf")
    if is_pdf_empty('upload.pdf'):
        flash('NO FILE WAS UPLOADED!', 'success')
    else:
        flash('Uploaded Successfully!', 'success')
    return redirect(url_for('home'))
    
# @app.route('/google/login')
# def google_login():
#     # Build the authorization URL
#     redirect_uri = request.base_url.replace('http://', 'https://')
#     auth_url = auth.build_auth_url({'provider': 'google'}, redirect_uri)

#     # Redirect the user to the authorization URL
#     return redirect(auth_url)  

# @app.route('/dashboard')
# def dashboard():
#     # Check if the user is authenticated
#     if 'uid' not in session:
#         return redirect('/google/login')

#     # Get the user's data from Firebase
#     user = auth.get_user(session['uid'])

#     # Render the dashboard page with the user's data
#     return render_template('dashboard.html', user=user)


@app.route('/cnvt')
def my_function():
    if os.path.exists('upload.pdf'):
        pdf_out("upload.pdf")
        return send_file("BrailleHeads-convt.pdf", as_attachment=True) 
    else:
        return "<p>Please Upload File and Try Again!<p>"


@app.route('/send_mp3')
def send_mp3():
    
    if os.path.exists('upload.pdf'):
        text=reader("upload.pdf")
        alphaToBraille.n="No FILE"
        text_to_speech(text,'Braille-Heads-convt.mp3')
        file_path = 'Braille-Heads-convt.mp3'
    else:
        text="No file was uploaded!"
        alphaToBraille.n="No FILE"
        text_to_speech(text,'Braille-Heads-convt.mp3')
        file_path = 'Braille-Heads-convt.mp3'
    return send_file(file_path, mimetype='audio/mp3',as_attachment=True) 
  
if __name__=='__main__':
    app.run(debug=True)