from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import config
from trade import Trade
from ledger import Ledger

app = Flask(__name__)
CORS(app)

sawmill_names = list(map(config.to_lower_case_only_letters, config.sawmill_names))
ledger = Ledger(None, len(sawmill_names))
sawmills = [Trade(name, ledger.domain_name, ledger) for name in sawmill_names]
ledger.sawmills = sawmills
history = []

sawmills_by_name = dict(zip(sawmill_names, sawmills))


@app.route('/', methods=['GET'])  # Decorator
def iroha_admin():
    return send_from_directory('templates', 'iroha_admin.html')


@app.route('/iroha_understanding', methods=['GET'])  # Decorator
def iroha_understanding():
    return send_from_directory('templates', 'iroha_understanding.html')


@app.route('/iroha_accounts', methods=['GET'])  # Decorator
def iroha_accounts():
    return send_from_directory('templates', 'iroha_accounts.html')


@app.route('/iroha_send', methods=['GET'])  # Decorator
def iroha_send():
    return send_from_directory('templates', 'iroha_send.html')


@app.route('/account_info', methods=['POST'])
def account_info():
    account_name = request.get_json()
    print("account_name= ", account_name)
    if account_name['user'] == "":
        response = {
            'message': "No account selected"
        }
        return jsonify(response), 400
    sawmill = sawmills_by_name.get(account_name['user'])
    print("sawmill= ", sawmill)
    if sawmill is None:
        response = {
            'message': "Account not found"
        }
        return jsonify(response), 400
    result = {account_name['user']: sawmill.get_woods_balance()}
    print("result", result)
    response = {
        'message2': "Account: " + account_name['user'],
        'message': result
    }
    return jsonify(response), 201


@app.route('/users', methods=['POST'])
def post_account_info():
    print("sawmill_names= ", sawmill_names)
    response = {
        'data': sawmill_names
    }
    return jsonify(response), 200


@app.route('/admin_details', methods=['GET'])
def admin_details():
    details = ledger.get_admin_details()
    print("details= ", details)
    response = {
            'message': details,
            'message2': 'Details loaded.',
            'data': details
        }
    return jsonify(response), 200


@app.route('/send_assets', methods=['POST'])
def send_assets():
    assent = request.get_json()
    print('assent = ', assent)
    accountFrom = sawmills_by_name.get(assent['accountsFrom'])
    print("accountFrom = ", accountFrom)
    if accountFrom is None:
        response = {'message': "Account is not found."}
        return jsonify(response), 400
    accountTo = sawmills_by_name.get(assent['accountsTo'])
    print("accountTo = ", accountTo)
    if accountFrom is None:
        response = {'message': "Account is not found."}
        return jsonify(response), 400
    print("accountFrom.full_name = ", accountFrom.full_name)
    print("accountTo.full_name = ", accountTo.full_name)
    if accountTo.full_name == accountFrom.full_name:
        print("accountTo.full_name == accountFrom.full_name = ", accountTo.full_name == accountFrom.full_name)
        response = {'message': "Accounts are equals."}
        return jsonify(response), 400
    asset = assent['assets']
    print("asset = ", asset)
    if asset not in ledger.woods:
        response = {'message': "Wood is not exists."}
        return jsonify(response), 400
    amount = assent['amount']
    print("assent['amount'] = ", assent['amount'])
    if amount == '':
        response = {'message': "You must define amount."}
        return jsonify(response), 400
    if int(amount) > int(accountFrom.get_woods_balance()[asset]) or int(amount) <= 0:
        history.append(f'{accountFrom.account_name} -> {accountTo.account_name}: {amount} of {asset} !NOT VALID!;')
        response = {'message': "Oops...You have no resources..."}
        return jsonify(response), 400
    result = accountFrom.transfer_wood(accountTo.account_name, asset, int(amount))
    result = ','.join([str(r) for r in result])
    history.append(f'{accountFrom.account_name} -> {accountTo.account_name}: {amount} of {asset};')
    response = {
        'message2': "history: " + str(history),
        'message': result
    }
    return jsonify(response), 201


@app.route('/send_assets', methods=['GET'])
def get_send_assets():
    response = {
            'message2': 'Details loaded.',
            'assets_items': ledger.get_accounts_info(),
            'assets': ledger.woods,
            'accountsFrom': sawmill_names,
            'accountsTo': sawmill_names,
            'history': history
        }
    return jsonify(response), 200


if __name__ == '__main__':
    ledger.init_ledger()
    app.run('0.0.0.0')
