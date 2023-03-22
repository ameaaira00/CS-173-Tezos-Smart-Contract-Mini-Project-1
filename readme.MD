# Lottery Smart Contract on Tezos
Aira Mae Aloveros

## Rules of the game
- Each ticket costs 1 tez.
- A participant can buy as many tickets as they want. More tickets = Higher chances of winning.
- A total of 5 tickets are to be sold before deciding a winner.
- The game resets after a winner is chosen.

### Added Improvements:
- Users are allowed to buy multiple tickets in the buy_ticket entrypoint in a single transaction.
- Admin can change ticket cost and maximum number of available tickets when no game is on.

## Contract Address
Check deployed contract in Limanet using the address KT1GUmntWmocev19kx6W1zQvYHk8Nfs8ZmuS
- To check test transactions in the deployed contract and interact with the it, go to https://better-call.dev/limanet/KT1GUmntWmocev19kx6W1zQvYHk8Nfs8ZmuS/operations
- For testing purposes, use the admin address tz1MJnoNz7m1zYtAf8Uv6VPwbsr2pepeh39L and click simulate. 