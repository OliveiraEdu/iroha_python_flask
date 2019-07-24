from iroha import Iroha, IrohaCrypto


class Trade:
    def __init__(self, account_name, domain, ledger):
        self.account_name = account_name
        self.domain = domain
        self.full_name = f"{self.account_name}@{self.domain}"
        self.__private_key = IrohaCrypto.private_key()
        self.public_key = IrohaCrypto.derive_public_key(self.__private_key)
        self.iroha = Iroha(self.full_name)
        self.ledger = ledger

    def get_woods_balance(self):
        query = self.iroha.query('GetAccountAssets', account_id=self.full_name)
        IrohaCrypto.sign_query(query, self.__private_key)

        response = self.ledger.net.send_query(query)
        data = response.account_assets_response.account_assets
        return {asset.asset_id.split('#')[0]: asset.balance for asset in data}

    def transfer_wood(self, name_to, wood, amount):
        reciever = f"{name_to}@{self.domain}"
        tx = self.iroha.transaction(
            [
                self.ledger.iroha.command(
                    "TransferAsset",
                    src_account_id=self.full_name,
                    dest_account_id=reciever,
                    asset_id=f"{wood}#{self.domain}",
                    description="transfer",
                    amount=str(amount),
                )
            ]
        )
        IrohaCrypto.sign_transaction(tx, self.__private_key)
        return self.ledger.send_transaction_and_log_status(tx)
