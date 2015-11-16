from itemcatalog.createapp import create_app
app = create_app('config.py')
app.run(host='0.0.0.0', port=5000)