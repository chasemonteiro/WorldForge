from pathlib import Path


path = Path(__file__).with_name("index.html")
html = path.read_text()

css_tag = '<link rel="stylesheet" href="./build-lab.css?v=2">'
js_tag = '<script src="./build-lab.js?v=2"></script>'

if css_tag not in html:
    if "</head>" not in html:
        raise SystemExit("Build lab patch target </head> not found")
    html = html.replace("</head>", f"  {css_tag}\n</head>", 1)

if js_tag not in html:
    if "</body>" not in html:
        raise SystemExit("Build lab patch target </body> not found")
    html = html.replace("</body>", f"  {js_tag}\n</body>", 1)

path.write_text(html)
print("Added persistent Tarnished build lab")
