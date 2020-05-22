from src import flask_tousan

if __name__ == "__main__":
    flask_tousan.app.run(debug = True, host='192.168.11.4', port=5000)
