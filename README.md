# Kitchen Inventory

**A stock system for food and such. Currently a work in progress.**  
Originally made for personal use so don't expect anything too special.

_(The personal version also contained code for using a USB barcode scanner but it is removed in this repo version.)_

![](image)

## Requirements
- MySQL / MariaDB
- Python 3 with...
- Flask, flaskext.mysql, flask_basicauth, requests, 
- Gunicorn (or similar)

## Setup
1. Create a MySQL database and user.
2. Import the `sqlSetup.sql` file to get it ready for the inventory.
3. Fill in the DB details in `inventory.py`:
```app.config['MYSQL_DATABASE_USER'] = 'inventory'
  app.config['MYSQL_DATABASE_PASSWORD'] = 'SUPER_AWESOME_DB_PASSWORD_HERE'
  app.config['MYSQL_DATABASE_DB'] = 'inventory'
  app.config['MYSQL_DATABASE_HOST'] = 'localhost'
```    
4. If you wish to password protect the site fill in some login details in `inventory.py` also:
```
app.config['BASIC_AUTH_USERNAME'] = 'YOUR_USERNAME_HERE'
app.config['BASIC_AUTH_PASSWORD'] = 'YOUR_PASSWORD_HERE'
```
(Otherwise delete or comment out those lines.)
5. You can test the app by uncommenting:
```
#if __name__ == "__main__":
#	app.run(host='0.0.0.0', debug=True)
```
and then running `python3 inventory.py`.

## Issues & Notes
There may still be some bits left over from the barcode scanner code, feel free to submit requests and stuff to address this. Also, feel free to improve it and submit pull requests or whatever also. It's always cool to see what people come up with.  
If you're wondering why I didn't include the barcode scanner parts - it's because it is setup very particular to my system and the code is just awfully hacked together so it's staying private (for now at least.)
:)

## Credits
This project utilises the following projects and technologies:
- flask - http://flask.pocoo.org/
- MaterializeCSS - http://materializecss.com/
- Pixeden Foood Icons - http://themes-pixeden.com/font-demos/the-icons-set/food/
- jQuery - https://code.jquery.com
- Some other things that I've probably fogotten to list. :(
