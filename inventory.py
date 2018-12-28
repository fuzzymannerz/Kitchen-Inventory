from flask import Flask, render_template, redirect, request, url_for
from flaskext.mysql import MySQL
from flask_basicauth import BasicAuth
import requests

app = Flask(__name__)

# Setup protection
app.config['BASIC_AUTH_USERNAME'] = 'YOUR_USERNAME_HERE'
app.config['BASIC_AUTH_PASSWORD'] = 'YOUR_PASSWORD_HERE'
app.config['BASIC_AUTH_FORCE'] = True

basic_auth = BasicAuth(app)

# MySQL Settings
mysql = MySQL(app)
 
# MySQL configuration
app.config['MYSQL_DATABASE_USER'] = 'inventory'
app.config['MYSQL_DATABASE_PASSWORD'] = 'SUPER_AWESOME_DB_PASSWORD_HERE'
app.config['MYSQL_DATABASE_DB'] = 'inventory'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


# Set the index page
@app.route('/')
@app.route('/edit/<editMode>')
@basic_auth.required
def main(editMode = False):
	try:
		conn = mysql.connect()
		cur = conn.cursor()
		cur.execute('SELECT * FROM items')
		results = cur.fetchall()

		return render_template('index.html', items=results, editMode=editMode)

	except Exception as e:
		return redirect('/error/{}'.format(e))

# View all from category page
@app.route('/viewall/<int:typeCat>')
@app.route('/viewall/<int:typeCat>/edit/<editMode>')
@basic_auth.required
def viewall(typeCat, editMode=False):
	try:
		conn = mysql.connect()
		cur = conn.cursor()
		cur.execute('SELECT * FROM items WHERE `type`="{}"'.format(typeCat))
		results = cur.fetchall()

		return render_template('viewall.html', items=results, editMode=editMode, type=typeCat)

	except Exception as e:
		return redirect('/error/{}'.format(e))

# View items that are no longer in stock
@app.route('/nostock')
@app.route('/nostock/edit/<editMode>')
def nostock(editMode = False):
	try:
		conn = mysql.connect()
		cur = conn.cursor()
		cur.execute('SELECT * FROM items')
		results = cur.fetchall()

		return render_template('nostock.html', items=results, editMode=editMode)

	except Exception as e:
		return redirect('/error/{}'.format(e))	
	
# Error Page
@app.route('/error/<string:e>')
def error(e):
	return render_template('error.html', error=e)

# Edit name page
@app.route('/editname/<int:id>/<string:name>/<int:type>')
def editname(name, id, type):
	try:
		return render_template('editname.html', itemName=name, itemID=id, itemType=type)

	except Exception as e:
		return redirect('/error/{}'.format(e))	
	
	
# Update the product name to something else
@app.route('/updatename',methods=['POST'])
def updatename():
	try:
		_name = request.form['item_name']
		_id = request.form['item_id']
		_type = request.form['item_type']
		
		if _name and _id:
			conn = mysql.connect()
			cur = conn.cursor()
			cur.execute('UPDATE `items` SET `name`="{}", `type`="{}" WHERE `id`= {}'.format(_name, _type, _id))
			conn.commit()
		
		else:
			raise RuntimeError("There was an error with the form")

		return redirect(url_for('main'))

	except Exception as e:
		return redirect('/error/{}'.format(e))
	
# Add new item manually
@app.route('/add')
@app.route('/add/<id>')
def add(id = None):

	if (id != None):
		try:
			if checkAmount(id) <= 0:
				conn = mysql.connect()
				cur = conn.cursor()
				cur.execute('UPDATE `items` SET `amount`=1 WHERE `id`= {}'.format(id))
				conn.commit()	
			else:
				conn = mysql.connect()
				cur = conn.cursor()
				cur.execute('UPDATE `items` SET `amount`=`amount`+1 WHERE `id`= {}'.format(id))
				conn.commit()

			return redirect('/edit/true')

		except Exception as e:
			return redirect('/error/{}'.format(e))

	else:
		return render_template('add.html')

# Add to the DB
@app.route('/additem',methods=['POST'])
def addItem():
	try:
		_barcode = request.form['barcode']
		_name = request.form['item_name']
		_amount = request.form['amount']
		_type = request.form['type']

		if _barcode and _name and _amount and _type:

			try:
				
				if sendToOpenFoods(_barcode) != "Unknown Product":
					itemName = sendToOpenFoods(_barcode)
				else:
					itemName = _name
					
				conn = mysql.connect()
				cur = conn.cursor()
				cur.execute('INSERT INTO `items` (`name`, `barcode`, `amount`, `type`) VALUES ("{}", {}, {}, {})'.format(itemName, _barcode, _amount, _type))
				conn.commit()
				return redirect(url_for('main'))

			except Exception as e:
				return redirect('/error/{}'.format(e))

		else:
			raise RuntimeError("There was an error with the form")


	except Exception as e:
		return redirect('/error/{}'.format(e))


# Remove items manually
@app.route('/remove/<int:id>')
def remove(id):
	try:
		conn = mysql.connect()
		cur = conn.cursor()
		cur.execute('UPDATE `items` SET `amount`=`amount`-1 WHERE `id`= {}'.format(id))
		conn.commit()

		return redirect('/edit/true')

	except Exception as e:
		return redirect('/error/{}'.format(e))


# Check amount of items in the inventory DB
def checkAmount(id):
	try:
		conn = mysql.connect()
		cur = conn.cursor()
		cur.execute('SELECT `amount` FROM `items` WHERE `id`= {}'.format(id))
		results = cur.fetchone()
		return results[0]

	except Exception as e:
		return redirect('/error/{}'.format(e))

# Completely delete an item from the DB
@app.route('/delete/<int:id>')
def deleteItem(id):
	try:
		conn = mysql.connect()
		cur = conn.cursor()
		cur.execute('DELETE FROM `items` WHERE `id`= {}'.format(id))
		conn.commit()
		
		return redirect('/')

	except Exception as e:
		return redirect('/error/{}'.format(e))
	
# Connect to the openfoodfacts.org API
def sendToOpenFoods(bc):
	url = "http://world.openfoodfacts.org/api/v0/product/" + bc + ".json"

	try:
		r = requests.get(url)
		data = r.json()

		# Deal with response
		if data['status_verbose'] == "product found": # If the product is in the DB
			return (data['product']['product_name'] + " (" + data['product']['quantity'].replace(" ", "") + ")")
		else:
			return "Unknown Product"

	except Exception as e:
		return redirect('/error/{}'.format(e))


# Run the app
#if __name__ == "__main__":
#	app.run(host='127.0.0.1', debug=True)