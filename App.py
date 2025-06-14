from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load and preprocess data
df = pd.read_csv('Inventory.csv')
df.fillna('', inplace=True)

# Structure: { 'Office A': [ {item info dict}, {item info dict}, ... ] }
data = {}
current_office = None

for _, row in df.iterrows():
    if row['Office'].strip():
        current_office = row['Office'].strip()
        data[current_office] = []

    if current_office:
        data[current_office].append(row.to_dict())

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/search")
def search():
    query = request.args.get("query", "").strip().lower()
    print(f"\n🔍 Search query: '{query}'")

    if not query:
        return render_template("index.html", offices=[], query=query)

    # Filter
    matched_offices = sorted(df[df["Office"].str.lower().str.contains(query, na=False)]["Office"].unique())
    print("✅ Matched offices:", matched_offices)

    # ✅ FIX: Use search.html instead of index.html
    return render_template("search.html", offices=matched_offices, query=query)

@app.route('/office/<office_name>')
def office_view(office_name):
    if office_name not in data:
        return render_template('office.html', office_name=office_name, hardware_types=[])

    items = data[office_name]
    hardware_types = sorted(set(item['Item'] for item in items if item['Item'].strip()))

    # Map items to icon class names (Font Awesome)
    icon_classes = {
        "computer": "fa-desktop",
        "printer": "fa-print",
        "scanner": "fa-barcode",
        "router": "fa-wifi",
        "keyboard": "fa-keyboard",
        "mouse": "fa-computer-mouse",
        "barcode scanner": "fa-barcode",
        "ups": "fa-plug",
    }

    return render_template(
        'office.html',
        office_name=office_name,
        hardware_types=hardware_types,
        icon_classes=icon_classes
    )

@app.route('/office/<office_name>/<item>')
def item_view(office_name, item):
    if office_name not in data:
        return render_template('item.html', office_name=office_name, item=item, hardware_list=[])

    hardware_list = [
        hw for hw in data[office_name] if hw['Item'].strip().lower() == item.lower()
    ]
    return render_template('item.html', office_name=office_name, item=item, hardware_list=hardware_list)

if __name__ == '__main__':
    app.run(debug=True)
