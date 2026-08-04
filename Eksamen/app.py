from flask import Flask, jsonify, request, render_template, send_from_directory
import json
import os
import uuid
from werkzeug.utils import secure_filename
 
app = Flask(__name__)
GÆSTER_FIL = 'data/gæster.json'
 

#Gæstelisten
def læs_gæster():
    with open(GÆSTER_FIL, encoding='utf-8') as fil:
        return json.load(fil)
 
def gem_gæster(data):
    with open(GÆSTER_FIL, 'w', encoding='utf-8') as fil:
        json.dump(data, fil, ensure_ascii=False)
 
@app.route('/')
def index():
    return render_template('main.html')

@app.route('/gæster', methods=['GET'])
def hent_gæsteliste():
    return jsonify(læs_gæster())

@app.route('/gæster', methods=['POST'])
def opdater_gæst():
    data = request.json
    navn = data.get('navn')
    status = data.get('status')
 
    gæster = læs_gæster()
    for gæst in gæster:
        if gæst['navn'] == navn:
            gæst['status'] = status
 
    gem_gæster(gæster)
    return jsonify({'besked': navn + ', dit svar er gemt'})


#Billedegalleri
app.config['MAX_CONTENT_LENGTH'] = 500 * 2000 * 2000
UPLOAD_MAPPE = 'static/uploads'
TILLADT = ['image/jpeg', 'image/png', 'image/heic', 'video/mp4']
GALLERI = 'data/galleri.json'

os.makedirs(UPLOAD_MAPPE, exist_ok=True)
os.makedirs('data', exist_ok=True)

def læs_galleri():
    if not os.path.exists(GALLERI):
        return []
    with open(GALLERI, encoding='utf-8') as fil:
        return json.load(fil)

def gem_galleri(data):
    with open(GALLERI, 'w', encoding='utf-8') as fil:
        json.dump(data, fil, ensure_ascii=False)

@app.route('/galleri')
def vis_galleri():
    return render_template('galleri.html')

@app.route('/galleri/upload', methods=['POST'])
def galleri_upload():
    fil = request.files.get('fil')
 
    if not fil:
        return jsonify({'fejl': 'Ingen fil er valgt'}), 400
 
    if fil.content_type not in TILLADT:
        return jsonify({'fejl': 'Filtypen er ikke tilladt'}), 400
 
    fjern = os.path.splitext(secure_filename(fil.filename))[1]
    unik = str(uuid.uuid4()) + fjern
    fil.save(os.path.join(UPLOAD_MAPPE, unik))
 
    filtype = 'billede' if fil.content_type.startswith('image/') else 'video'
    galleri = læs_galleri()
    galleri.append({'filnavn': unik, 'type': filtype})
    gem_galleri(galleri)
 
    return jsonify({'besked': 'Filen er uploadet'})

@app.route('/galleri/filer', methods=['GET'])
def hent_galleri_liste():
    return jsonify(læs_galleri())
 
@app.route('/galleri/filer/<filnavn>')
def hent_galleri(filnavn):
    return send_from_directory(UPLOAD_MAPPE, filnavn)
 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)