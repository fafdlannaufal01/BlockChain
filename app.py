from flask import Flask, render_template, request
import hashlib
import time

app = Flask(__name__)


class Block:
    def __init__(self, index, previous_hash, transactions, timestamp=None, nonce=0):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.timestamp = timestamp or time.time()
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.index}{self.previous_hash}{self.transactions}{self.timestamp}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty):
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()


class Blockchain:
    def __init__(self, difficulty=4):
        self.chain = [self.create_genesis_block()]
        self.difficulty = difficulty
        self.pending_transactions = []
        self.mining_reward = 50

    def create_genesis_block(self):
        return Block(0, "0", ["Genesis Block"])

    def get_latest_block(self):
        return self.chain[-1]

    def add_transaction(self, sender, receiver, amount):
        self.pending_transactions.append({
            "from": sender,
            "to": receiver,
            "amount": amount
        })

    def mine_pending_transactions(self, miner_address):
        if not self.pending_transactions:
            return "Tidak ada transaksi untuk ditambang."

        new_block = Block(
            index=len(self.chain),
            previous_hash=self.get_latest_block().hash,
            transactions=self.pending_transactions
        )
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)

        # reward transaction goes into the next block, same as the original code
        self.pending_transactions = [{
            "from": "Blockchain System",
            "to": miner_address,
            "amount": self.mining_reward
        }]
        return (f"Block {new_block.index} mined! Hash: {new_block.hash} | "
                f"Miner '{miner_address}' menerima reward {self.mining_reward} coin")

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.calculate_hash():
                return f"Hash tidak valid pada block {current.index}"
            if current.previous_hash != previous.hash:
                return f"Previous hash tidak cocok pada block {current.index}"

        return "Blockchain valid"


my_coin = Blockchain(difficulty=4)


@app.route("/")
def index():
    return render_template("index.html", chain=my_coin.chain)


@app.route("/add_transaction", methods=["POST"])
def add_transaction():
    my_coin.add_transaction(
        request.form["sender"],
        request.form["receiver"],
        float(request.form["amount"])
    )
    return render_template("index.html", chain=my_coin.chain,
                           message="Transaction added. Waiting to be mined.")


@app.route("/mine", methods=["POST"])
def mine():
    message = my_coin.mine_pending_transactions(request.form["miner_address"])
    return render_template("index.html", chain=my_coin.chain, message=message)


@app.route("/validate", methods=["POST"])
def validate():
    return render_template("index.html", chain=my_coin.chain,
                           message=my_coin.is_chain_valid())


if __name__ == "__main__":
    app.run(debug=True)
