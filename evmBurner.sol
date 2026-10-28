// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.0;

contract EvmBurner {
    uint256 public totalOperations;
    mapping(uint256 => bytes32) public stateStorage;

    // This function burns CPU via crypto loops and hits disk via state writes (SSTORE)
    function executeHeavyTask(uint256 iterations) public {
        bytes32 hash = keccak256(abi.encodePacked(block.timestamp, msg.sender));

        // 1. CPU Load: Intensive cryptographic hashing loop
        for (uint256 i = 0; i < iterations; i++) {
            hash = keccak256(abi.encodePacked(hash, i));
        }

        // 2. Disk I/O Load: Writing directly to the blockchain state
        uint256 currentSlot = totalOperations;
        stateStorage[currentSlot] = hash;
        totalOperations = currentSlot + 1;
    }
}