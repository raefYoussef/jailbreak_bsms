from flask import Flask, render_template, request, url_for, flash, redirect, jsonify
from passlib.hash import sha256_crypt
from dbconnect import connection
from MySQLdb import escape_string as thwart
import gc, datetime


app = Flask(__name__)


@app.route('/signUp/', methods=["GET","POST"])
def signUp():
        return render_template('signUp.html')


@app.route('/signUpUser/', methods=["GET","POST"])
def signUpUser():
        user =  request.form['username']
        password = request.form['password']

        return jsonify({'status':'OK','user':user,'pass':password})


@app.route('/', methods=["GET","POST"])
def signin():
	error = ''
	try:
		c, conn = connection()
		
		if request.method == "POST":
			attempted_email = request.form['email']
			attempted_password = request.form['password']

			data = c.execute("SELECT * FROM users WHERE email = ('"+ attempted_email + "')")

			if data and sha256_crypt.verify(attempted_password, c.fetchone()["password"]):
				#flash(attempted_username)
				#flash(attempted_password)
				#if attempted_username == "admin" and attempted_password == "password":
				return redirect(url_for('dashboard'))
			else:
				error = "Invalid credentials. Try Again."
        
		gc.collect()

		return render_template("signin.html", error = error)

	except Exception as e:
		flash(e)
		return render_template("signin.html", error = error)


@app.route('/compare_epc/', methods=["POST"])
def compare_epc():
	try:
		c, conn = connection()
		data_count = c.execute("SELECT * FROM inventory WHERE internal_id = ('"+ request.form["epc"] + "')")
		data = c.fetchall()
		return jsonify({"epc": data})
	except Exception as e:
		return jsonify({"error": e})


@app.route('/add_epc/', methods=["POST"])
def add_epc():
	try:
		c, conn = connection()
		c.execute("INSERT INTO inventory (keg_type, internal_id) VALUES (%s, %s)", (thwart(keg_type), thwart(internal_id)))
		conn.commit()
		c.close()
		conn.close()
	except Exception as e:
		return jsonify({"error": e})


@app.route('/signin_temp/', methods=["GET","POST"])
def signin_temp():
	error = ''
	try:
		c, conn = connection()
		if request.method == "POST":
			attempted_username = request.form['username']
			attempted_password = request.form['password']

			data = c.execute("SELECT * FROM users WHERE username = ('"+ attempted_username + "')")

			#data = c.fetchone()[2]


			if data and sha256_crypt.verify(request.form['password'], c.fetchone()["password"]):
				#flash(attempted_username)
				#flash(attempted_password)
				#if attempted_username == "admin" and attempted_password == "password":
				return redirect(url_for('dashboard'))
			else:
				error = "Invalid credentials. Try Again."
				gc.collect()

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
	return render_template("dashboard.html", account_name = "Kasey Turner")


@app.route('/dashboard_ajax_brands/', methods=["POST"])
def dashboard_ajax_brand():
		try:
			# establish a connection to database
			c, conn = connection()
			
			# Beer Brands 
			brand_count = c.execute("""	SELECT beer_brands.name FROM beer_brands 
										INNER JOIN inventory ON beer_brands.id = inventory.beer_brand 
										WHERE ((inventory.status <=> 'FULL_INV' OR inventory.status <=> 'FULL_TAP') AND (inventory.beer_brand IS NOT NULL)) 
										ORDER BY inventory.beer_brand asc """) 
			brands = c.fetchall()
			# populate set with beer brands frequencies 
			freq_set = {i["name"]: brands.count(i) for i in brands}
			# format set into array required by morrisjs donut chart
			freq_list = [{"label": freq_set.keys()[i], "value": freq_set.values()[i]} for i in range(len(freq_set))]

			return jsonify({"brands_chart":freq_list})

		except Exception as e:
			# failed connection
			return jsonify(e)


@app.route('/dashboard_ajax_customers/', methods=["POST"])
def dashboard_ajax_customers():
	try:
		# establish a connection to database
		c, conn = connection()
		
		# Customers
		cstr_count = c.execute("SELECT customer FROM inventory WHERE (customer IS NOT NULL) ORDER BY beer_brand ASC")
		customers = c.fetchall()
		# populate set with number of kegs for each customer
		cust_set = {i["customer"]: customers.count(i) for i in customers}
		cust_list = []

		for customer_name in cust_set.keys():
			# obtain last activity for each customer
			actv_count = c.execute("SELECT GREATEST(IFNULL(MAX(time_in), 0), IFNULL(MAX(time_shipped), 0)) AS last_activity FROM inventory WHERE customer = '" + customer_name + "'")
			activity = c.fetchall()

			freq = cust_set[customer_name]

			# compile, and format, data
			if actv_count != 0 :
				cust_list.append([customer_name, freq, activity[0]["last_activity"]])
			else :
				cust_list.append([customer_name, freq, None])

		return jsonify(cust_list)

	except Exception as e:
		# failed connection
		return jsonify(e)


@app.route('/dashboard_ajax_invStatus/', methods=["POST"])
def dashboard_ajax_kegStatus():
	try:
		# establish a connection to database
		c, conn = connection()
		
		# inventory status for past week
		status_list = []

		for i in xrange(7):
			# obtain kegs status and freq 
			sts_count = c.execute("""	SELECT activity_log.status AS status, COUNT(activity_log.status) As freq FROM activity_log 
										INNER JOIN (SELECT keg_id, MAX(time) AS ts FROM activity_log WHERE time <= SUBDATE(NOW(),""" + str(i) + """) GROUP BY keg_id) maxt 
										ON (activity_log.keg_id = maxt.keg_id AND activity_log.time = maxt.ts) GROUP BY activity_log.status """)
			status = c.fetchall()

			# accounts for non-existant statues
			date = str(datetime.datetime.now().date() - datetime.timedelta(i))
			status_dict = {"date": date, "DIRTY":0, "CLEAN":0, "FULL_INV":0, "FULL_TAP":0, "FULL_OUT":0}

			for i in status:
				status_dict[i["status"]]=i["freq"]

			status_list.append(status_dict)

		return jsonify(status_list)

	except Exception as e:
		# failed connection
		return jsonify(e)	


@app.route('/settings/')
def settings():
	return render_template("settings.html")


@app.route('/view_inventory/', methods=["GET","POST"])
def view_inventory():
	c, conn = connection()
	inventory_items = c.execute("SELECT * FROM inventory")
	inventory_items = c.fetchall()
	# x = [{key_id: 1}, {keg_id: 2}, {key_id: 3}]
	# x[0]["keg_id"]
	#print("hello")
	#print(inventory_items)
	return render_template("view_inventory.html", inventory=inventory_items,  account_name = "Kasey Turner")


@app.route('/edit_inventory/', methods=["GET","POST"])
def edit_inventory():
	return render_template("edit_inventory.html", methods=['POST'])
    

@app.route('/logistics/')
def logistics():
	return render_template("logistics.html", account_name = "Kasey Turner")


if __name__ == "__main__":
	# app.secret_key = 'some secret key'
	app.run(debug=True)
	#app.run()
