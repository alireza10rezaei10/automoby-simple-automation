# app.py
import cv2
import numpy as np
from io import BytesIO
from PIL import Image


# ---------------- Crop Function ----------------
def place_subject_center_white_bg_full(image_data: bytes):
    nparr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    gray_blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, mask = cv2.threshold(gray_blur, 245, 255, cv2.THRESH_BINARY_INV)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask_clean = np.zeros_like(mask)
    for c in contours:
        if cv2.contourArea(c) > 500:
            cv2.drawContours(mask_clean, [c], -1, 255, -1)

    ys, xs = np.where(mask_clean == 255)
    size = 512
    if len(xs) == 0 or len(ys) == 0:
        img_final = cv2.resize(img_rgb, (size, size), interpolation=cv2.INTER_LANCZOS4)
    else:
        x0, x1 = xs.min(), xs.max()
        y0, y1 = ys.min(), ys.max()
        cropped = img_rgb[y0 : y1 + 1, x0 : x1 + 1]

        img_final = np.ones((size, size, 3), dtype=np.uint8) * 255
        h, w = cropped.shape[:2]
        scale = min(size / h, size / w)
        new_h, new_w = int(h * scale), int(w * scale)
        resized = cv2.resize(cropped, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

        y_offset = (size - new_h) // 2
        x_offset = (size - new_w) // 2
        img_final[y_offset : y_offset + new_h, x_offset : x_offset + new_w] = resized

    img_pil = Image.fromarray(img_final)
    buffer = BytesIO()
    img_pil.save(buffer, format="JPEG", quality=100)
    buffer.seek(0)
    return buffer


# ---------------- Routes ----------------
html_ui = """
<!doctype html>
<html lang="fa">
<head>
<meta charset="UTF-8">
<title>اتوموبی اتومیشن</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@100..900&display=swap" rel="stylesheet">
<style>
body { font-family: 'Vazirmatn', Arial; direction: rtl; text-align: center; margin: 20px; background: #f5f5f5; }
h1 { color: purple; margin-bottom: 5px; }
.title-line { width: 50%; height: 4px; background: purple; border-radius: 20px; margin: 0 auto 20px auto; }

#drop-zone { width: 100%; max-width: 512px; height: 200px; border: 2px dashed purple; border-radius: 10px; margin: auto; display: flex; align-items: center; justify-content: center; color: #666; cursor: pointer; background: #fff; text-align: center; padding: 10px; position: relative; overflow: hidden; }
#drop-zone.dragover { background: #f0e6ff; border-color: #800080; }
#drop-zone img { max-height: 100%; max-width: 100%; border-radius: 6px; display: block; margin: auto; }
.remove-btn {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: rgba(255,0,0,0.8);
    color: white;
    border: none;
    border-radius: 50%;
    width: 36px;
    height: 36px;
    cursor: pointer;
    font-weight: bold;
    font-size: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
}

button { padding: 10px 0; font-size: 18px; border-radius: 8px; border: none; background: purple; color: white; cursor: pointer; margin-top: 15px; display: block; margin-left: auto; margin-right: auto; width: 40%; }
button:hover { background: #800080; }

#output { margin-top: 20px; max-width: 512px; display: none; border: 1px solid #ccc; padding: 10px; background: white; }
#output img { display: block; margin: auto; border-radius: 6px; }

.container { max-width: 800px; margin: auto; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 0 15px rgba(0,0,0,0.1); }

input[type=file] { display: none; }
</style>
</head>
<body>
<h1>کراپ هوشمند تصویر</h1>
<div class="title-line"></div>
<div class="container">
    <label id="drop-zone">تصویر خود را پیست کنید، بکشید یا انتخاب کنید</label>
    <input type="file" id="imageInput" accept="image/*">
    <button onclick="cropImage()">کراپ</button>
    <div id="output"></div>
</div>

<script>
let selectedFile = null;

const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('imageInput');
const outputDiv = document.getElementById('output');

// کلیک روی drop zone باز کردن فایل
dropZone.addEventListener('click', () => { if(!selectedFile) fileInput.click(); });

// انتخاب فایل از دیالوگ
fileInput.addEventListener('change', () => {
    if(fileInput.files.length){
        setSelectedFile(fileInput.files[0]);
    }
});

// Drag & Drop
dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('dragover'); });
dropZone.addEventListener('dragleave', e => { e.preventDefault(); dropZone.classList.remove('dragover'); });
dropZone.addEventListener('drop', e => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if(e.dataTransfer.files.length) {
        setSelectedFile(e.dataTransfer.files[0]);
    }
});

// Paste
window.addEventListener('paste', e => {
    const items = e.clipboardData.items;
    for(let i=0;i<items.length;i++){
        if(items[i].type.indexOf('image') !== -1){
            setSelectedFile(items[i].getAsFile());
        }
    }
});

// تابع برای ست کردن فایل انتخاب شده و پیش‌نمایش + دکمه حذف
function setSelectedFile(file){
    selectedFile = file;
    dropZone.innerHTML = '';
    const img = document.createElement('img');
    img.src = URL.createObjectURL(file);
    dropZone.appendChild(img);

    const removeBtn = document.createElement('button');
    removeBtn.innerText = '×';
    removeBtn.classList.add('remove-btn');
    removeBtn.onclick = (e) => {
        e.stopPropagation(); // جلوگیری از باز شدن فایل منیجر
        selectedFile = null;
        dropZone.innerHTML = 'تصویر خود را پیست کنید یا بکشید';
        outputDiv.style.display = 'none';
    };
    dropZone.appendChild(removeBtn);

    outputDiv.style.display = 'none';
}

function cropImage() {
    if(!selectedFile) return alert('لطفا ابتدا یک تصویر انتخاب یا کشیده شود!');
    const formData = new FormData();
    formData.append('image', selectedFile);

    fetch('/crop', {method:'POST', body: formData})
    .then(res => res.blob())
    .then(blob => {
        const url = URL.createObjectURL(blob);
        outputDiv.innerHTML = `<img src="${url}" alt="Cropped" width="512" height="512">`;
        outputDiv.style.display = 'inline-block';
    })
    .catch(err => alert('خطا در پردازش تصویر!'));
}
</script>
</body>
</html>
"""
