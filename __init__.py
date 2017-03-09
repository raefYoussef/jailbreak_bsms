from flask import Flask, render_template, flash, url_for

app = Flask(__name__)

@app.route('/', )
def signin():
	return render_template("signin.html", methods=['POST'])


if __name__ == "__main__":
    app.run()
