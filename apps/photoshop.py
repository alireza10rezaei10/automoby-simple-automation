# apps/photoshop.py
import cv2
import numpy as np
from io import BytesIO
from PIL import Image


# ---------------- Crop Box Function ----------------
def crop_to_box(image_data: bytes, x1: int, y1: int, x2: int, y2: int):
    # Load image with OpenCV
    nparr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Invalid image data")

    # Normalize coords
    h, w = img.shape[:2]
    x1 = max(0, min(w - 1, int(x1)))
    x2 = max(0, min(w - 1, int(x2)))
    y1 = max(0, min(h - 1, int(y1)))
    y2 = max(0, min(h - 1, int(y2)))

    # Ensure x1 < x2 and y1 < y2
    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1

    # Crop the image
    cropped = img[y1 : y2 + 1, x1 : x2 + 1]

    # Resize to 512x512
    resized = cv2.resize(cropped, (512, 512), interpolation=cv2.INTER_LANCZOS4)

    # Convert to PIL and save as JPEG
    img_rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    buffer = BytesIO()
    img_pil.save(buffer, format="JPEG", quality=100)
    buffer.seek(0)
    return buffer


# ---------------- Box Function ----------------
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


# ---------------- Combined Function ----------------
def apply_combined(
    image_data: bytes, crop_coords=None, watermark_coords=None, color_hex="#ffffff"
):
    # Start with original image data
    current_data = image_data

    # Apply watermark if provided
    if watermark_coords:
        x1_w, y1_w, x2_w, y2_w = watermark_coords
        current_data = apply_colored_box(
            current_data, x1_w, y1_w, x2_w, y2_w, color_hex
        ).getvalue()

    # Apply crop if provided
    if crop_coords:
        x1_c, y1_c, x2_c, y2_c = crop_coords
        result_buffer = crop_to_box(current_data, x1_c, y1_c, x2_c, y2_c)
    else:
        # If no crop, save the current_data as JPEG
        img = Image.open(BytesIO(current_data))
        result_buffer = BytesIO()
        img.save(result_buffer, format="JPEG", quality=95)
        result_buffer.seek(0)

    return result_buffer


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
.crop-box {
    border-color: #4CAF50 !important;
    background: rgba(76, 175, 80, 0.2) !important;
}
.watermark-box {
    border-color: #f44336 !important;
    background: rgba(244, 67, 54, 0.2) !important;
}
button { padding: 10px 20px; font-size: 16px; border-radius: 8px; border: none; background: purple; color: white; cursor: pointer; margin: 5px; }
button:hover { background: #800080; }
.mode-btn { background: #6a0dad; margin: 10px 5px; }
#cropModeBtn.active { background: #4CAF50; }
#watermarkModeBtn.active { background: #f44336; }
#applyBtn { background: #28a745; width: 200px; font-size: 18px; }

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
<h1>ابزار ویرایش تصویر</h1>
<div class="title-line"></div>
<div class="container">
    <div id="drop-zone">تصویر خود را پیست کنید، بکشید یا انتخاب کنید<div id="spinner"></div></div>
    <input type="file" id="imageInput" accept="image/*">
    <br>
    <button id="cropModeBtn" class="mode-btn" onclick="toggleMode('crop')">انتخاب ناحیه کراپ</button>
    <button id="watermarkModeBtn" class="mode-btn" onclick="toggleMode('watermark')">انتخاب ناحیه واترمارک</button>
    <br>
    <label for="colorPicker" id="colorLabel">رنگ پر کردن واترمارک:</label>
    <input type="color" id="colorPicker" value="#ffffff">
    <br>
    <button id="applyBtn" onclick="applyAll()">انجام ویرایش</button>
    <div id="output"></div>
</div>

<script>
let selectedFile = null;
let startX = 0, startY = 0, endX = 0, endY = 0;
let isDrawing = false;
let boxCoords = { crop: null, watermark: null };
let currentMode = null;
let activeImg = null;
let imgOffsetX = 0, imgOffsetY = 0;

const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('imageInput');
const outputDiv = document.getElementById('output');
const spinner = document.getElementById('spinner');
const cropModeBtn = document.getElementById('cropModeBtn');
const watermarkModeBtn = document.getElementById('watermarkModeBtn');
const colorPicker = document.getElementById('colorPicker');
const colorLabel = document.getElementById('colorLabel');
const applyBtn = document.getElementById('applyBtn');

let cropBox, watermarkBox;

// کلیک روی drop zone باز کردن فایل
dropZone.addEventListener('click', (e) => {
    if(!selectedFile && e.target === dropZone && !isDrawing) fileInput.click();
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

function toggleMode(mode) {
    currentMode = mode;
    isDrawing = false;

    // Reset buttons
    cropModeBtn.classList.remove('active');
    watermarkModeBtn.classList.remove('active');

    if (mode === 'crop') {
        cropModeBtn.classList.add('active');
        if (activeImg) enableBoxDraw(activeImg, 'crop');
    } else if (mode === 'watermark') {
        watermarkModeBtn.classList.add('active');
        if (activeImg) enableBoxDraw(activeImg, 'watermark');
    }
}

function setSelectedFile(file){
    selectedFile = file;
    boxCoords = { crop: null, watermark: null };
    currentMode = null;
    isDrawing = false;
    if (cropBox) cropBox.style.display = 'none';
    if (watermarkBox) watermarkBox.style.display = 'none';
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
        boxCoords = { crop: null, watermark: null };
        currentMode = null;
        cropModeBtn.classList.remove('active');
        watermarkModeBtn.classList.remove('active');
        if (cropBox) cropBox.style.display = 'none';
        if (watermarkBox) watermarkBox.style.display = 'none';
        dropZone.innerHTML = 'تصویر خود را پیست کنید، بکشید یا انتخاب کنید';
        dropZone.appendChild(spinner);
        dropZone.appendChild(cropBox || createBoxes());
        dropZone.appendChild(watermarkBox || createBoxes());
        outputDiv.style.display = 'none';
    });
    dropZone.appendChild(removeBtn);

    // Create boxes if not exist
    createBoxes();
    dropZone.appendChild(cropBox);
    dropZone.appendChild(watermarkBox);
    dropZone.appendChild(spinner);
    outputDiv.style.display = 'none';

    img.onload = () => { 
        activeImg = img; 
        // Reset modes
        cropModeBtn.classList.remove('active');
        watermarkModeBtn.classList.remove('active');
        currentMode = null;
    };
}

function createBoxes() {
    if (!cropBox) {
        cropBox = document.createElement('div');
        cropBox.classList.add('selection-box', 'crop-box');
        cropBox.style.display = 'none';
    }
    if (!watermarkBox) {
        watermarkBox = document.createElement('div');
        watermarkBox.classList.add('selection-box', 'watermark-box');
        watermarkBox.style.display = 'none';
    }
}

function enableBoxDraw(imgElem, mode) {
    const selectionBox = mode === 'crop' ? cropBox : watermarkBox;
    const handleMouseDown = (e) => {
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
    };

    const handleMouseMove = (e) => {
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
    };

    const handleMouseUp = (e) => {
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
        const coords = {
            x1: Math.round(dispX1 * scaleX),
            y1: Math.round(dispY1 * scaleY),
            x2: Math.round(dispX2 * scaleX),
            y2: Math.round(dispY2 * scaleY),
        };
        boxCoords[mode] = coords;
        selectionBox.style.display = 'block'; // Keep visible
    };

    // Remove previous listeners if any
    if (imgElem._mousedownHandler) imgElem.removeEventListener('mousedown', imgElem._mousedownHandler);
    if (imgElem._mousemoveHandler) imgElem.removeEventListener('mousemove', imgElem._mousemoveHandler);
    if (imgElem._mouseupHandler) window.removeEventListener('mouseup', imgElem._mouseupHandler);

    // Add new listeners
    imgElem._mousedownHandler = handleMouseDown;
    imgElem._mousemoveHandler = handleMouseMove;
    imgElem._mouseupHandler = handleMouseUp;

    imgElem.addEventListener('mousedown', imgElem._mousedownHandler);
    imgElem.addEventListener('mousemove', imgElem._mousemoveHandler);
    window.addEventListener('mouseup', imgElem._mouseupHandler);
}

function applyAll(){
    if(!selectedFile) return alert('لطفا ابتدا یک تصویر انتخاب کنید!');
    if(!boxCoords.crop && !boxCoords.watermark) return alert('لطفا حداقل یک ناحیه (کراپ یا واترمارک) انتخاب کنید!');

    const formData = new FormData();
    formData.append('image', selectedFile);

    if (boxCoords.crop) {
        formData.append('x1_c', boxCoords.crop.x1);
        formData.append('y1_c', boxCoords.crop.y1);
        formData.append('x2_c', boxCoords.crop.x2);
        formData.append('y2_c', boxCoords.crop.y2);
    }

    if (boxCoords.watermark) {
        formData.append('x1_w', boxCoords.watermark.x1);
        formData.append('y1_w', boxCoords.watermark.y1);
        formData.append('x2_w', boxCoords.watermark.x2);
        formData.append('y2_w', boxCoords.watermark.y2);
        formData.append('color', colorPicker.value);
    }

    // فعال کردن بلور و اسپینر
    dropZone.classList.add('loading');
    spinner.style.display = 'block';

    fetch('/apply-all', {method:'POST', body: formData})
    .then(res => res.blob())
    .then(blob => {
        const url = URL.createObjectURL(blob);
        outputDiv.innerHTML = `<img src="${url}" alt="Edited">`;
        outputDiv.style.display = 'block';
        // Hide boxes after apply
        if (cropBox) cropBox.style.display = 'none';
        if (watermarkBox) watermarkBox.style.display = 'none';
    })
    .catch(err => alert('خطا در پردازش تصویر!'))
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
