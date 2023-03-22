# Aira Mae Aloveros
# IMPROVEMENTS
# 1. Allows users to buy multiple tickets in the buy_ticket entrypoint in a single transaction. (Hint: pass number of tickets to buy in the parameters)
# 2. Add entrypoints that can be used by the admin to change ticket cost and maximum number of available tickets. (Hint: Only allow changing these parameters when no game is on i.e number of tickets sold is 0)

import smartpy as sp


class Lottery(sp.Contract):
    def __init__(self):
        self.init(
            players=sp.map(l={}, tkey=sp.TNat, tvalue=sp.TAddress),
            ticket_cost=sp.tez(1),
            tickets_available=sp.nat(5),
            max_tickets=sp.nat(5),
            operator=sp.address("tz1MJnoNz7m1zYtAf8Uv6VPwbsr2pepeh39L") #Hardcoded address for testing in Deployed contract
        )

    @sp.entry_point
    def setup_new_ticket_cost(self, new_ticket_cost):
        new_ticket_cost_tez = sp.utils.nat_to_tez(new_ticket_cost)

        # Sanity checks
        sp.verify(sp.sender == self.data.operator, "NOT_AUTHORISED")
        sp.verify(self.data.tickets_available == self.data.max_tickets, "CHANGING LOTTERY PARAMETERS IS NOT ALLOWED DURING GAME") #number of tickets sold is 0
        sp.verify(new_ticket_cost_tez > sp.tez(0), "INVALID TICKET COST")

        #Set new ticket cost
        self.data.ticket_cost = new_ticket_cost_tez

    @sp.entry_point
    def setup_new_max_ticket(self, new_max_tickets):
        new_max_ticket_nat = sp.as_nat(new_max_tickets)

        # Sanity checks
        sp.verify(sp.sender == self.data.operator, "NOT_AUTHORISED")
        sp.verify(self.data.tickets_available == self.data.max_tickets, "CHANGING PARAMETERS IS NOT ALLOWED DURING GAME") #number of tickets sold is 0
        sp.verify(new_max_ticket_nat > 0, "INVALID NUMBER OF TICKETS")

        #Set new maximum number of available tickets and the current available ticket
        self.data.max_tickets = new_max_ticket_nat
        self.data.tickets_available = self.data.max_tickets

    @sp.entry_point
    def buy_ticket(self, num_of_tix):
        # Sanity checks
        sp.verify(self.data.tickets_available > 0, "NO TICKETS AVAILABLE")
        sp.verify(num_of_tix > 0, "PURCHASED TICKET MUST BE AT LEAST 1")
        sp.verify(self.data.tickets_available >= num_of_tix,
                  "NOT ENOUGH REMAINING AVAILABLE TICKETS")
        sp.verify(sp.amount >= sp.mul(num_of_tix, self.data.ticket_cost), "PAYMENT NOT ENOUGH")
        sp.verify(sp.amount >= sp.tez(0), "INVALID AMOUNT")

        # Storage updates
        self.data.players[sp.len(self.data.players)] = sp.sender
        self.data.tickets_available = sp.as_nat(self.data.tickets_available - num_of_tix)

        # Return extra tez balance to the sender
        extra_balance = sp.amount - sp.mul(num_of_tix, self.data.ticket_cost)
        sp.if extra_balance > sp.mutez(0):
            sp.send(sp.sender, extra_balance)

    @sp.entry_point
    def end_game(self):
        # Sanity checks
        sp.verify(sp.sender == self.data.operator, "NOT_AUTHORISED")
        sp.verify(self.data.tickets_available == 0, "GAME IS YET TO END")

        # Pick a winner
        winner_id = sp.as_nat(sp.now - sp.timestamp(0)) % self.data.max_tickets
        winner_address = self.data.players[winner_id]

        # Send the reward to the winner
        sp.send(winner_address, sp.balance)

        # Reset the game
        self.data.players = {}
        self.data.tickets_available = self.data.max_tickets

    @sp.entry_point
    def default(self):
        sp.failwith("NOT ALLOWED")


@sp.add_test(name="main")
def test():
    scenario = sp.test_scenario()

    # Test accounts
    admin = sp.address("tz1MJnoNz7m1zYtAf8Uv6VPwbsr2pepeh39L") #Hardcoded address for testing in Deployed contract
    alice = sp.test_account("alice")
    bob = sp.test_account("bob")
    mike = sp.test_account("mike")
    charles = sp.test_account("charles")
    john = sp.test_account("john")

    
    # Contract instance
    lottery = Lottery()
    scenario += lottery

    # NOTE:Uncomment each section one by one to test each functions

    #I. BUY TICKET TEST START. Uncomment section to test buy_ticket --------------------------------
    scenario.h1("Testing buy_ticket")
    
    scenario.h2("buy_ticket (valid test)")
    scenario += lottery.buy_ticket(2).run(amount=sp.tez(2), sender=alice)
    
    scenario.h2("buy_ticket: Remaing available tickets not enough (failure test)")
    scenario += lottery.buy_ticket(4).run(amount=sp.tez(4),
                                          sender=alice, valid=False)
    
    scenario.h2("buy_ticket: Purchased ticket must be atleast 1 (failure test)")
    scenario += lottery.buy_ticket(0).run(amount=sp.tez(1),
                                          sender=alice, valid=False)
    
    scenario.h2("buy_ticket: Not enough payment (failure test)")
    scenario += lottery.buy_ticket(2).run(amount=sp.tez(1),
                                          sender=alice, valid=False)
    
    scenario.h2("buy_ticket: Invalid amount (failure test)")
    scenario += lottery.buy_ticket(2).run(amount=sp.tez(1),
                                          sender=alice, valid=False)
    
    scenario.h2("buy_ticket (valid test) continued")
    scenario += lottery.buy_ticket(3).run(amount=sp.tez(5), sender=bob)
    
    scenario.h2("buy_ticket: No Available tickets (failure test)")
    scenario += lottery.buy_ticket(2).run(amount=sp.tez(2),
                                          sender=alice, valid=False)
    
    scenario.h2("end_game (valid test)")
    scenario += lottery.end_game().run(sender = admin, now = sp.timestamp(20))
    # BUY TICKET TEST ENDS ----------------------------------------------------------------------------------------------------------------------------

    #II. END GAME START. Uncomment section to test end_game -------------------------------------------------------------------------------------------
    # scenario.h1("Testing end_game")
    # scenario.h2("valid buy_ticket")
    # scenario += lottery.buy_ticket(2).run(amount=sp.tez(2), sender=alice)
    # scenario += lottery.buy_ticket(3).run(amount=sp.tez(5), sender=bob)
    
    # scenario.h2("end_game (valid test)")
    # scenario += lottery.end_game().run(sender = admin, now = sp.timestamp(20))
    
    # scenario.h2("end_game: Game is yet to end (failure test)")
    # scenario += lottery.end_game().run(sender = admin, now = sp.timestamp(20), valid=False)
    
    # scenario.h2("end_game: Not authorised (failure test)")
    # scenario += lottery.end_game().run(sender = alice, now = sp.timestamp(20), valid=False)
    # END GAME ENDS --------------------------------------------------------------------------------------------------------------------------------

    #III. SET UP NEW TICKET COST START. Uncomment section to test setup_new_ticket_cost ------------------------------------------------------------
    # scenario.h1("Testing setup_new_ticket_cost")
    # scenario.h2("valid buy_ticket")
    # scenario += lottery.buy_ticket(2).run(amount=sp.tez(2), sender=alice)
    
    # scenario.h2("setup_new_ticket_cost: Changing parameters not allowed during game (failure test)")
    # scenario += lottery.setup_new_ticket_cost(10).run(sender = admin, valid=False)
    
    # scenario.h2("valid buy_ticket")
    # scenario += lottery.buy_ticket(3).run(amount=sp.tez(5), sender=bob)
    
    # scenario.h2("valid end_game")
    # scenario += lottery.end_game().run(sender = admin, now = sp.timestamp(20))
    
    # scenario.h2("Game resets. Available ticket is back to ticket_cost")

    # scenario.h2("setup_new_ticket_cost: Not authorised (failure test)")
    # scenario += lottery.setup_new_ticket_cost(10).run(sender = alice, valid=False)
    
    # scenario.h2("setup_new_ticket_cost: Invalid ticket cost (failure test)")
    # scenario += lottery.setup_new_ticket_cost(0).run(sender = admin, valid=False)

    # scenario.h2("setup_new_ticket_cost: (valid test)")
    # scenario += lottery.setup_new_ticket_cost(10).run(sender = admin)
    # SET UP NEW TICKET COST ENDS ---------------------------------------------------------------------------------------------------------------------------

    #IV. SET UP NEW MAXIMUM NUMBER OF AVAILABLE TICKETSTART. Uncomment section to test setup_new_max_ticket --------------------------------------------------
    # scenario.h1("Testing setup_new_max_ticket")
    # scenario.h2("valid buy_ticket")
    # scenario += lottery.buy_ticket(2).run(amount=sp.tez(2), sender=alice)
    
    # scenario.h2("setup_new_max_ticket: Changing parameters not allowed during game (failure test)")
    # scenario += lottery.setup_new_max_ticket(100).run(sender = admin, valid=False)
    
    # scenario.h2("valid buy_ticket")
    # scenario += lottery.buy_ticket(3).run(amount=sp.tez(5), sender=bob)
    
    # scenario.h2("valid end_game")
    # scenario += lottery.end_game().run(sender = admin, now = sp.timestamp(20))
    
    # scenario.h2("Game resets. Available ticket is back to max_ticket")

    # scenario.h2("setup_new_max_ticket: Not authorised (failure test)")
    # scenario += lottery.setup_new_max_ticket(100).run(sender = alice, valid=False)
    
    # scenario.h2("setup_new_max_ticket: Invalid ticket cost (failure test)")
    # scenario += lottery.setup_new_max_ticket(0).run(sender = admin, valid=False)

    # scenario.h2("setup_new_max_ticket: (valid test)")
    # scenario += lottery.setup_new_max_ticket(100).run(sender = admin)
    # SET UP NEW TICKET COST ENDS --------------------------------------------------------------------------------------------------------------------------------
