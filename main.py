from flask import Flask, render_template, request
from clients import CountryInfo

app = Flask(__name__)
informer = CountryInfo()


@app.route("/form")
def form():
    return render_template("form.html")


@app.route("/data", methods=["POST", "GET"])
def data():
    if request.method == "GET":
        return (
            f"The URL /data is accessed directly. Try going to '/form' to submit form"
        )
    if request.method == "POST":
        response = informer(request.form["country"])
        # We do request for all the information because it is the only opportunity api provides. 
        # We cannot ask only official language or weather stats
        required_data = request.form["required"]
        if response['text'] != "":
            form_data = {
                "full_name": "",
                "lang": "",
                "weather_charts": {
                    "temp_chart_url": "",
                    "press_char_url": "",
                    "text": ""
                },
                "text": response['text']
            }
        else:
            if required_data == "all":
                form_data = {
                    "full_name": response['full_name'],
                    "lang": "The official language is " + response['official_languages'][0],
                    "weather_charts": response['weather_chart_link'],
                    "text": response['text']
                }
            elif required_data == "fullname":
                form_data = {
                    "full_name": response['full_name'],
                    "lang": "",
                    "weather_charts": {
                        "temp_chart_url": "",
                        "press_char_url": "",
                        "text": "you did not request stats"
                    },
                    "text": response['text']
                }
            elif required_data == "lang":
                form_data = {
                    "full_name": "",
                    "lang": "The official language is " + response['official_languages'][0],
                    "weather_charts": {
                        "temp_chart_url": "",
                        "press_char_url": "",
                        "text": "you did not request stats"
                    },
                    "text": response['text']
                }
            else:
                form_data = {
                    "full_name": "",
                    "lang": "",
                    "weather_charts": response['weather_chart_link'],
                    "text": response['text']
                }
        return render_template("data.html", form_data=form_data)


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
