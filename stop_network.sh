#!/bin/bash

echo "🛑 Stopping all Hyperledger Besu processes..."

# Terminate only the Java processes running the Besu application context
pkill -f "org.hyperledger.besu.Besu"

echo "✅ Network stopped successfully."