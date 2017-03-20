from flask import Flask, render_template, request, url_for, flash

app = Flask(__name__)

@app.route('/')
def signin():
	return render_template("signin.html", methods=['POST'])

@app.route('/home/')
def home():
	return render_template("home.html")

@app.route('/signin_temp/')
def signin_temp():
	return render_template("signin_temp.html", methods=['POST'])

if __name__ == "__main__":
	app.run(debug=True)
	#app.run()