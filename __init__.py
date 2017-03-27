from flask import Flask, render_template, request, url_for, flash, request, redirect

app = Flask(__name__)

@app.route('/')
def signin():
	return render_template("signin.html", methods=['POST'])

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

@app.route('/home/')
def home():
	return render_template("home.html")

@app.route('/dashboard/')
def dashboard():
	return render_template("dashboard.html", account_name = "John Smith")

@app.route('/settings/')
def settings():
	return render_template("settings.html")

@app.route('/view_inventory/')
def view_inventory():
	return render_template("view_inventory.html", account_name = "John Smith")

@app.route('/edit_inventory/')
def edit_inventory():
	return render_template("edit_inventory.html", account_name = "John Smith")

@app.route('/logistics/')
def logistics():
	return render_template("logistics.html", account_name = "John Smith")

if __name__ == "__main__":
	app.secret_key = 'some secret key'
	app.run(debug=True)
	#app.run()