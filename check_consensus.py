from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

# Initialize provider
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8541'))

# Inject the Proof-of-Authority middleware for Web3.py v6+
w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

latest_block = w3.eth.block_number

print(f"🔍 Analyzing the last 15 blocks (Current block: {latest_block})")
print("-" * 50)
print(f"{'Block':<10} | {'Tx Count':<10} | {'Proposer (Miner)'}")
print("-" * 50)

# Fetching the last 15 blocks to observe the Round-Robin pattern
for i in range(max(0, latest_block - 15), latest_block + 1):
    block = w3.eth.get_block(i)
    miner = block.miner
    tx_count = len(block.transactions)
    print(f"#{i:<9} | {tx_count:<10} | {miner}")