import requests
import time
import json


# ---------------- Helper Functions ----------------
def safe_request(url, retries=3, wait=5):
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response
        except Exception:
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
        except Exception:
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
    except Exception:
        pass
    return {"title": title, "attributes": attributes, "url": pdp_url}


def generate(category_url):
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
                    time.sleep(0.5)
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


html = """
    <!doctype html>
    <html lang="fa">
    <head>
      <meta charset="UTF-8">
      <title>اتوموبی اتومیشن</title>
          <link rel="preconnect" href="https://fonts.googleapis.com">
          <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
          <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@100..900&display=swap" rel="stylesheet">
      <style>
        body { font-family: 'Vazirmatn', Arial; direction: rtl; text-align: right; margin: 20px; background: #f5f5f5; }
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
