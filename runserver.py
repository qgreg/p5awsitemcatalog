from itemcatalog.createapp import create_app

# Create the app using the configuration
app = create_app('config.py')
if __name__ == "__main__":
	app.run()
