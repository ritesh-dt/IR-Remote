import os
from flask import Flask
from flask import redirect, url_for, request, send_file
from zipfile import ZipFile

app = Flask(__name__)
@app.route("/")
def home():
	if request.method == "GET":
		dropdown_type = request.form["dropdown_type"]
		selection = request.form["selection"]
		if dropdown_type == "None":
			return "|".join([item for item in os.listdir("Database")\
								 if os.path.isdir(f"Database/{item}")])
		elif dropdown_type == "add":
			return send_file(f"Database/{selection}.zip")
		else:
			return "|".join([item.split(".")[0] for item in os.listdir(f"Database/{selection}")\
								if item.split(".")[0]])



if __name__ == "__main__":
	app.run(debug=True)