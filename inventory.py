from flask import Flask, render_template, redirect, request, url_for
from flaskext.mysql import MySQL
from flask_basicauth import BasicAuth
import requests
import configparser
from random import randint
import sys

# Configuration
app = Flask(__name__)
config = configparser.ConfigParser()
config.read('config.ini')

version = "0.1"

# Setup protection
app.config['BASIC_AUTH_USERNAME'] = config['basicAuth']['username']
app.config['BASIC_AUTH_PASSWORD'] = config['basicAuth']['password']
app.config['BASIC_AUTH_FORCE'] = config['basicAuth']['forceAuth']
basic_auth = BasicAuth(app)
 
# Set the MySQL configuration
app.config['MYSQL_DATABASE_USER'] = config['mySQL']['username']
app.config['MYSQL_DATABASE_PASSWORD'] = config['mySQL']['password']
app.config['MYSQL_DATABASE_DB'] = config['mySQL']['database']
app.config['MYSQL_DATABASE_HOST'] = config['mySQL']['host']
mysql = MySQL(app)
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

		return render_template('index.html', items=results, editMode=editMode, version=version, config=config['siteSettings'])

	except Exception as e:
		return redirect('/error/{}'.format(e))

# View all from category page
@app.route('/table/<int:type>')
def makeTable(type):
	try:
		conn = mysql.connect()
		cur = conn.cursor()
		cur.execute('SELECT * FROM items WHERE `type`="{}"'.format(type))
		results = cur.fetchall()

		return render_template('/inc/table.html', items=results, config=config['siteSettings'])

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

		return render_template('nostock.html', items=results, editMode=editMode, config=config['siteSettings'])

	except Exception as e:
		return redirect('/error/{}'.format(e))	
	
# Error Page
@app.route('/error/<string:e>')
def error(e):
	return render_template('error.html', error=e, version=version, config=config['siteSettings'])

# Edit name page
@app.route('/edititem/<int:bc>')
def edititem(bc):

	try:
		conn = mysql.connect()
		cur = conn.cursor()
		cur.execute('SELECT * FROM items WHERE `barcode`={}'.format(bc))
		results = cur.fetchall()

		return render_template('edititem.html', item=results, config=config['siteSettings'])

	except Exception as e:
		return redirect('/error/{}'.format(e))
	
	
# Update the product name to something else
@app.route('/updateitem',methods=['POST'])
def updateitem():
	try:
		_name = request.form['item_name']
		_barcode = request.form['item_bc']
		_type = request.form['item_type']
		
		if _name and _barcode:
			conn = mysql.connect()
			cur = conn.cursor()
			cur.execute('UPDATE `items` SET `name`="{}", `type`="{}" WHERE `barcode`= {}'.format(_name, _type, _barcode))
			conn.commit()
		
		else:
			raise RuntimeError("There was an error with the form")

		return redirect(url_for('main'))

	except Exception as e:
		return redirect('/error/{}'.format(e))
	
# Add new item manually
@app.route('/add')
@app.route('/add/<bc>')
def add(bc = None):

	if (bc != None):
		try:
			if checkAmount(bc) <= 0:
				conn = mysql.connect()
				cur = conn.cursor()
				cur.execute('UPDATE `items` SET `amount`=1 WHERE `barcode`= {}'.format(bc))
				conn.commit()	
			else:
				conn = mysql.connect()
				cur = conn.cursor()
				cur.execute('UPDATE `items` SET `amount`=`amount`+1 WHERE `barcode`= {}'.format(bc))
				conn.commit()

			return redirect('/edit/true')

		except Exception as e:
			return redirect('/error/{}'.format(e))

	else:
		return render_template('add.html', config=config['siteSettings'])

# Generate a barcode for the DB if barcode is disabled or missing on item
def barcodeGenerator():
	try:

		# Set amount of digits in barcode and generate one
		digits = 7
		range_start = 10 ** (digits - 1)
		range_end = (10 ** digits) - 1
		bc = randint(range_start, range_end)

		conn = mysql.connect()
		cur = conn.cursor()
		cur.execute('SELECT * FROM items WHERE `barcode`={}'.format(bc))
		results = cur.fetchall()

		if len(results) == 0:
			return bc

		else:
			barcodeGenerator()

	except Exception as e:
		return redirect('/error/{}'.format(e))

# Add to the DB
@app.route('/additem', methods=['POST'])
def addItem():
	try:

		_barcode = request.form['barcode']
		_name = request.form['item_name']
		_amount = request.form['amount']
		_type = request.form['type']

		# Deal with the barcode
		if _barcode == "off":
			# If barcodes are disabled, generate a random 7 digit one to keep DB happy
			_barcode = barcodeGenerator()

		if _barcode and _name and _amount and _type:

			try:
				if config['siteSettings']['enablebarcodes'] == "on":
					if sendToOpenFoods(_barcode) != "Unknown Product":
						itemName = sendToOpenFoods(_barcode)
					else:
						itemName = _name
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
@app.route('/remove/<int:bc>')
def remove(bc):
	try:
		conn = mysql.connect()
		cur = conn.cursor()
		cur.execute('UPDATE `items` SET `amount`=`amount`-1 WHERE `barcode`= {}'.format(bc))
		conn.commit()

		return redirect('/edit/true')

	except Exception as e:
		return redirect('/error/{}'.format(e))

# Check amount of items in the inventory DB
def checkAmount(bc):
	try:
		conn = mysql.connect()
		cur = conn.cursor()
		cur.execute('SELECT `amount` FROM `items` WHERE `barcode`= {}'.format(bc))
		results = cur.fetchone()
		return results[0]

	except Exception as e:
		return redirect('/error/{}'.format(e))

# Completely delete an item from the DB
@app.route('/delete/<int:bc>')
def deleteItem(bc):
	try:
		conn = mysql.connect()
		cur = conn.cursor()
		cur.execute('DELETE FROM `items` WHERE `barcode`= {}'.format(bc))
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


# Settings Page
@app.route('/settings')
@basic_auth.required
def settings():
	return render_template('settings.html', version=version, config=config['siteSettings'], saved="false")

@app.route('/settings/save', methods=['POST'])
@basic_auth.required
def saveSettings():
	try:
		_siteTitle = request.form['siteTitle']
		_darkMode = request.form.get("darkMode")
		_enableBarcodes = request.form.get("enableBarcodes")

		if _siteTitle:

			try:
				# Update the config file
				cfg = open("config.ini", 'w')
				config.set('siteSettings', 'sitetitle', _siteTitle)

				if _darkMode == None:
					config.set('siteSettings', 'darkmode', 'off')
				else:
					config.set('siteSettings', 'darkmode', 'on')

				if _enableBarcodes == None:
					config.set('siteSettings', 'enablebarcodes', 'off')
				else:
					config.set('siteSettings', 'enablebarcodes', 'on')

				config.write(cfg)
				cfg.close()
				return "ok"

			except Exception as e:
				return redirect('/error/{}'.format(e))

		else:
			raise RuntimeError("There was an error with the form")

	except Exception as e:
		return redirect('/error/{}'.format(e))


# Check if test mode
if config['testMode']['active'] == "True":
	if __name__ == "__main__":
		app.run(host=config['testMode']['host'])