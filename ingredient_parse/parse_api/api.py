import json

from flask import Flask, jsonify, request
from ingredient_parser import parse_ingredient

app = Flask(__name__);

@app.route('/parse', methods=['POST'])
def get_users():
    request_body = request.data
    request_lines = request_body.decode('utf-8').split('\n')
    results = []
    for raw_line in request_lines:
        line = raw_line.strip()
        if line != '':
            parsed_ingredient = parse_ingredient(line)
            notes_list = []
            if parsed_ingredient.preparation:
                notes_list.append(parsed_ingredient.preparation.text)
            if len(parsed_ingredient.amount) > 0:
                amount = parsed_ingredient.amount[0]
                if amount.APPROXIMATE:
                    notes_list.append('Amount is approximate')
                quantity = amount.quantity
                unit = str(amount.unit)
            else:
                quantity = ''
                unit = ''
            if parsed_ingredient.comment:
                notes_list.append(parsed_ingredient.comment.text)
            if parsed_ingredient.purpose:
                notes_list.append('Purpose: ' + parsed_ingredient.purpose.text)
            data = {
                'food': parsed_ingredient.name.text,
                'quantity': quantity,
                'unit_of_measurement': unit,
                'notes': '. '.join(notes_list)
            }
            results.append(data)
    # ParsedIngredient(
    #     name=IngredientText(text='pork shoulder', confidence=0.999193),
    #     size=None,
    #     amount=[IngredientAmount(quantity='3',
    #                             unit=<Unit('pound')>,
    #                             text='3 pounds',
    #                             confidence=0.999906,,
    #                             APPROXIMATE=False,
    #                             SINGULAR=False)],
    #     preparation=IngredientText(text='cut into 2 inch chunks', confidence=0.999193),
    #     comment=None,
    #     purpose=None,
    #     sentence='3 pounds pork shoulder, cut into 2-inch chunks'
    # )
    response = jsonify(results)
    response.headers.add('Access-Control-Allow-Origin', '*')
    print(results)
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)