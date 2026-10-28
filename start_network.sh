#!/bin/bash

# Create the logs directory if it does not exist
mkdir -p logs

echo "🚀 Starting QBFT cluster in the background..."

# 1. Start Node 1 (Bootnode)
./build/install/besu/bin/besu \
  --data-path=qbft_network/node1/data \
  --genesis-file=qbft_network/genesis.json \
  --p2p-port=30301 \
  --p2p-host=127.0.0.1 \
  --rpc-http-enabled \
  --rpc-http-api=ETH,NET,QBFT,WEB3,TXPOOL \
  --rpc-http-port=8541 \
  --rpc-http-cors-origins="*" \
  --sync-min-peers=0 > logs/node1.log 2>&1 &

# Allow the bootnode 1 second to initialize and open the P2P port
sleep 1

BOOTNODE_ENODE="enode://8087f73015facf9160e2d8ed47bcb39aeb121916582df6b06e151f565be9a2155e8a2fd7189cfb3675ab66b70e25bbe2129e079a56705a938a2d2f41fb79c05a@127.0.0.1:30301"

# 2. Start Node 2
./build/install/besu/bin/besu \
  --data-path=qbft_network/node2/data \
  --genesis-file=qbft_network/genesis.json \
  --bootnodes="$BOOTNODE_ENODE" \
  --p2p-port=30302 \
  --p2p-host=127.0.0.1 \
  --rpc-http-enabled \
  --rpc-http-api=ETH,NET,QBFT,WEB3,TXPOOL \
  --rpc-http-port=8542 \
  --rpc-http-cors-origins="*" \
  --sync-min-peers=0 > logs/node2.log 2>&1 &

# 3. Start Node 3
./build/install/besu/bin/besu \
  --data-path=qbft_network/node3/data \
  --genesis-file=qbft_network/genesis.json \
  --bootnodes="$BOOTNODE_ENODE" \
  --p2p-port=30303 \
  --p2p-host=127.0.0.1 \
  --rpc-http-enabled \
  --rpc-http-api=ETH,NET,QBFT,WEB3,TXPOOL \
  --rpc-http-port=8543 \
  --rpc-http-cors-origins="*" \
  --sync-min-peers=0 > logs/node3.log 2>&1 &

# 4. Start Node 4
./build/install/besu/bin/besu \
  --data-path=qbft_network/node4/data \
  --genesis-file=qbft_network/genesis.json \
  --bootnodes="$BOOTNODE_ENODE" \
  --p2p-port=30304 \
  --p2p-host=127.0.0.1 \
  --rpc-http-enabled \
  --rpc-http-api=ETH,NET,QBFT,WEB3,TXPOOL \
  --rpc-http-port=8544 \
  --rpc-http-cors-origins="*" \
  --sync-min-peers=0 > logs/node4.log 2>&1 &

echo "✅ All 4 nodes started successfully!"
echo "📂 Logs are available in the directory: ./logs/"