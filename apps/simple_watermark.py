# apps/simple_watermark.py
import cv2
import numpy as np
from io import BytesIO
from PIL import Image


# ---------------- Function ----------------
def apply_colored_box(
    image_data: bytes, x1: int, y1: int, x2: int, y2: int, color_hex: str
):
    # باز کردن تصویر با Pillow برای تشخیص فرمت
    img = Image.open(BytesIO(image_data))
    format_in = img.format  # PNG, JPEG, ...

    # تبدیل به numpy array برای OpenCV
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    # normalize coords
    h, w = img_cv.shape[:2]
    x1 = max(0, min(w - 1, int(x1)))
    x2 = max(0, min(w - 1, int(x2)))
    y1 = max(0, min(h - 1, int(y1)))
    y2 = max(0, min(h - 1, int(y2)))

    # hex → BGR
    color_hex = color_hex.lstrip("#")
    if len(color_hex) != 6:
        color_hex = "ffffff"
    rgb = tuple(int(color_hex[i : i + 2], 16) for i in (0, 2, 4))
    bgr = (rgb[2], rgb[1], rgb[0])

    # رسم مستطیل پرشده
    cv2.rectangle(img_cv, (x1, y1), (x2, y2), bgr, -1)

    # تبدیل دوباره به PIL
    img_out = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))

    # ذخیره در buffer با فرمت اصلی و کیفیت حفظ شده
    buffer = BytesIO()
    save_kwargs = {}
    if format_in.upper() in ["JPEG", "JPG"]:
        save_kwargs["quality"] = 95
    img_out.save(buffer, format=format_in, **save_kwargs)
    buffer.seek(0)
    return buffer


# ---------------- HTML ----------------
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

#drop-zone { 
    width: 100%; max-width: 600px; min-height: 300px; 
    border: 2px dashed purple; border-radius: 10px; 
    margin: auto; display: flex; align-items: center; justify-content: center; 
    color: #666; cursor: pointer; background: #fff; text-align: center; 
    padding: 10px; position: relative; overflow: hidden; transition: 0.3s; 
}
#drop-zone.dragover { background: #f0e6ff; border-color: #800080; }
#drop-zone img { max-width: 100%; max-height: 500px; display: block; margin: auto; user-select: none; -webkit-user-drag: none; }

.remove-btn {
    position: absolute;
    top: 10px;
    right: 10px;
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
    z-index: 50;
}

.container { max-width: 900px; margin: auto; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 0 15px rgba(0,0,0,0.1); }
input[type=file] { display: none; }
#output { margin-top: 20px; display: none; }
#output img { max-width: 100%; border-radius: 6px; }

/* انتخاب رنگ */
#colorPicker { margin-top: 15px; width: 80px; height: 40px; border: none; cursor: pointer; }

/* باکس انتخاب */
.selection-box {
    position: absolute;
    border: 2px dashed purple;
    background: rgba(128,0,128,0.18);
    pointer-events: none;
    display: none;
    z-index: 40;
}
button { padding: 10px 20px; font-size: 16px; border-radius: 8px; border: none; background: purple; color: white; cursor: pointer; margin-top: 15px; }
button:hover { background: #800080; }

/* بلور و اسپینر */
#drop-zone.loading img,
#drop-zone.loading .remove-btn,
#drop-zone.loading .selection-box {
    filter: blur(3px);
    pointer-events: none;
}

#spinner {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    border: 6px solid #f3f3f3;
    border-top: 6px solid purple;
    border-radius: 50%;
    width: 50px;
    height: 50px;
    animation: spin 1s linear infinite;
    display: none;
    z-index: 10;
}

@keyframes spin {
    0% { transform: translate(-50%, -50%) rotate(0deg); }
    100% { transform: translate(-50%, -50%) rotate(360deg); }
}
</style>
</head>
<body>
<h1>حذف واترمارک ساده</h1>
<div class="title-line"></div>
<div class="container">
    <div id="drop-zone">تصویر خود را پیست کنید، بکشید یا انتخاب کنید<div id="spinner"></div></div>
    <input type="file" id="imageInput" accept="image/*">
    <br>
    <label for="colorPicker">رنگ باکس:</label>
    <input type="color" id="colorPicker" value="#ffffff">
    <br>
    <button onclick="submitBox()">انجام</button>
    <div id="output"></div>
</div>

<script>
let selectedFile = null;
let startX = 0, startY = 0, endX = 0, endY = 0;
let isDrawing = false;
let boxCoords = null;
let activeImg = null;
let imgOffsetX = 0, imgOffsetY = 0;

const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('imageInput');
const outputDiv = document.getElementById('output');
const spinner = document.getElementById('spinner');

const selectionBox = document.createElement('div');
selectionBox.classList.add('selection-box');
dropZone.appendChild(selectionBox);

// کلیک روی drop zone باز کردن فایل
dropZone.addEventListener('click', (e) => {
    if(!selectedFile && e.target === dropZone) fileInput.click();
});

// انتخاب فایل از دیالوگ
fileInput.addEventListener('change', () => {
    if(fileInput.files.length) setSelectedFile(fileInput.files[0]);
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

function setSelectedFile(file){
    selectedFile = file;
    dropZone.innerHTML = '';
    const img = document.createElement('img');
    img.src = URL.createObjectURL(file);
    img.draggable = false;
    img.style.maxWidth = '100%';
    img.style.display = 'block';
    img.style.margin = 'auto';
    dropZone.appendChild(img);

    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.innerText = '×';
    removeBtn.classList.add('remove-btn');
    removeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        selectedFile = null;
        activeImg = null;
        isDrawing = false;
        boxCoords = null;
        selectionBox.style.display = 'none';
        dropZone.innerHTML = 'تصویر خود را پیست کنید، بکشید یا انتخاب کنید';
        dropZone.appendChild(spinner);
        dropZone.appendChild(selectionBox);
        outputDiv.style.display = 'none';
    });
    dropZone.appendChild(removeBtn);

    dropZone.appendChild(selectionBox);
    selectionBox.style.display = 'none';
    dropZone.appendChild(spinner);
    outputDiv.style.display = 'none';

    img.onload = () => { activeImg = img; enableBoxDraw(img); };
}

function enableBoxDraw(imgElem){
    imgElem.addEventListener('mousedown', (e) => {
        e.preventDefault(); e.stopPropagation();
        isDrawing = true;
        const imgRect = imgElem.getBoundingClientRect();
        const dropRect = dropZone.getBoundingClientRect();
        imgOffsetX = imgRect.left - dropRect.left;
        imgOffsetY = imgRect.top - dropRect.top;
        startX = e.clientX - imgRect.left;
        startY = e.clientY - imgRect.top;

        selectionBox.style.left = (imgOffsetX + startX) + "px";
        selectionBox.style.top = (imgOffsetY + startY) + "px";
        selectionBox.style.width = "0px";
        selectionBox.style.height = "0px";
        selectionBox.style.display = "block";
    });

    imgElem.addEventListener('mousemove', (e) => {
        if(!isDrawing) return;
        const imgRect = imgElem.getBoundingClientRect();
        endX = e.clientX - imgRect.left;
        endY = e.clientY - imgRect.top;
        const minX = Math.min(startX, endX);
        const minY = Math.min(startY, endY);
        selectionBox.style.left = (imgOffsetX + minX) + "px";
        selectionBox.style.top = (imgOffsetY + minY) + "px";
        selectionBox.style.width = Math.abs(endX - startX) + "px";
        selectionBox.style.height = Math.abs(endY - startY) + "px";
    });

    window.addEventListener('mouseup', (e) => {
        if(!isDrawing || !activeImg) return;
        isDrawing = false;
        const rect = activeImg.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        const dispX1 = Math.round(Math.min(startX, mouseX));
        const dispY1 = Math.round(Math.min(startY, mouseY));
        const dispX2 = Math.round(Math.max(startX, mouseX));
        const dispY2 = Math.round(Math.max(startY, mouseY));
        const scaleX = activeImg.naturalWidth / rect.width;
        const scaleY = activeImg.naturalHeight / rect.height;
        boxCoords = {
            x1: Math.round(dispX1 * scaleX),
            y1: Math.round(dispY1 * scaleY),
            x2: Math.round(dispX2 * scaleX),
            y2: Math.round(dispY2 * scaleY),
        };
    });
}

function submitBox(){
    if(!selectedFile || !boxCoords) return;
    const color = document.getElementById('colorPicker').value;
    const formData = new FormData();
    formData.append('image', selectedFile);
    formData.append('x1', boxCoords.x1);
    formData.append('y1', boxCoords.y1);
    formData.append('x2', boxCoords.x2);
    formData.append('y2', boxCoords.y2);
    formData.append('color', color);

    // فعال کردن بلور و اسپینر
    dropZone.classList.add('loading');
    spinner.style.display = 'block';

    fetch('/apply-box', {method:'POST', body: formData})
    .then(res => res.blob())
    .then(blob => {
        const url = URL.createObjectURL(blob);
        outputDiv.innerHTML = `<img src="${url}" alt="With Box">`;
        outputDiv.style.display = 'block';
    })
    .catch(err => console.error(err))
    .finally(() => {
        // برداشتن بلور و اسپینر
        dropZone.classList.remove('loading');
        spinner.style.display = 'none';
    });
}
</script>
</body>
</html>
"""
