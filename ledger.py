import binascii
from random import randint
from iroha import Iroha, IrohaGrpc, IrohaCrypto
import os
import config

IROHA_HOST_ADDR = os.getenv('IROHA_HOST_ADDR', '10.0.0.2')
IROHA_PORT = os.getenv('IROHA_PORT', '50051')
ADMIN_ACCOUNT_ID = os.getenv('ADMIN_ACCOUNT_ID', 'admin@test')
ADMIN_PRIVATE_KEY = os.getenv('ADMIN_PRIVATE_KEY', 'f101537e319568c765b2cc89698325604991dca57b9716b58016b253506cab70')

class Ledger:
    def __init__(self):
        self.__private_key = IrohaCrypto.private_key()
        self.public_key = IrohaCrypto.derive_public_key(self.__private_key)
        self.admin_private_key = ADMIN_PRIVATE_KEY
        self.iroha = Iroha(ADMIN_ACCOUNT_ID)
        self.net = IrohaGrpc('{}:{}'.format(IROHA_HOST_ADDR, IROHA_PORT))
        
    def send_transaction_and_log_status(self, transaction):
        hex_hash = binascii.hexlify(IrohaCrypto.hash(transaction))
        print('Transaction hash = {}, creator = {}'.format(
            hex_hash, transaction.payload.reduced_payload.creator_account_id))
        self.net.send_tx(transaction)
        return list(self.net.tx_status_stream(transaction))    
        
    def get_admin_details(self):
        result_dict = {}
        query = self.iroha.query('GetAccountDetail', account_id=f'admin@test')
        IrohaCrypto.sign_query(query, self.admin_private_key)

        response = self.net.send_query(query)
        data = response.account_detail_response
        print(data)
        print('Account id = {}, details = {}'.format('admin@test', data.detail))
        result_dict['admin@test'] = data.detail
        return result_dict

    def get_user_details(self, username_input):
        result_dict = {}
        query = self.iroha.query('GetAccountDetail', account_id = username_input)
        IrohaCrypto.sign_query(query, self.admin_private_key)

        response = self.net.send_query(query)
        data = response.account_detail_response
        print(data)
        print('Account id = {}, details = {}'.format(username_input, data.detail))
        result_dict[username_input] = data.detail
        return result_dict

    def get_user_account_assets(self):
        result_dict = {}
        query = self.iroha.query('GetAccountAssets', account_id=f'userone@domain')
        IrohaCrypto.sign_query(query, self.admin_private_key)

        response = self.net.send_query(query)
        data = response.account_assets_response.account_assets
        for asset in data:
            print('Asset id = {}, balance = {}'.format(asset.asset_id, asset.balance))
            result_dict[asset.asset_id] = asset.balance
        return result_dict

    def get_admin_account_assets(self):
        result_dict = {}
        query = self.iroha.query('GetAccountAssets', account_id=f'admin@test')
        IrohaCrypto.sign_query(query, self.admin_private_key)

        response = self.net.send_query(query)
        data = response.account_assets_response.account_assets
        for asset in data:
            print('Asset id = {}, balance = {}'.format(asset.asset_id, asset.balance))
            result_dict[asset.asset_id] = asset.balance
        return result_dict

    def set_key_pair_to_userone(self, value_input):
        tx = self.iroha.transaction([self.iroha.command('SetAccountDetail',
        account_id='userone@domain', key='hash_1', value = value_input)])
        IrohaCrypto.sign_transaction(tx, self.admin_private_key)
        print(self.send_transaction_and_log_status(tx))
        
    def set_key_pair_to_user(self, account_input, key_input, value_input):
        print('Sets Key/Value pair...')
        tx = self.iroha.transaction([self.iroha.command('SetAccountDetail',
        account_id = account_input, key = key_input, value = value_input)])
        IrohaCrypto.sign_transaction(tx, self.admin_private_key)
        print(self.send_transaction_and_log_status(tx))
        
    def create_account(self, username_input, domain_input):
        print('Create Account...')
        tx = self.iroha.transaction([
            self.iroha.command('CreateAccount', account_name = username_input, domain_id = domain_input,
                               public_key=self.public_key)
        ])
        IrohaCrypto.sign_transaction(tx, self.admin_private_key)
        print(self.send_transaction_and_log_status(tx))
        
        tx = iroha.transaction([self.iroha.command('GrantPermission', account_id='admin@test', permission=can_set_my_account_detail)], creator_account=username_input+'@'+domain_input')
        IrohaCrypto.sign_transaction(tx, self.admin_private_key)
        print(self.send_transaction_and_log_status(tx))
