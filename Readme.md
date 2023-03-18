# Simple Braille Application<br/>
This is a simple application, I made for our project on Quality Education for **GDSC**. It is a flask application that relies front.html, which is styled using bootstrap. It will take a pdf as an input, convert it into braille and save it as pdf or download it as mp3 audio.<br>To start the application, simply run:
```python
python server.py
```
This needs a windows machine to work, as the text to speech uses win32com.client for Co-Initializing. To install all the requirements create a virtual-env and run:
```python
pip install -r requirements.txt 
```
