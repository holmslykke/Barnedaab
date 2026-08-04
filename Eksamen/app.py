from flask import Flask, jsonify, request, render_template
import json
import os
import uuid
import requests
import vercel_blob
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20 MB pr. fil


# ---------- Fælles hjælpefunktioner til Vercel Blob ----------
# Vercel Functions har ikke en fast disk, så al data (gæsteliste + billeder)
# gemmes i stedet i Vercel Blob storage.

def hent_blob_json(sti, standard):
    """Henter en JSON-fil fra Vercel Blob. Returnerer 'standard' hvis filen ikke findes endnu."""
    try:
        info = vercel_blob.head(sti)
        respons = requests.get(info['url'], timeout=10)
        respons.raise_for_status()
        return respons.json()
    except Exception:
        return standard


def gem_blob_json(sti, data):
    """Gemmer/overskriver en JSON-fil i Vercel Blob."""
    vercel_blob.put(
        sti,
        json.dumps(data, ensure_ascii=False).encode('utf-8'),
        {
            "addRandomSuffix": "false",
            "allowOverwrite": "true",
            "access": "public",
            "contentType": "application/json",
        },
    )


@app.route('/')
def index():
    return render_template('main.html')


# ---------- Gæsteliste ----------

GÆSTER_STI = 'data/gæster.json'

# Bruges kun første gang siden besøges, før nogen har svaret endnu.
SEED_GÆSTER = [
    {"navn": "Asger", "status": "Mangler svar"},
    {"navn": "Mor", "status": "Mangler svar"},
    {"navn": "Far", "status": "Mangler svar"},
    {"navn": "Mormor", "status": "Mangler svar"},
    {"navn": "Morfar", "status": "Mangler svar"},
    {"navn": "Farmor", "status": "Mangler svar"},
    {"navn": "Farfar", "status": "Mangler svar"},
    {"navn": "Onkel Nicklas", "status": "Mangler svar"},
    {"navn": "Faster Maiken", "status": "Mangler svar"},
    {"navn": "Tanke Marie", "status": "Mangler svar"},
    {"navn": "Morbror Patrick", "status": "Mangler svar"},
    {"navn": "Onkel Lucas", "status": "Mangler svar"},
    {"navn": "Onkel Marcus", "status": "Mangler svar"},
    {"navn": "Tante Emma", "status": "Mangler svar"},
    {"navn": "Oldemor Karen", "status": "Mangler svar"},
    {"navn": "Oldefar Björn", "status": "Mangler svar"},
    {"navn": "Oldefar Henning", "status": "Mangler svar"},
    {"navn": "Oldemor Margit", "status": "Mangler svar"},
    {"navn": "Oldemor Ingeborg", "status": "Mangler svar"},
    {"navn": "Oldefar Hans", "status": "Mangler svar"},
    {"navn": "Bettina", "status": "Mangler svar"},
    {"navn": "AK", "status": "Mangler svar"},
    {"navn": "Jonas", "status": "Mangler svar"},
    {"navn": "Sofie", "status": "Mangler svar"},
    {"navn": "Mikkel", "status": "Mangler svar"},
    {"navn": "Vár", "status": "Mangler svar"},
    {"navn": "Kristian", "status": "Mangler svar"},
    {"navn": "Amalie", "status": "Mangler svar"},
    {"navn": "August", "status": "Mangler svar"},
    {"navn": "Sofie Hauge", "status": "Mangler svar"},
    {"navn": "Nils", "status": "Mangler svar"},
    {"navn": "Mathilde", "status": "Mangler svar"},
    {"navn": "Morten", "status": "Mangler svar"},
    {"navn": "Cathrine", "status": "Mangler svar"},
    {"navn": "Signe", "status": "Mangler svar"},
    {"navn": "William", "status": "Mangler svar"},
    {"navn": "Alberte", "status": "Mangler svar"},
    {"navn": "Kenneth", "status": "Mangler svar"},
    {"navn": "Sevda", "status": "Mangler svar"},
    {"navn": "Ditte", "status": "Mangler svar"},
    {"navn": "Peter", "status": "Mangler svar"},
    {"navn": "Jens Emil", "status": "Mangler svar"},
    {"navn": "Mette Marie", "status": "Mangler svar"},
    {"navn": "Andreas", "status": "Mangler svar"},
    {"navn": "Caroline Clausen", "status": "Mangler svar"},
]


def læs_gæster():
    return hent_blob_json(GÆSTER_STI, SEED_GÆSTER)


def gem_gæster(data):
    gem_blob_json(GÆSTER_STI, data)


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


# ---------- Billedgalleri ----------

GALLERI_STI = 'data/galleri.json'
TILLADT = ['image/jpeg', 'image/png', 'image/heic', 'video/mp4']


def læs_galleri():
    return hent_blob_json(GALLERI_STI, [])


def gem_galleri(data):
    gem_blob_json(GALLERI_STI, data)


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

    upload_resultat = vercel_blob.put(
        'uploads/' + unik,
        fil.read(),
        {"addRandomSuffix": "false", "access": "public"},
    )

    filtype = 'billede' if fil.content_type.startswith('image/') else 'video'
    galleri = læs_galleri()
    galleri.append({'url': upload_resultat['url'], 'type': filtype})
    gem_galleri(galleri)

    return jsonify({'besked': 'Filen er uploadet'})


@app.route('/galleri/filer', methods=['GET'])
def hent_galleri_liste():
    return jsonify(læs_galleri())


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
