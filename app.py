# static folder is by default public
# templates folder is by default private
# localhost:5000/static will show all the files present in the static folder


# Bottstrap template taken from https://startbootstrap.com/themes/clean-blog/

from flask import Flask 
from flask import render_template
from flask import redirect


app = Flask(__name__)

@app.route('/')
def home():
	return render_template('index.html')


# static kaa jo url hai aapkay server may ussay replace kar dega aapko ye
# {{url_for('static', filename='about-bg.jpg') }}


if __name__ == '__main__':
	app.run(debug=True)