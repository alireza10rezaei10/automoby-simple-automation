import json
import traceback
import time
import os
from typing import Generator


def generate() -> Generator[str, None, None]:
    """Server-Sent Events generator.

    Yields JSON messages encoded as SSE `data: ...\n\n` strings.
    Message types:
    - STATUS: {'type':'STATUS','msg':...}
    - ERROR: {'type':'ERROR','msg':...,'detail':...}
    - SHEET_URL: {'type':'SHEET_URL','url':...}
    - CSV_PATH: {'type':'CSV_PATH','path':...}
    - DONE: {'type':'DONE'}
    """

    def sse(msg_obj: dict) -> str:
        """Helper to format SSE data line"""
        return f"data: {json.dumps(msg_obj, ensure_ascii=False)}\n\n"

    # initial status
    yield sse({"type": "STATUS", "msg": "شروع عملیات..."})

    # lazy-import crawler so import-time issues are reported to the user
    try:
        from apps.emami_ghafari_quantity_syncer.services import crawler as crawler_mod
    except Exception:
        tb = traceback.format_exc()
        yield sse({"type": "ERROR", "msg": "خطا در ایمپورت سرویس کراولر", "detail": tb})
        return

    # construct crawler
    try:
        yield sse({"type": "STATUS", "msg": "در حال ساخت crawler..."})
        crawler = crawler_mod.Main()
    except Exception:
        tb = traceback.format_exc()
        yield sse({"type": "ERROR", "msg": "خطا در ساخت crawler", "detail": tb})
        return

    # fetch pages
    try:
        yield sse({"type": "STATUS", "msg": "شروع دریافت محصولات..."})
        start_ts = time.time()

        first_page = crawler._fetch_page_products(page=1)
        total_pages = int(first_page.get("total_pages") or 1)
        products = list(first_page.get("products") or [])

        yield sse(
            {
                "type": "STATUS",
                "msg": f"صفحه 1 از {total_pages} دریافت شد ({len(products)} محصول)",
            }
        )

        total_count = len(products)
        for page in range(2, total_pages + 1):
            try:
                page_resp = crawler._fetch_page_products(page=page)
                count = len(page_resp.get("products") or [])
                total_count += count
                products.extend(page_resp.get("products") or [])
                yield sse(
                    {
                        "type": "STATUS",
                        "msg": f"صفحه {page} از {total_pages} دریافت شد ({total_count} محصول)",
                    }
                )
                time.sleep(0.2)
            except Exception:
                tb = traceback.format_exc()
                yield sse(
                    {"type": "ERROR", "msg": f"خطا در دریافت صفحه {page}", "detail": tb}
                )
                return

        elapsed = round(time.time() - start_ts, 2)

        # build DataFrame
        try:
            import pandas as pd

            df = pd.DataFrame(products)
            rows = len(df)
        except Exception:
            df = None
            rows = 0

        yield sse(
            {"type": "STATUS", "msg": f"دریافت شد: {rows} ردیف در {elapsed} ثانیه"}
        )

    except Exception:
        tb = traceback.format_exc()
        yield sse({"type": "ERROR", "msg": "خطا در دریافت محصولات", "detail": tb})
        return

    # attempt to upload to Google Sheets (3 tries), fallback to CSV
    try:
        from apps.emami_ghafari_quantity_syncer.services.google_sheets import (
            service as gs_service_mod,
            credentials as gs_creds,
        )
    except Exception:
        tb = traceback.format_exc()
        yield sse(
            {"type": "ERROR", "msg": "خطا در ایمپورت سرویس Google Sheets", "detail": tb}
        )
        yield sse({"type": "DONE"})
        return

    MAX_RETRIES = 3
    WAIT_SECONDS = 5
    sheet_errors = []

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            yield sse(
                {
                    "type": "STATUS",
                    "msg": "درحال بروزرسانی گوگل شیت...",
                }
            )

            gs = gs_service_mod.GoogleSheetsService()
            # if df is None or empty, pass an empty DataFrame
            import pandas as pd

            upload_df = pd.DataFrame() if df is None else df
            gs.update_sheet(upload_df)

            sheet_url = getattr(gs_creds, "GOOGLE_SHEETS_TARGET_SHEET_URL", None)
            yield sse({"type": "SHEET_URL", "url": sheet_url})
            yield sse({"type": "DONE"})
            return

        except Exception:
            tb = traceback.format_exc()
            sheet_errors.append(tb)
            if attempt < MAX_RETRIES:
                yield sse(
                    {
                        "type": "STATUS",
                        "msg": f"خطا در تلاش {attempt}. {WAIT_SECONDS} ثانیه تا تلاش بعدی...",
                    }
                )
                time.sleep(WAIT_SECONDS)


main_html = """
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
    button { padding: 10px 20px; font-size: 16px; border-radius: 5px; border: none; background: purple; color: white; cursor: pointer; margin: 10px auto; display: block;}
    button:hover { background: #800080; }
    button:disabled { background: #999; }
    .progress-container { margin-bottom: 20px; }
    progress { width: 100%; height: 25px; border-radius: 5px; }
    #log { max-height: 400px; overflow-y: auto; margin-top: 15px; }
    .error { white-space: pre-wrap; font-family: 'Vazirmatn'; }
    .container { max-width: 1000px; margin: auto; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 0 15px rgba(0,0,0,0.1); }
    .message-box { padding: 15px; margin: 10px 0; border-radius: 8px; }
    .message-box.success { background: #f0fff4; border: 1px solid #c6f6d5; }
    .message-box.error { background: #fff5f5; border: 1px solid #fed7d7; color: #742a2a; }
    .message-box a { color: purple; text-decoration: none; }
    .message-box a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <h1>به‌روزرسانی موجودی/قیمت امامی غفاری</h1>
  <div class="title-line"></div>

  <div class="container">
    <div class="progress-container">
      <h3 id="progress-title">آماده به کار</h3>
      <progress id="progress-bar" value="0" max="1"></progress>
      <div id="progress-text"></div>
    </div>

    <button onclick="startSync()" id="start-btn">شروع همگام‌سازی</button>

    <div id="log"></div>
    <div id="final-output"></div>
  </div>

  <script>
    let evtSource = null;
    let totalPages = 1;

    function startSync() {
      if(evtSource) { evtSource.close(); }
      
      const btn = document.getElementById('start-btn');
      const progressBar = document.getElementById('progress-bar');
      const progressText = document.getElementById('progress-text');
      const progressTitle = document.getElementById('progress-title');
      const log = document.getElementById('log');
      const finalOutput = document.getElementById('final-output');
      
      btn.disabled = true;
      log.innerHTML = '';
      finalOutput.innerHTML = '';
      progressBar.value = 0;
      progressText.innerText = '';
      progressTitle.innerText = 'آماده به کار';

      evtSource = new EventSource('/emami-ghafari-sync-run');
      
      evtSource.onmessage = function(e) {
        const msg = JSON.parse(e.data);
        
        if(msg.type === 'STATUS') {
          progressTitle.innerText = msg.msg;
          
          // Update progress if message contains page info
          const match = msg.msg.match(/صفحه\s*(\d+)\s*از\s*(\d+)/);
          if(match) {
            const [_, current, total] = match;
            totalPages = parseInt(total);
            progressBar.max = totalPages;
            progressBar.value = parseInt(current);
            progressText.innerText = `${progressBar.value} از ${totalPages} صفحه`;
          } else if(msg.msg.includes('دریافت شد:')) {
            // Show final product count
            progressText.innerText = msg.msg;
          }
        }
        else if(msg.type === 'ERROR') {
          progressTitle.innerText = 'خطا رخ داد';
          btn.disabled = false;
          
          const errorBox = document.createElement('div');
          errorBox.className = 'message-box error';
          errorBox.innerHTML = `<strong>خطا: </strong>${msg.msg}${msg.detail ? '<br><br>' + msg.detail.replace(/\\n/g, '<br>') : ''}`;
          log.innerHTML = ''; // پاک کردن لاگ‌های قبلی
          log.appendChild(errorBox);
          
          if(evtSource) { evtSource.close(); }
        }
        else if(msg.type === 'SHEET_URL') {
          const successBox = document.createElement('div');
          successBox.className = 'message-box success';
          successBox.innerHTML = `<strong>عملیات موفق:</strong> <a href="${msg.url}" target="_blank">مشاهده در Google Sheets</a>`;
          log.innerHTML = '';
          log.appendChild(successBox);
        }
        else if(msg.type === 'CSV_PATH') {
          const successBox = document.createElement('div');
          successBox.className = 'message-box success';
          successBox.innerHTML = `<strong>فایل CSV ذخیره شد:</strong> <code>${msg.path}</code>`;
        }
        else if(msg.type === 'DONE') {
          progressTitle.innerText = 'عملیات به پایان رسید';
          btn.disabled = false;
          if(evtSource) { evtSource.close(); }
        }
      };
      
      evtSource.onerror = function() {
        progressTitle.innerText = 'خطا در ارتباط';
        btn.disabled = false;
        const errorBox = document.createElement('div');
        errorBox.className = 'message-box error';
        errorBox.innerHTML = '<strong>خطا:</strong> ارتباط با سرور قطع شد';
        log.innerHTML = '';
        log.appendChild(errorBox);
        if(evtSource) { evtSource.close(); }
      };
    }
  </script>
</body>
</html>
"""
