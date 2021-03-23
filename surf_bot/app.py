from flask import Flask

from surf_bot.sign_up import SurfSpotConditions

app = Flask(__name__)

SURF_CONDITIONS = SurfSpotConditions()


@app.route("/sms", methods=["POST"])
def sms():

    return SURF_CONDITIONS.sms_build()


if __name__ == "__main__":
    app.run()
