import asyncio
import time
from web3 import AsyncWeb3
from web3.providers import AsyncHTTPProvider
from eth_account import Account

# Initialize asynchronous Web3 provider targeting Node 1
w3 = AsyncWeb3(AsyncHTTPProvider('http://127.0.0.1:8541'))

async def main():
    if not await w3.is_connected():
        print("❌ Cannot connect to Node 1 RPC endpoint.")
        return

    # Configuration for the benchmark load
    TOTAL_TRANSACTIONS = 200  # Total number of transactions to blast
    BATCH_SIZE = 50           # Number of concurrent requests sent in a single wave

    # Load Node 1 private key safely
    with open('qbft_network/node1/data/key', 'r') as key_file:
        private_key = key_file.read().strip()

    sender_address = w3.to_checksum_address('0x117817b801e9bcc679eaf37c9f22b06605a484eb')
    receiver_address = w3.to_checksum_address('0x0000000000000000000000000000000000000000')

    print("📊 Preparing benchmark payload...")
    start_nonce = await w3.eth.get_transaction_count(sender_address)
    gas_price = await w3.eth.gas_price

    # 1. Pre-sign all transactions locally to remove CPU signing overhead from the execution loop
    signed_tx_pool = []
    for i in range(TOTAL_TRANSACTIONS):
        tx = {
            'nonce': start_nonce + i,
            'to': receiver_address,
            'value': w3.to_wei(0.001, 'ether'),
            'gas': 21000,
            'gasPrice': gas_price,
            'chainId': 1337
        }
        signed_tx = Account.sign_transaction(tx, private_key)
        signed_tx_pool.append(signed_tx.raw_transaction)

    print(f"🚀 Blasting {TOTAL_TRANSACTIONS} transactions in batches of {BATCH_SIZE}...")
    start_time = time.time()

    # 2. Async execution loop using gather to push network saturation
    for i in range(0, TOTAL_TRANSACTIONS, BATCH_SIZE):
        batch = signed_tx_pool[i:i + BATCH_SIZE]

        # Map raw transaction execution to internal web3 coroutines
        tasks = [w3.eth.send_raw_transaction(tx) for tx in batch]

        # Fire the concurrent batch payload immediately
        await asyncio.gather(*tasks, return_exceptions=True)
        print(f"🛸 Batch {(i // BATCH_SIZE) + 1} dispatched successfully.")

    end_time = time.time()
    duration = end_time - start_time

    print("\n🏁 Benchmark Results Summary:")
    print(f"⏱️ Total execution time: {duration:.2f} seconds")
    print(f"📈 Submission rate: {TOTAL_TRANSACTIONS / duration:.2f} TX/sec injected to TxPool")
    print("💡 Run the txpool stats curl command to observe consensus processing.")

if __name__ == '__main__':
    asyncio.run(main())