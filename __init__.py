from flask import Flask, render_template, request, url_for, flash, request, redirect

app = Flask(__name__)

@app.route('/')
def signin():
	return render_template("signin.html", methods=['POST'])

@app.route('/home/')
def home():
	return render_template("home.html")

@app.route('/signin_temp/', methods=["GET","POST"])
def signin_temp():
	error = ''
	try:
	    if request.method == "POST":
	        attempted_username = request.form['username']
		attempted_password = request.form['password']
		flash(attempted_username)
		flash(attempted_password)
		
		if attempted_username == "admin" and attempted_password == "password":
		    return redirect(url_for('home'))
		else:
		    error = "Invalid credentials. Try Again."

	    return render_template("signin_temp.html", error = error)		
	    
	except Exception as e:
	    flash(e)
	    return render_template("signin_temp.html", error = error)


#@app.errorhandler(405)
#def method_not_found(e):
#	return render_template("405.html")

if __name__ == "__main__":
	app.secret_key = 'some secret key'
	app.run(debug=True)
	#app.run()