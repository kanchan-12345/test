from flask import Flask, request, jsonify

app = Flask(__name__)

# Simulating the databases as dictionaries
meterDB = {}
fogDB = {}

# Function to add a new smart meter
@app.route('/addMeter', methods=['POST'])
def add_meter():
    addM = request.json
    newIDM = addM.get('newIDM')
    newHPBM = addM.get('newHPBM')
    DI = addM.get('DI')
    
    # Simulating the asset registry operation
    meterDB[newIDM] = {'HPBM': newHPBM, 'DI': DI}
    
    return jsonify({'message': 'Smart meter added successfully', 'data': meterDB[newIDM]}), 201


# Function to add a new fog node
@app.route('/addFogNode', methods=['POST'])
def add_fog_node():
    addF = request.json
    newIDF = addF.get('newIDF')
    newHPBF = addF.get('newHPBF')
    
    # Simulating the asset registry operation
    fogDB[newIDF] = {'HPBF': newHPBF}
    
    return jsonify({'message': 'Fog node added successfully', 'data': fogDB[newIDF]}), 201


# Function to remove a smart meter
@app.route('/removeMeter', methods=['POST'])
def remove_meter():
    removeM = request.json
    IDM = removeM.get('IDM')
    
    # Simulating the removal from the asset registry
    if IDM in meterDB:
        del meterDB[IDM]
        return jsonify({'message': 'Smart meter removed successfully'}), 200
    else:
        return jsonify({'message': 'Smart meter not found'}), 404


# Function to remove a fog node
@app.route('/removeFogNode', methods=['POST'])
def remove_fog_node():
    removeF = request.json
    IDF = removeF.get('IDF')
    
    # Simulating the removal from the asset registry
    if IDF in fogDB:
        del fogDB[IDF]
        return jsonify({'message': 'Fog node removed successfully'}), 200
    else:
        return jsonify({'message': 'Fog node not found'}), 404


# Function to update fog node public key
@app.route('/updateFogNode', methods=['POST'])
def update_fog_node():
    updateF = request.json
    IDF = updateF.get('IDF')
    newHPBF = updateF.get('newHPBF')
    
    # Simulating the update in the asset registry
    if IDF in fogDB:
        fogDB[IDF]['HPBF'] = newHPBF
        return jsonify({'message': 'Fog node public key updated successfully', 'data': fogDB[IDF]}), 200
    else:
        return jsonify({'message': 'Fog node not found'}), 404


# Function to update smart meter public key
@app.route('/updateMeter', methods=['POST'])
def update_meter():
    updateM = request.json
    IDM = updateM.get('IDM')
    newHPBM = updateM.get('newHPBM')
    
    # Simulating the update in the asset registry
    if IDM in meterDB:
        meterDB[IDM]['HPBM'] = newHPBM
        return jsonify({'message': 'Smart meter public key updated successfully', 'data': meterDB[IDM]}), 200
    else:
        return jsonify({'message': 'Smart meter not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)
