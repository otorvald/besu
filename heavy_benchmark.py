import asyncio
import time
from web3 import AsyncWeb3
from web3.providers import AsyncHTTPProvider
from solcx import compile_source, install_solc

# Define variables for nodes and load configuration
RPC_URL = "http://127.0.0.1:8541"
with open("qbft_network/node1/data/key", "r") as key_file:
    PRIVATE_KEY = key_file.read().strip()
ITERATIONS_PER_TX = 500
TOTAL_TXS = 200
BATCH_SIZE = 50

# Source code of our heavy contract
CONTRACT_SOURCE = """
// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.0;

contract EvmBurner {
    uint256 public totalOperations;
    mapping(uint256 => bytes32) public stateStorage;

    // High CPU/Storage utilization task
    function executeHeavyTask(uint256 iterations) public {
        bytes32 hash = keccak256(abi.encodePacked(block.timestamp, msg.sender));
        for (uint256 i = 0; i < iterations; i++) {
            hash = keccak256(abi.encodePacked(hash, i));
        }
        uint256 currentSlot = totalOperations;
        stateStorage[currentSlot] = hash;
        totalOperations = currentSlot + 1;
    }
}
"""

async def main():
    print("🛠️ Installing and configuring Solidity compiler...")
    install_solc("0.8.20")
    compiled_sol = compile_source(CONTRACT_SOURCE, solc_version="0.8.20")
    contract_id, contract_interface = compiled_sol.popitem()

    bytecode = contract_interface['bin']
    abi = contract_interface['abi']

    w3 = AsyncWeb3(AsyncHTTPProvider(RPC_URL))
    sender_account = w3.eth.account.from_key(PRIVATE_KEY)
    sender_address = sender_account.address

    print(f"🔗 Connected to Besu. Deployer address: {sender_address}")

    start_nonce = await w3.eth.get_transaction_count(sender_address)
    print("🚀 Deploying EvmBurner contract to the network...")

    construct_tx = await w3.eth.contract(abi=abi, bytecode=bytecode).constructor().build_transaction({
        'from': sender_address,
        'nonce': start_nonce,
        'gas': 3000000,
        'gasPrice': await w3.eth.gas_price,
        'chainId': 1337
    })

    signed_tx = w3.eth.account.sign_transaction(construct_tx, PRIVATE_KEY)
    # FIX: Changed to raw_transaction
    tx_hash = await w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"⏳ Waiting for deployment transaction: {tx_hash.hex()}")

    receipt = None
    while receipt is None:
        try:
            receipt = await w3.eth.get_transaction_receipt(tx_hash)
        except Exception:
            await asyncio.sleep(0.5)

    contract_address = receipt['contractAddress']
    print(f"✅ Contract successfully deployed at: {contract_address}")

    contract = w3.eth.contract(address=contract_address, abi=abi)
    current_nonce = start_nonce + 1
    gas_price = await w3.eth.gas_price

    print(f"📊 Preparing {TOTAL_TXS} heavy EVM transactions...")
    tasks = []

    for i in range(TOTAL_TXS):
        tx = await contract.functions.executeHeavyTask(ITERATIONS_PER_TX).build_transaction({
            'from': sender_address,
            'nonce': current_nonce + i,
            'gas': 500000,
            'gasPrice': gas_price,
            'chainId': 1337
        })
        signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        # FIX: Changed to raw_transaction
        tasks.append(signed.raw_transaction)

    print(f"🔥 Blasting transactions in batches of {BATCH_SIZE}...")
    start_time = time.time()

    for i in range(0, len(tasks), BATCH_SIZE):
        batch = tasks[i:i + BATCH_SIZE]
        await asyncio.gather(*[w3.eth.send_raw_transaction(tx) for tx in batch])
        print(f"🛸 Batch {i // BATCH_SIZE + 1} injected successfully.")

    total_time = time.time() - start_time
    print("\n🏁 Heavy Load Benchmark Results Summary:")
    print(f"⏱️ Total injection time: {total_time:.2f} seconds")
    print(f"📈 Injection rate: {TOTAL_TXS / total_time:.2f} HEAVY_TX/sec sent to TxPool")

if __name__ == "__main__":
    asyncio.run(main())