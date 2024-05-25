from flask import Flask, send_file, request, jsonify
import os
import requests
from azure.storage.blob import BlobServiceClient
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/raamatud/*": {"origins": "*"}, r"/raamatu_otsing/*": {"origins": "*"}})

raamatute_kaust = "./raamatud"

@app.route('/raamatud/', methods = ['GET'])
def raamatu_nimekiri():
    raamatud = blob_raamatute_nimekiri()
    tulemus = {"raamatud": raamatud}
    return jsonify(tulemus), 200

@app.route('/raamatud/<book_id>', methods=['GET'])
def raamatu_allatombamine(book_id):
    raamatu_sisu = blob_alla_laadimine(book_id)
    return raamatu_sisu, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/raamatud/<book_id>', methods=['DELETE'])
def raamatu_kustutamine(book_id):
    return blob_kustutamine(book_id)

@app.route('/raamatud/', methods = ['POST'])
def raamatu_lisamine():
    input_data = request.json
    book_id = input_data['raamatu_id']
    url = f'https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt'
    response = requests.get(url)
    sisu = response.text
    blob_ules_laadimine_sisu(book_id, sisu)
    tulemus = {"tulemus": "Raamatu loomine õnnestus", "raamatu_id": book_id}
    return jsonify(tulemus), 201

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

def blob_ules_laadimine_sisu(faili_nimi, sisu):
    blob_service_client = BlobServiceClient.from_connection_string(os.getenv('AZURE_BLOB_CONNECTION_STRING'))
    blob_client = blob_service_client.get_blob_client(container=blob_container_name, blob=faili_nimi)
    blob_client.upload_blob(sisu)

def blob_kustutamine(faili_nimi):
    blob_service_client = BlobServiceClient.from_connection_string(os.getenv('AZURE_BLOB_CONNECTION_STRING'))
    try:
        blob_client = blob_service_client.get_blob_client(container=blob_container_name, blob=faili_nimi)
        blob_client.delete_blob()
        return jsonify({}), 204
    except:
        return jsonify({}), 404

if __name__ == '__main__':
    blob_container_name = "prak8"
    blob_konteineri_loomine(blob_container_name)
    app.run(debug=True)
