# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template_string, Response, request
import requests, time, json

app = Flask(__name__)

# ---------------------------------
# main ----------------------------
# ---------------------------------

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>اتوموبی اتومیشن</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f5f5f5;
            display: flex;
            flex-direction: column;
            align-items: center;
            margin: 0;
            padding: 0;
        }
        h1 {
            color: #800080; /* بنفش */
            margin: 50px 0 10px 0;
            font-size: 3em;
        }
        hr {
            width: 50%; /* نصف صفحه */
            border: 3px solid #800080; /* بنفش */
            border-radius: 2px;
            margin-bottom: 30px;
        }
        .cards {
            display: flex;
            gap: 30px;
            flex-wrap: wrap;
            justify-content: center;
        }
        .card {
            background-color: #ffffff;
            width: 220px;
            height: 150px;
            border-radius: 15px;
            box-shadow: 0 6px 18px rgba(0,0,0,0.2);
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 1.2em;
            font-weight: bold;
            text-align: center;
            cursor: pointer;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .card:hover {
            transform: translateY(-10px);
            box-shadow: 0 12px 25px rgba(0,0,0,0.3);
        }
        a {
            text-decoration: none;
            color: inherit;
        }
    </style>
</head>
<body>
    <h1>اتوموبی اتومیشن</h1>
    <hr>
    <div class="cards">
        <a href="/form-to-json">
            <div class="card">تبدیل فرم به جیسون</div>
        </a>
        <a href="/attributes-scraping">
            <div class="card">اتریبیوت اسکریپینگ</div>
        </a>
    </div>
</body>
</html>
"""


@app.route("/")
def home():
    return html_content


# ---------------------------------
# form to json --------------------
# ---------------------------------

form_to_json = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>اتوموبی اتومیشن</title>
  <style>
    body {
      font-family: sans-serif;
      background: #f9fafb;
      margin: 0;
      padding: 20px;
      display: flex;
      justify-content: center;
    }
    .container {
      max-width: 800px;
      background: white;
      padding: 20px;
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      width: 100%;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }
    .title-box {
      width: 50%;
      grid-column: span 2;
      background: white; /* سفید بمونه */
      color: #8b5cf6;    /* متن بنفش */
      padding: 12px;
      border-radius: 12px;
      text-align: center;
      font-weight: bold;
      font-size: 1.2em;
      border-bottom: 1px solid #8b5cf6;
      margin: 0 auto;
      margin-bottom: 30px;
    }

    h1, h2 {
      margin-top: 0;
      text-align: center;
    }
    .field {
      border: 1px solid #ddd;
      padding: 10px;
      border-radius: 8px;
      margin-bottom: 10px;
      display: grid;
      grid-template-columns: 1fr 1fr auto;
      gap: 10px;
      align-items: end;
    }
    input {
      width: 100%;
      padding: 8px;
      border: 1px solid #ccc;
      border-radius: 6px;
    }
    button {
      cursor: pointer;
      padding: 8px 12px;
      border-radius: 6px;
      border: 1px solid #ccc;
      background: #f3f4f6;
    }
    button:hover { background: #e5e7eb; }
    .primary { background: #4f46e5; color: white; border: none; }
    .primary:hover { background: #4338ca; }
    pre {
      background: #f3f4f6;
      padding: 10px;
      border-radius: 8px;
      overflow-x: auto;
      white-space: pre-wrap;
    }
    .json-panel {
      display: flex;
      flex-direction: column;
      gap: 10px;
      direction: ltr;
    }
    .copied {
      color: green;
      font-size: 0.9em;
      text-align: center;
    }
  </style>
</head>
<body>
  <div class="container">
    <!-- عنوان بالای فرم -->
    <div class="title-box">فرم به جیسون</div>

    <!-- فرم -->
    <div>
      <h1>فرم ورودی</h1>
      <div id="fields"></div>
      <div style="margin-top:10px; display:flex; gap:10px;">
        <button onclick="addField()">➕ افزودن فیلد</button>
        <button onclick="resetFields()">🔄 بازنشانی</button>
      </div>
      <div style="margin-top:10px; display:flex; gap:10px; align-items:center;">
        <button class="primary" onclick="buildAndCopyJson()">🛠️📋 ساخت و کپی JSON</button>
        <button onclick="clearOutput()">🗑️ پاک کردن خروجی</button>
        <span style="margin-right:auto; font-size:0.9em; color:gray;">فیلدها: <span id="count">0</span></span>
      </div>
    </div>

    <!-- خروجی -->
    <div class="json-panel">
      <h2>خروجی JSON</h2>
      <pre id="output" dir="ltr">{}</pre>
      <div id="copiedMsg" class="copied" style="display:none;">✔ کپی شد</div>
    </div>
  </div>

  <script>
    let fields = [];
    let outputJson = null;

    function renderFields() {
      const container = document.getElementById("fields");
      container.innerHTML = "";
      fields.forEach((f, idx) => {
        const div = document.createElement("div");
        div.className = "field";
        div.innerHTML = `
          <div>
            <label style="font-size:0.8em;color:gray;">عنوان</label>
            <input value="${f.title}" oninput="updateField(${f.id}, 'title', this.value)" placeholder="عنوان ${idx+1}" />
          </div>
          <div>
            <label style="font-size:0.8em;color:gray;">مقدار</label>
            <input value="${f.value}" oninput="updateField(${f.id}, 'value', this.value)" placeholder="مقدار ${idx+1}" />
          </div>
          <div style="display:flex; gap:5px;">
            <button onclick="removeField(${f.id})">🗑</button>
            <button onclick="duplicateField(${f.id})">📑</button>
          </div>
        `;
        container.appendChild(div);
      });
      document.getElementById("count").innerText = fields.length;
    }

    function addField() {
      fields.push({id: Date.now()+Math.random(), title:"", value:""});
      renderFields();
    }

    function removeField(id) {
      if(fields.length === 1) return;
      fields = fields.filter(f => f.id !== id);
      renderFields();
    }

    function duplicateField(id) {
      const f = fields.find(x => x.id === id);
      const idx = fields.indexOf(f);
      const copy = {id: Date.now()+Math.random(), title: f.title, value: f.value};
      fields.splice(idx+1, 0, copy);
      renderFields();
    }

    function updateField(id, key, val) {
      fields = fields.map(f => f.id === id ? {...f, [key]: val} : f);
    }

    function resetFields() {
      fields = [{id: Date.now(), title:"", value:""}];
      renderFields();
    }

    function buildAndCopyJson() {
      const obj = {};
      fields.forEach(f => {
        if(f.title.trim()) {
          obj[f.title.trim()] = f.value.trim();
        }
      });
      outputJson = obj;
      const jsonText = JSON.stringify(outputJson, null, 2);
      document.getElementById("output").innerText = jsonText;

      navigator.clipboard.writeText(jsonText).then(() => {
        const msg = document.getElementById("copiedMsg");
        msg.style.display = "block";
        setTimeout(() => msg.style.display = "none", 2000);
      });
    }

    function clearOutput() {
      outputJson = null;
      document.getElementById("output").innerText = "{}";
    }

    resetFields();
  </script>
</body>
</html>

"""


@app.route("/form-to-json")
def form_to_json_page():
    return form_to_json


# ---------------------------------
# attributes scraping -------------
# ---------------------------------


# ---------------- Helper Functions ----------------
def safe_request(url, retries=3, wait=5):
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(wait)
            else:
                raise


def extract_plp_urls(products):
    urls = []
    for p in products:
        try:
            dkp = p.get("url").get("uri").split("/")[2].split("-")[1]
            urls.append(f"https://www.digikala.com/product/dkp-{dkp}/")
        except:
            continue
    return urls


def extract_product_data(pdp_url):
    dkp_number = pdp_url.rstrip("/").split("-")[-1]
    api_url = f"https://api.digikala.com/v2/product/{dkp_number}/"
    resp = safe_request(api_url)
    product = resp.json()["data"]["product"]
    title = product.get("title_fa")
    attributes = []
    try:
        attributes = [
            {attr.get("title"): attr.get("values")}
            for attr in product.get("specifications")[0].get("attributes")
        ]
    except:
        pass
    return {"title": title, "attributes": attributes, "url": pdp_url}


# ---------------- Routes ----------------
@app.route("/attributes-scraping")
def index():
    html = """
    <!doctype html>
    <html lang="fa">
    <head>
      <meta charset="UTF-8">
      <title>اتوموبی اتومیشن</title>
      <style>
        body { font-family: Tahoma, Arial; direction: rtl; text-align: right; margin: 20px; background: #f5f5f5; }
        h1 { color: purple; text-align: center; margin-bottom: 5px; }
        .title-line { width: 50%; height: 4px; background: purple; border-radius: 20px; margin: 0 auto 20px auto; }
        input { padding: 10px; font-size: 16px; border-radius: 5px; border: 1px solid #ccc; width: 70%; }
        button { padding: 10px 20px; font-size: 16px; border-radius: 5px; border: none; background: purple; color: white; cursor: pointer; margin-top: 10px; }
        button:hover { background: #800080; }
        .progress-container { margin-bottom: 20px; }
        progress { width: 100%; height: 25px; border-radius: 5px; }
        #log { max-height: 400px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; background: white; border-radius: 5px; }
        .error { background: #ffcccc; border-radius: 8px; padding: 10px; margin: 8px 0; }
        .container { max-width: 1000px; margin: auto; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 0 15px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: right; }
        th { background: #eee; }
        td a { color: purple; text-decoration: none; }
        td a:hover { text-decoration: underline; }
      </style>
    </head>
    <body>
      <h1>اتریبیوت اسکریپینگ</h1>
      <div class="title-line"></div>

      <div class="container">
        <input type="text" id="category" placeholder="لینک دسته‌بندی دیجی‌کالا را وارد کنید">
        <button onclick="startScrape()">شروع اسکریپ</button>

        <div class="progress-container">
          <h3>در حال یافتن محصولات...</h3>
          <progress id="plp-bar" value="0" max="1"></progress>
          <span id="plp-text"></span>
        </div>

        <div class="progress-container">
          <h3>در حال پردازش محصولات صفحه جاری...</h3>
          <progress id="pdp-bar" value="0" max="1"></progress>
          <span id="pdp-text"></span>
        </div>

        <h3>ویژگی‌های جدید یافته شده:</h3>
        <table id="new-attributes-table">
          <thead>
            <tr><th>ویژگی</th><th>مثال</th></tr>
          </thead>
          <tbody></tbody>
        </table>

        <h3>لیست محصولات:</h3>
        <div id="log">
          <table id="product-table">
            <thead>
              <tr>
                <th>عنوان محصول</th>
                <th>ویژگی‌ها</th>
                <th>لینک محصول</th>
              </tr>
            </thead>
            <tbody id="product-body"></tbody>
          </table>
        </div>
      </div>

      <script>
      let stoppedDueToError = false;
      let evtSource = null;
      let seenAttributes = new Set();

      function startScrape() {
          if(evtSource) { evtSource.close(); evtSource = null; }

          stoppedDueToError = false;
          seenAttributes = new Set();
          const category = document.getElementById("category").value;
          const plpBar = document.getElementById("plp-bar");
          const plpText = document.getElementById("plp-text");
          const pdpBar = document.getElementById("pdp-bar");
          const pdpText = document.getElementById("pdp-text");
          const tbody = document.getElementById("product-body");
          tbody.innerHTML = "";
          document.querySelector("#new-attributes-table tbody").innerHTML = "";
          plpBar.value = 0; pdpBar.value = 0;
          plpText.innerText = ""; pdpText.innerText = "";

          evtSource = new EventSource("/scrape?category_url=" + encodeURIComponent(category));

          evtSource.onmessage = function(e) {
              const msg = JSON.parse(e.data);
              if(stoppedDueToError) return;

              if(msg.type=="PLP_PROGRESS") {
                  plpBar.max = msg.total_pages;
                  plpBar.value = msg.page;
                  plpText.innerText = `صفحه ${msg.page} از ${msg.total_pages} بارگذاری شد (${msg.urls.length} محصول)`;

                  // --------------------- هر صفحه PDP bar از صفر شروع شود ---------------------
                  pdpBar.max = msg.urls.length;
                  pdpBar.value = 0;
                  pdpText.innerText = `0 / ${pdpBar.max} محصولات پردازش شد`;
              }
              else if(msg.type=="PDP_PROGRESS") {
                  pdpBar.value += 1;
                  pdpText.innerText = `${pdpBar.value} / ${pdpBar.max} محصول پردازش شد`;

                  const tr = document.createElement("tr");
                  const attrs = msg.data.attributes
                                .map(a => Object.entries(a)
                                .map(([k,v]) => `${k}: ${v.join(", ")}`)
                                .join("<br>"))
                                .join("<hr>");
                  tr.innerHTML = `<td>${msg.data.title}</td><td>${attrs}</td><td><a href="${msg.data.url}" target="_blank">مشاهده</a></td>`;
                  tbody.appendChild(tr);

                  const attrTbody = document.querySelector("#new-attributes-table tbody");
                  msg.data.attributes.forEach(a => {
                      Object.entries(a).forEach(([attrName, values]) => {
                          if(!seenAttributes.has(attrName)) {
                              seenAttributes.add(attrName);
                              const trAttr = document.createElement("tr");
                              trAttr.innerHTML = `<td>${attrName}</td><td>${values[0] || ""}</td>`;
                              attrTbody.appendChild(trAttr);
                          }
                      });
                  });
              }
              else if(msg.type=="ERROR") {
                  stoppedDueToError = true;
                  const logDiv = document.getElementById("log");
                  const div = document.createElement("div");
                  div.classList.add("error");
                  div.innerText = `خطا: ${msg.msg}`;
                  logDiv.prepend(div);
                  pdpText.innerText = "اسکریپت متوقف شد! لطفا دوباره لینک وارد کنید.";
                  if(evtSource) { evtSource.close(); evtSource = null; }
              }
              else if(msg.type=="DONE") {
                  pdpText.innerText = "تمام شد!";
                  if(evtSource) { evtSource.close(); evtSource = null; }
              }
          };

          evtSource.onerror = function() {
              stoppedDueToError = true;
              if(evtSource) { evtSource.close(); evtSource = null; }
              pdpText.innerText = "کاربر مرورگر را بسته یا صفحه را ترک کرد، اسکریپت متوقف شد.";
          };
      }
      </script>
    </body>
    </html>
    """
    return render_template_string(html)


# ---------------- Scrape Route ----------------
@app.route("/scrape")
def scrape():
    category_url = request.args.get("category_url")

    def generate():
        try:
            category = category_url.split("/")[-2].split("-", 1)[1]
            seen_urls = set()
            PLP_URL = f"https://api.digikala.com/v1/categories/{category}/search/?page="

            page = 1
            while True:
                resp = safe_request(PLP_URL + str(page))
                data = resp.json()["data"]
                urls = extract_plp_urls(data["products"])

                yield f"data: {json.dumps({'type': 'PLP_PROGRESS', 'page': page, 'total_pages': data['pager']['total_pages'], 'urls': urls})}\n\n"

                for url in urls:
                    if url in seen_urls:
                        continue
                    seen_urls.add(url)
                    try:
                        product = extract_product_data(url)
                        yield f"data: {json.dumps({'type': 'PDP_PROGRESS', 'data': product})}\n\n"
                    except Exception as e:
                        yield f"data: {json.dumps({'type': 'ERROR', 'msg': str(e)})}\n\n"
                        time.sleep(5)
                        return

                if page >= data["pager"]["total_pages"]:
                    break
                page += 1

            yield f"data: {json.dumps({'type': 'DONE'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'ERROR', 'msg': str(e)})}\n\n"

    return Response(generate(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
