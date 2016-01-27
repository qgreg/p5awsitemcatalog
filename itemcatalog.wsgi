import sys
sys.path.insert(0, "/var/www/itemcatalog")

from itemcatalog.createapp import create_app

# Create the app using the configuration
application = create_app('config.py')
if __name__ == "__main__":
	application.run()
