from flask import Flask, render_template, request, url_for, flash, redirect, jsonify, session
from passlib.hash import sha256_crypt
from dbconnect import connection
from MySQLdb import escape_string as thwart
import gc, datetime


app = Flask(__name__)


@app.route('/', methods=["GET","POST"])
def signin():
	error = ''
	try:
		c, conn = connection()
		
		if request.method == "POST":
			attempted_email = request.form['email']
			attempted_password = request.form['password']

			data_count = c.execute("SELECT * FROM users WHERE email = '"+ attempted_email + "'")
			data = c.fetchone()
			user_password = data["password"]

			if data_count and sha256_crypt.verify(attempted_password, user_password):
				session["uid"] = data["uid"]
				session["username"] = data["username"]
				c.execute("UPDATE users SET signin_time = NOW() WHERE email = '"+ attempted_email +"'") 
				conn.commit()
    			#c.close()
    			#conn.close()
				return redirect(url_for('dashboard'))
			else:
				error = "Invalid credentials. Try Again."
				c.execute("UPDATE users SET failed_signin = failed_signin + 1 WHERE email = '"+ attempted_email +"'") 
				conn.commit()
				return render_template("signin.html")
				
		else:
			return render_template("signin.html")

	except Exception as e:
		flash(e)
		return render_template("signin.html", error = error)


@app.route('/signout/', methods=["GET","POST"])
def signout():
	#attempted_email = request.form['email"]
	#c, conn = connection()
	#c.execute("UPDATE users SET signout_time = NOW()) WHERE email = '" +  + "'") 
	#\conn.commit()
	session.pop("uid", None)
	session.pop("username", None)

	return redirect(url_for('signin'))


@app.route('/test/', methods=["GET","POST"])
def test():
	return render_template("test.html")


@app.route('/compare_epc/', methods=["POST"])
def compare_epc():
	try:
		c, conn = connection()
		#"SELECT * FROM inventory WHERE internal_id = ('"+ request.form["epc"] + "')"
		
		data_count = c.execute(""" SELECT inventory.keg_id, inventory.keg_type, inventory.status, beer_brands.name AS beer_brand, 
								inventory.time_in, inventory.time_cleaned, inventory.time_filled, inventory.time_tapped, 
								inventory.time_shipped, inventory.customer, inventory.notes FROM inventory 
								LEFT JOIN beer_brands ON beer_brands.id = inventory.beer_brand 
								WHERE inventory.internal_id = ('"""+ request.form["epc"] + """')
								ORDER BY inventory.keg_id ASC """)
		data = c.fetchall()

		
		return jsonify({"epc": data})
	except Exception as e:
		return jsonify({"error": e})


@app.route('/delete_kegs/', methods=["POST"])
def delete_kegs():
	try:
		c, conn = connection()
		#keg_type = request.form["epc"]
		data = request.form["keg_ids"]

		idarray = data.split(',')

		for element in idarray:
			c.execute("DELETE FROM inventory WHERE keg_id=" + element)
		conn.commit()
		
		return jsonify({"epc": idarray})
	except Exception as e:
		return jsonify({"error": e})


@app.route('/add_epc/', methods=["POST"])
def add_epc():
	try:
		c, conn = connection()
		#keg_type = request.form["epc"]
		data = request.form

		keg_type = data["kegtype_und"]
		internal_id = data["rawId_und"]
		notes = data["notes_und"]

		idarray = internal_id.split(',')

		for element in idarray:
			c.execute("INSERT INTO inventory (keg_type, internal_id, notes) VALUES ('"+thwart(keg_type)+ "', '"+thwart(element)+"', '"+thwart(notes)+"')")
		conn.commit()
		
		return jsonify({"epc": idarray})
	except Exception as e:
		return jsonify({"error": e})


@app.route('/signin_temp/', methods=["GET","POST"])
def signin_temp():
	if "uid" in session:
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

	return redirect(url_for('signin'))


#@app.errorhandler(405)
#def method_not_found(e):
#	return render_template("405.html")


@app.route('/home/')
def home():
	if "uid" in session:
		return render_template("home.html")

	return redirect(url_for('signin'))


@app.route('/dashboard/')
def dashboard():
	if "uid" in session:
		return render_template("dashboard.html", account_name = session["username"])

	return redirect(url_for('signin'))


@app.route('/dashboard_ajax_brands/', methods=["POST"])
def dashboard_ajax_brand():
	try:
		# establish a connection to database
		c, conn = connection()
		
		# Beer Brands 
		brand_count = c.execute("""	SELECT beer_brands.name FROM beer_brands 
									INNER JOIN inventory ON beer_brands.id = inventory.beer_brand 
									WHERE ((inventory.status <=> 'FULL_INV' OR inventory.status <=> 'FULL_TAP') AND (inventory.beer_brand IS NOT NULL)) 
									ORDER BY inventory.beer_brand ASC """) 
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
										INNER JOIN (SELECT keg_id, MAX(time) AS ts FROM activity_log WHERE time <= SUBDATE(NOW(), %s) GROUP BY keg_id) maxt 
										ON (activity_log.keg_id = maxt.keg_id AND activity_log.time = maxt.ts) GROUP BY activity_log.status """ % str(i))
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


@app.route('/dashboard_ajax_notifications/', methods=["POST"])
def dashboard_ajax_notifications():
	try:
		# establish a connection to database
		c, conn = connection()
		
		# Shipped Kegs
		shipped_count = c.execute("""	SELECT activity_log.keg_id, activity_log.time, beer_brands.name AS beer_brand, activity_log.customer, users.username AS user FROM activity_log 
										INNER JOIN beer_brands ON beer_brands.id = activity_log.beer_brand 
										LEFT JOIN users ON activity_log.user=users.Uid 
										WHERE activity_log.status="FULL_OUT" AND activity_log.time >= SUBDATE(NOW(),7) 
										ORDER BY activity_log.time DESC """) 
		shipped = c.fetchall()

		shipped_list = [[i["keg_id"], str(i["time"]), i["beer_brand"], i["customer"], i["user"]] for i in shipped]


		# Filled Kegs
		filled_count = c.execute("""	SELECT activity_log.keg_id, activity_log.time, beer_brands.name AS beer_brand, users.username AS user FROM activity_log 
										INNER JOIN beer_brands ON beer_brands.id = activity_log.beer_brand 
										LEFT JOIN users ON activity_log.user=users.Uid 
										WHERE activity_log.status="FULL_INV" AND activity_log.time >= SUBDATE(NOW(),7) 
										ORDER BY activity_log.time DESC """) 
		filled = c.fetchall()

		filled_list = [[i["keg_id"], str(i["time"]), i["beer_brand"], i["user"]] for i in filled]


		# Tapped Kegs
		tapped_count = c.execute("""	SELECT activity_log.keg_id, activity_log.time, beer_brands.name AS beer_brand, users.username AS user FROM activity_log 
										INNER JOIN beer_brands ON beer_brands.id = activity_log.beer_brand 
										LEFT JOIN users ON activity_log.user=users.Uid 
										WHERE activity_log.status="FULL_TAP" AND activity_log.time >= SUBDATE(NOW(),7) 
										ORDER BY activity_log.time DESC """) 
		tapped = c.fetchall()

		tapped_list = [[i["keg_id"], str(i["time"]), i["beer_brand"], i["user"]] for i in tapped]


		# Returned Kegs
		returned_count = c.execute("""	SELECT activity_log.keg_id, activity_log.time, beer_brands.name AS beer_brand, activity_log.customer, users.username AS user FROM activity_log 
										INNER JOIN beer_brands ON beer_brands.id = activity_log.beer_brand 
										LEFT JOIN users ON activity_log.user=users.Uid 
										WHERE activity_log.time >= SUBDATE(NOW(),7) AND activity_log.status="DIRTY" AND activity_log.customer IS NOT NULL AND activity_log.beer_brand IS NOT NULL
										ORDER BY activity_log.time DESC """) 
		returned = c.fetchall()

		returned_list = [[i["keg_id"], str(i["time"]), i["beer_brand"], i["customer"], i["user"]] for i in returned]



		return jsonify({"shipped": shipped_list, "shipped_count": shipped_count, "filled": filled_list, "filled_count": filled_count, "tapped": tapped_list, "tapped_count": tapped_count, "returned": returned_list, "returned_count": returned_count})

	except Exception as e:
		# failed connection
		return e


@app.route('/settings/')
def settings():
	if "uid" in session:
		return render_template("settings.html")

	return redirect(url_for('signin'))


@app.route('/view_inventory/', methods=["GET","POST"])
def view_inventory():
	if "uid" in session:
		
		c, conn = connection()

		inventory_items = c.execute(""" SELECT 	inventory.keg_id, inventory.keg_type, inventory.status, beer_brands.name AS beer_brand, 
												inventory.time_in, inventory.time_cleaned, inventory.time_filled, inventory.time_tapped, 
												inventory.time_shipped, inventory.customer, inventory.notes FROM inventory 
										LEFT JOIN beer_brands ON beer_brands.id = inventory.beer_brand 
										ORDER BY keg_id ASC""")
		
		inventory = c.fetchall()
		
		inv_list = []

		for i in inventory:
			keg_id = i["keg_id"]
			keg_type = i["keg_type"]
			status = i["status"]
			beer_brand = i["beer_brand"] if i["beer_brand"] else ""
			time_in = str(i["time_in"]) if i["time_in"] else ""
			time_cleaned = str(i["time_cleaned"]) if i["time_cleaned"] else ""		
			time_filled = str(i["time_filled"]) if i["time_filled"] else ""	
			time_tapped = str(i["time_tapped"]) if i["time_tapped"] else ""
			time_shipped = str(i["time_shipped"]) if i["time_shipped"] else ""
			customer = str(i["customer"]) if i["customer"] else ""
			notes = str(i["notes"]) if i["notes"] else ""

			inv_list.append([keg_id, keg_type, status, beer_brand, time_in, time_cleaned, time_filled, time_tapped, time_shipped, customer, notes])
		
		return render_template("view_inventory.html", inventory=inv_list,  account_name = session["username"])


	return redirect(url_for('signin'))


@app.route('/edit_inventory/', methods=["GET","POST"])
def edit_inventory():
	if "uid" in session:
		return render_template("edit_inventory.html", account_name = session["username"])

	return redirect(url_for('signin'))


@app.route('/logistics/', methods=["GET","POST"])
def logistics():
	if "uid" in session:
		return render_template("logistics.html", account_name = session["username"])

	return redirect(url_for('signin'))

@app.route('/setting/', methods=["GET","POST"])
def setting():
	if "uid" in session:

		c, conn = connection()

		beer_count = c.execute("""SELECT * FROM beer_brands""")
		
		beers = c.fetchall()
		
		beer_list = []

		for i in beers:
			beer_id = i["id"]
			beer_name = i["name"]
			active = i["active"]
			
			beer_list.append([beer_id, beer_name, active])
		
		#return render_template("view_inventory.html", inventory=inv_list,  account_name = session["username"])
		return render_template("setting.html", account_name = session["username"], beers=beer_list)

	return redirect(url_for('signin'))

@app.route('/get_beer_data/', methods=["POST"])
def get_beer_data():
	try:
		c, conn = connection()
		
		beer_count = c.execute("SELECT * FROM beer_brands")

		brands = c.fetchall()
		
		return jsonify({"epc": brands})
	except Exception as e:
		return jsonify({"error": e})

@app.route('/deactivate_brands/', methods=["POST"])
def deactivate_brands():
	try:
		c, conn = connection()
		idstring = request.form["beer_ids"]

		idarray = idstring.split(",")
		for element in idarray:
			beer_count = c.execute("UPDATE beer_brands SET active=0 WHERE id=" + element);
		conn.commit();

		return jsonify({"epc": idarray})
	except Exception as e:
		return jsonify({"error": e})

@app.route('/activate_brands/', methods=["POST"])
def activate_brands():
	try:
		c, conn = connection()
		idstring = request.form["beer_ids"]

		idarray = idstring.split(",")
		for element in idarray:
			beer_count = c.execute("UPDATE beer_brands SET active=1 WHERE id=" + element);
		conn.commit();
		
		return jsonify({"epc": idarray})
	except Exception as e:
		return jsonify({"error": e})

@app.route('/add_brand/', methods=["POST"])
def add_brand():
	try:
		c, conn = connection()
		string = request.form["name"]

		c.execute("INSERT INTO beer_brands active=1 name=" + string);
		conn.commit();
		
		return jsonify({"epc": string})
	except Exception as e:
		return jsonify({"error": e})


@app.route('/logistics_ajax_brands/', methods=["POST"])
def logistics_ajax_brands():
	try:
		# establish a connection to database
		c, conn = connection()
		
		# beer brands which has been shipped 
		brand_count = c.execute("""	SELECT activity_log.beer_brand AS `id`, beer_brands.name FROM `activity_log` 
									INNER JOIN `beer_brands` ON activity_log.beer_brand = beer_brands.id  
									WHERE (activity_log.status='FULL_OUT') 
									GROUP BY activity_log.beer_brand """) 

		brands = c.fetchall()

		brands_shipped = [brand["name"] for brand in brands]
		freq_shipped = []
		
		for month in xrange(1,13):
			month_freq = {}
			month_freq["date"] = str(datetime.datetime.today().year) + "-" + str(month)

			for brand in brands:
				freq_count = c.execute("SELECT count(*) As `count` FROM activity_log WHERE beer_brand= %s AND month(time)= %s"
										%(str(brand["id"]), str(month)))
				freq = c.fetchone()
				month_freq[brand["name"]] = freq["count"]

			freq_shipped.append(month_freq)		


		# beer brands which has been shipped 
		brand_count = c.execute("""	SELECT activity_log.beer_brand AS `id`, beer_brands.name FROM `activity_log` 
									INNER JOIN `beer_brands` ON activity_log.beer_brand = beer_brands.id  
									WHERE (activity_log.status='FULL_TAP') 
									GROUP BY activity_log.beer_brand """) 

		brands = c.fetchall()

		brands_tapped = [brand["name"] for brand in brands]
		freq_tapped = []
		
		for month in xrange(1,13):
			month_freq = {}
			month_freq["date"] = str(datetime.datetime.today().year) + "-" + str(month)

			for brand in brands:
				freq_count = c.execute("SELECT count(*) As `count` FROM activity_log WHERE beer_brand= %s AND month(time)= %s"
										%(str(brand["id"]), str(month)))
				freq = c.fetchone()
				month_freq[brand["name"]] = freq["count"]

			freq_tapped.append(month_freq)		
				

		return jsonify({"freq_shipped": freq_shipped, "brands_shipped": brands_shipped, "freq_tapped": freq_tapped, "brands_tapped": brands_tapped})

	except Exception as e:
		# failed connection
		return jsonify(e)


@app.route('/logistics_ajax_customers/', methods=["POST"])
def logistics_ajax_customers():
	try:
		# establish a connection to database
		c, conn = connection()
		
		customers_count = c.execute("SELECT customer FROM activity_log WHERE customer IS NOT NULL GROUP BY customer")
		customers = freq = c.fetchall()

		customers_info = []

		for customer in customers:
			name = customer["customer"]

			activity_count = c.execute("SELECT max(time) AS `last_activity` FROM activity_log WHERE (status='DIRTY' OR status='FULL_OUT') AND customer='%s'" %(name))
			activity = c.fetchone()
			last_activity = str(activity["last_activity"])

			keg_out_count = c.execute("SELECT count(*) AS `lifetime_total` FROM activity_log WHERE status='FULL_OUT' AND customer='%s'" %(name))
			keg_out = c.fetchone()
			lifetime_total = keg_out["lifetime_total"]

			returned_count = c.execute("SELECT count(*) AS `returned_total` FROM activity_log WHERE status='DIRTY' AND customer='%s'" %(name))
			returned = c.fetchone()
			returned_total = returned["returned_total"]
			current_total = lifetime_total - returned_total

			oldest_count = c.execute("""	SELECT min(self2_t.time) AS `oldest_shipped`
												FROM (
													SELECT time  FROM activity_log 
													INNER JOIN (
														SELECT keg_id, max(time) As `max` FROM activity_log 
														WHERE customer='%s' 
														GROUP BY keg_id
														) self_t 
													ON activity_log.keg_id=self_t.keg_id AND time=self_t.max 
													WHERE customer='%s' AND status='FULL_OUT' 
													GROUP BY activity_log.keg_id
													) As self2_t""" 
												%(name, name))
			oldest = c.fetchone()
			oldest_shipped = str(oldest["oldest_shipped"]) if oldest["oldest_shipped"] else '' 

			popular_count = c.execute(" SELECT beer_brands.name, count(*) AS freq FROM activity_log INNER JOIN beer_brands ON activity_log.beer_brand = beer_brands.id WHERE status='FULL_OUT' AND customer='%s' GROUP BY beer_brand ORDER BY freq DESC" %(name))
			popular = c.fetchall()
			popular_brands = ['', '', '']

			for i in xrange(min(len(popular),3)):
				popular_brands[i] = popular[i]["name"] 


			customers_info.append([name, lifetime_total, current_total, last_activity, oldest_shipped, popular_brands[0], popular_brands[1], popular_brands[2]]) 
				
	
		return jsonify(customers_info)

	except Exception as e:
		# failed connection
		return jsonify(e)	


if __name__ == "__main__":
	app.secret_key = 'some secret key'
	app.run(debug=True)
	# app.run()
