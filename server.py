import json
from urllib.parse import urlencode
from pprint import pprint

import flask
import requests
from flask import Flask, request
from flask_cors import CORS


app = Flask(__name__)
cors = CORS(app)


@app.route('/', defaults={'path': ''}, methods=["GET", "POST"])
@app.route('/<path:path>', methods=["GET", "POST"])
def catch_all(path):
    reload = False
    new_path = f"https://zen.yandex.ru/{path}?{urlencode(request.args)}"
    headers = dict(request.headers)

    for k in headers:
        headers[k] = headers[k].replace("zenautoplay.ru", "zen.yandex.ru")

    if request.method == "POST":  
        data = request.data

        if path == "editor-api/v2/update-publication-content":
            j = request.json
            content = json.loads(j["articleContent"]["contentState"])
            for block in content["blocks"]:
                if block["type"] == "atomic:embed" and block["data"]["embedData"]["type"] == "yandex-efir":
                    if not "#" in block["data"]["embedData"]["stringParams"]:
                        reload = True
                        block["data"]["embedData"]["stringParams"] = block["data"]["embedData"]["stringParams"].replace("&autoplay=0", "") + "#autoplay=1"
            j["articleContent"]["contentState"] = json.dumps(content)
            pprint(j)
            data = json.dumps(j)
        resp = requests.post(new_path, data=data, headers={k: v for k, v in headers.items() if k not in ["Host", "Content-Length", "Cookie"]}, cookies=request.cookies)
    else:
        resp = requests.get(new_path, headers=headers, cookies=request.cookies)

    r = flask.make_response(resp.text.replace("https://zen.yandex.ru", "https://zenautoplay.ru"))
    for k, v in resp.cookies.items():
        r.set_cookie(k, v)
    if reload:
        r.headers["Reload"] = "true"
    return r, resp.status_code  
if __name__ == "__main__":
    app.run()
