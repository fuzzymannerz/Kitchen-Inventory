# Kitchen Inventory

**A stock system for food and such. Currently a work in progress.**  


![](https://i.imgur.com/4YBlx2e.png)

## Requirements
- MySQL / MariaDB
- Python 3 with...
- Flask, flask-mysql, flask-basicauth, requests, configparser
- Gunicorn (or similar)

## Setup
1. Create a MySQL database and user and grant it full access to said database.
2. Import the `sqlSetup.sql` file to get it ready for the inventory.
3. Fill in the DB details in `config.ini`.  
4. If you wish to password protect the site fill in some login details in `config.ini` also:

5. You can test the app by setting `active = True` under the `[testMode]` section of the `config.ini` file and then running `python3 inventory.py`.  
You can then access the site at http://localhost:5000.  
If you are running it on another machine change `127.0.0.1` to `0.0.0.0`.  
_(Depending on your setup, you may also need to forward port 5000 if running it from another machine.)_

If you are to leave it running then it is recommended to use something like [Gunicorn](https://gunicorn.org/) to serve the files instead.  
For example: `gunicorn -b 0.0.0.0:5000 inventory:app --daemon`.

## Removing Basic Auth Login
If you don't wish to have an auth login for the site you can remove it as follows:  
1. Remove or comment out the following lines in `inventory.py`:  
```
app.config['BASIC_AUTH_USERNAME'] = config['basicAuth']['username']
app.config['BASIC_AUTH_PASSWORD'] = config['basicAuth']['password']
app.config['BASIC_AUTH_FORCE'] = config['basicAuth']['forceAuth']
basic_auth = BasicAuth(app)
```  
as well as all instances of `@basic_auth.required` in the same file.

## Settings
There is a settings page accessible from `/settings` or by clicking the settings menu link.  
Here you can change the title of the site as well as activate and deactivate a dark mode and disable manual barcode usage.  

_More options will be here as the project develops._

---

## Contributions
If you feel you have something to add or make better or whatever feel free to contribute to the project by forking and submitting pull requests. There is also the [development branch](https://github.com/fuzzymannerz/Kitchen-Inventory/tree/development) which contains the latest ideas being worked on.  
Don't use it though in production as it's most likely broken. ;)

## Credits
This project utilises the following projects and technologies:
- flask - http://flask.pocoo.org/
- MaterializeCSS - http://materializecss.com/
- Pixeden Foood Icons - http://themes-pixeden.com/font-demos/the-icons-set/food/
- jQuery - https://code.jquery.com
- Some other things that I've probably fogotten to list. :(
