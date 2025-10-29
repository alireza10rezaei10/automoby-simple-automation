main_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>اتوموبی اتومیشن</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@100..900&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Vazirmatn', sans-serif, 'Arial';
            font-weight: 100;
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
        <a href="/photoshop">
            <div class="card">فتوشاپ</div>
        </a>
        <a href="/emami-ghafari-sync">
            <div class="card">به‌روزرسانی موجودی/قیمت امامی غفاری</div>
        </a>
    </div>
</body>
</html>
"""
