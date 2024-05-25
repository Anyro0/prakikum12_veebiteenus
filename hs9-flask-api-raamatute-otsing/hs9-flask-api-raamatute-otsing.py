from flask import Flask, send_file, request, jsonify
import os
import requests
from azure.storage.blob import BlobServiceClient
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/raamatud/*": {"origins": "*"}, r"/raamatu_otsing/*": {"origins": "*"}})

raamatute_kaust = "./raamatud"

@app.route('/raamatu_otsing/<int:raamatu_id>', methods=['POST'])
def raamatust_sone_otsimine(raamatu_id):
    input_data = request.json
    sone = input_data['sone']
    summa = 0
    if not raamatu_id.isnumeric():
        return jsonify({}), 400
    if raamatu_id in blob_raamatute_nimekiri():
        for line in blob_alla_laadimine(raamatu_id).split('\n'):
            ajutine = line.lower().split().count(sone)
            summa += ajutine
        tulemus = {"raamatu_id": raamatu_id, "sone": sone, "leitud": summa}
        return jsonify(tulemus), 200
    else:
        return jsonify({}), 404

@app.route('/raamatu_otsing/', methods = ['POST'])
def koigist_raamatutest_sone_otsimine():
    try:

        input_data = request.json
        sone = input_data['sone']
    except:
        return jsonify({}), 404

    tulemused = []

    for raamatu_id in blob_raamatute_nimekiri():
        summa = 0
        for line in blob_alla_laadimine(raamatu_id).split('\n'):
            ajutine = line.lower().split().count(sone)
            summa += ajutine
        if summa > 0:
            tulemused.append({"raamatu_id": raamatu_id, "leitud": summa})
    tulemus = {"sone": sone, "tulemused": tulemused}
    return jsonify(tulemus), 200

def blob_konteineri_loomine(konteineri_nimi):
    blob_service_client = BlobServiceClient.from_connection_string(os.getenv('AZURE_BLOB_CONNECTION_STRING'))
    container_client = blob_service_client.get_container_client(container=konteineri_nimi)
    if not container_client.exists():
        try:
            blob_service_client.create_container(konteineri_nimi)
            print(f"Container '{konteineri_nimi}' created successfully.")
        except Exception as e:
            print(f"Error creating container '{konteineri_nimi}': {str(e)}")

def blob_raamatute_nimekiri():
    blob_service_client = BlobServiceClient.from_connection_string(os.getenv('AZURE_BLOB_CONNECTION_STRING'))
    raamatute_nimekiri = []
    container_client = blob_service_client.get_container_client(container=blob_container_name)
    for blob in container_client.list_blobs():
        raamatute_nimekiri.append(blob.name)
    return raamatute_nimekiri

def blob_alla_laadimine(faili_nimi):
    blob_service_client = BlobServiceClient.from_connection_string(os.getenv('AZURE_BLOB_CONNECTION_STRING'))
    try:
        blob_client = blob_service_client.get_blob_client(container=blob_container_name, blob=faili_nimi)
        blob_sisu = blob_client.download_blob().content_as_text()
        return blob_sisu
    except:
        return jsonify({}), 404



if __name__ == '__main__':
    blob_container_name = "prak8"
    blob_konteineri_loomine(blob_container_name)
    app.run(debug=True)
