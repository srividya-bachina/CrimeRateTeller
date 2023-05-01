from flask import Flask, render_template, session, request, redirect, url_for, send_file
from plot import YearVsCrime, StateVsCrime, CrimePercent, ScatterPlot,DynamicLine, Map, StackedArea, NearByJurisdictions
import os

app = Flask(__name__)
image_folder = os.path.join('static', 'images')

app.secret_key = "my_secret_key"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/line.json')
def line_json():
    fig = YearVsCrime()
    fig.save("line.json")
    with open("line.json") as file:
        return file.read() 

@app.route('/bar.json')
def bar_json():
    fig = StateVsCrime()
    fig.save("bar.json")
    with open("bar.json") as file:
        return file.read()

@app.route('/pie.json')
def pie_json():
    fig = CrimePercent()
    fig.save("pie.json")
    with open("pie.json") as file:
        return file.read() 

@app.route('/scatter.json')
def scatter_json():
    fig = ScatterPlot()
    fig.save("scatter.json")
    with open("scatter.json") as file:
        return file.read()   

@app.route('/analysis') 
def analysis():
    return render_template("analysis.html")

@app.route('/gallery') 
def gallery():
    image_files = os.listdir(image_folder)
    return render_template("gallery.html", image_files=image_files)

@app.route('/emergencycontacts') 
def emergencycontacts():
    file_path = os.path.join(app.root_path, 'Data', 'emergencycontacts.xlsx')
    return render_template('emergencycontacts.html', file_path=file_path)

@app.route('/go_to_analysis')
def go_to_analysis():
    return render_template('analysis.html')

@app.route('/submit_form', methods=['POST'])
def submit_form():
    years_min = request.form['years_min']
    years_min = int(years_min)
    years_max = request.form['years_max']
    years_max = int(years_max)
    state = request.form['state']
    city = request.form['city']
    # store the form values in a session
    session['years_min'] = years_min
    session['years_max'] = years_max
    session['state'] = state
    session['city'] = city
    
    return redirect(url_for('visualisation'))

@app.route('/visualisation')
def visualisation():
    state = session.get('state')
    city = session.get('city')
    fig = Map(state, city)
     # Generate HTML code for map
    map_html = fig._repr_html_()
    return render_template("visualisation.html", map_html=map_html)

@app.route('/dynamic_line.json')
def dynamic_line_json():
    years_min = session.get('years_min')
    years_max = session.get('years_max')
    state = session.get('state')
    city = session.get('city')
    fig = DynamicLine(years_min, years_max, state, city)
    fig.save("dynamic_line.json")
    with open("dynamic_line.json") as file:
        return file.read() 
    


@app.route('/area.json')
def area_json():
    years_min = session.get('years_min')
    years_max = session.get('years_max')
    state = session.get('state')
    city = session.get('city')
    fig = StackedArea(years_min, years_max, state, city)
    fig.save("area.json")
    with open("area.json") as file:
        return file.read() 

@app.route('/nearby.json')
def nearby_json():
    state = session.get('state')
    fig = NearByJurisdictions(state)
    fig.save("nearby.json")
    with open("nearby.json") as file:
        return file.read() 

if __name__ == '__main__':
    app.run(debug=True)