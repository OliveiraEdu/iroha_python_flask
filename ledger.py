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
    def __init__(self, sawmills, l):
        self.domain_name = "trade"
        self.admin_private_key = ADMIN_PRIVATE_KEY
        self.iroha = Iroha(ADMIN_ACCOUNT_ID)
        self.net = IrohaGrpc('{}:{}'.format(IROHA_HOST_ADDR, IROHA_PORT))
        self.sawmills = sawmills

        self.woods = list(map(config.to_lower_case_only_letters, config.woods))  # uses as assets
        self.commands = [
            self.iroha.command('CreateDomain', domain_id=self.domain_name, default_role='user'),
            *[self.iroha.command('CreateAsset', asset_name=wood,
                                 domain_id=self.domain_name, precision=0)
              for wood in self.woods]
        ]
        tx = IrohaCrypto.sign_transaction(
            self.iroha.transaction(self.commands), self.admin_private_key)
        print(self.send_transaction_and_log_status(tx))
        self.get_admin_details()
        tx = self.iroha.transaction(
            [self.iroha.command('AddAssetQuantity', asset_id=f'{wood}#{self.domain_name}',
                                amount=str(10000//l))
             for wood in self.woods]
        )
        IrohaCrypto.sign_transaction(tx, self.admin_private_key)
        print(self.send_transaction_and_log_status(tx))
        self.get_admin_details()

    def send_transaction_and_log_status(self, transaction):
        hex_hash = binascii.hexlify(IrohaCrypto.hash(transaction))
        print('Transaction hash = {}, creator = {}'.format(
            hex_hash, transaction.payload.reduced_payload.creator_account_id))
        self.net.send_tx(transaction)
        return list(self.net.tx_status_stream(transaction))

    def get_admin_details(self):
        print('admin details...')
        result_dict = {}
        query = self.iroha.query('GetAccountAssets', account_id=f'admin@test')
        IrohaCrypto.sign_query(query, self.admin_private_key)

        response = self.net.send_query(query)
        data = response.account_assets_response.account_assets
        for asset in data:
            print('Asset id = {}, balance = {}'.format(
                asset.asset_id, asset.balance))
            result_dict[asset.asset_id] = asset.balance
        return result_dict

    def init_ledger(self):
        print('init ledger...')
        tx = self.iroha.transaction([
            self.iroha.command('CreateAccount', account_name=sawmill.account_name, domain_id=sawmill.domain,
                               public_key=sawmill.public_key)
            for sawmill in self.sawmills
        ])
        IrohaCrypto.sign_transaction(tx, self.admin_private_key)
        print(self.send_transaction_and_log_status(tx))

        print("=" * 20)
        tx_commands = []
        for i in self.sawmills:
            for j in self.woods:
                tx_commands.append(self.iroha.command('TransferAsset', src_account_id='admin@test',
                                                      dest_account_id=f'{i.account_name}@{self.domain_name}',
                                                      asset_id=f'{j}#{self.domain_name}',
                                                      amount=str(randint(1, 100))))
        tx = self.iroha.transaction(tx_commands)
        IrohaCrypto.sign_transaction(tx, self.admin_private_key)
        print(self.send_transaction_and_log_status(tx))
        self.get_admin_details()
        print(self.get_accounts_info())
        print("=" * 20)

    def get_accounts_info(self):
        result_dict = {}
        for i in self.sawmills:
            result_dict[i.account_name] = i.get_woods_balance()
        return result_dict
