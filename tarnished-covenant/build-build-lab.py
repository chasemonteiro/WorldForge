from pathlib import Path
import re

path = Path(__file__).with_name("index.html")
html = path.read_text()

css_tag = '<link rel="stylesheet" href="./build-lab.css?v=13">'
js_tag = '<script src="./build-lab.js?v=17"></script>'

css_pattern = r'<link rel="stylesheet" href="\./build-lab\.css\?v=\d+">'
js_pattern = r'<script src="\./build-lab\.js\?v=\d+"></script>'

if re.search(css_pattern, html):
    html = re.sub(css_pattern, css_tag, html, count=1)
else:
    if "</head>" not in html:
        raise SystemExit("Build lab patch target </head> not found")
    html = html.replace("</head>", f"  {css_tag}\n</head>", 1)

if re.search(js_pattern, html):
    html = re.sub(js_pattern, js_tag, html, count=1)
else:
    if "</body>" not in html:
        raise SystemExit("Build lab patch target </body> not found")
    html = html.replace("</body>", f"  {js_tag}\n</body>", 1)

path.write_text(html)
print("Added persistent Tarnished build lab")
