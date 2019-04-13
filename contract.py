"""
CSC148, Winter 2019
Assignment 1

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2019 Bogdan Simion, Diane Horton, Jacqueline Smith
"""
import datetime
from math import ceil
from typing import Optional
from bill import Bill
from call import Call



# Constants for the month-to-month contract monthly fee and term deposit
MTM_MONTHLY_FEE = 50.00
TERM_MONTHLY_FEE = 20.00
TERM_DEPOSIT = 300.00

# Constants for the included minutes and SMSs in the term contracts (per month)
TERM_MINS = 100

# Cost per minute and per SMS in the month-to-month contract
MTM_MINS_COST = 0.05

# Cost per minute and per SMS in the term contract
TERM_MINS_COST = 0.1

# Cost per minute and per SMS in the prepaid contract
PREPAID_MINS_COST = 0.025


class Contract:
    """ A contract for a phone line

    This is an abstract class. Only subclasses should be instantiated.

    === Public Attributes ===
    start:
         starting date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    """
    start: datetime.datetime
    bill: Optional[Bill]

    def __init__(self, start: datetime.date) -> None:
        """ Create a new Contract with the <start> date, starts as inactive
        """
        self.start = start
        self.bill = None

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.

        Ensure information to calculate monthly bill is provided to after
        advancing.
        """
        raise NotImplementedError

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        self.bill.add_billed_minutes(ceil(call.duration / 60.0))

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        return float(self.bill.get_cost())


# TODO: Implement the MTMContract, TermContract, and PrepaidContract


class TermContract(Contract):
    """
    A contract for a phone line

    This is an abstract class. Only subclasses should be instantiated.

    === Public Attributes ===
    start:
         starting date for the contract
    end:
         end date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    """
    start: datetime.datetime
    end: datetime.datetime
    cancellation_date: datetime.datetime
    bill: Optional[Bill]

    def __init__(self, start: datetime.date, end: datetime.date) -> None:
        """ Create a new TermContract with the <start> and <end> date, starts
        as inactive
        """
        Contract.__init__(self, start)
        self.end = end

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.

        Ensure information to calculate monthly bill is provided to after
        advancing.
        """
        self.bill = bill
        if self.start.month == month or self.start.year == year:
            self.bill.add_fixed_cost(TERM_DEPOSIT)

        if self.start.month < month or self.start.year < year:
            self.cancellation_date = datetime.datetime(year, month, 1)

        self.bill.add_fixed_cost(TERM_MONTHLY_FEE)
        self.bill.set_rates("TERM", TERM_MINS_COST)

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """

        if self.bill.free_min == TERM_MINS:
            self.bill.add_billed_minutes(ceil(call.duration / 60.0))

        else:
            if self.bill.free_min + ceil(call.duration / 60.0) < TERM_MINS:
                self.bill.free_min += ceil(call.duration / 60.0)

            else:
                free_min = TERM_MINS - self.bill.free_min
                self.bill.add_free_minutes(free_min)
                self.bill.add_billed_minutes(ceil(call.duration / 60.0) -
                                             TERM_MINS + self.bill.free_min)


    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        if datetime.datetime(self.end.year, self.end.month, self.end.day)\
                < datetime.datetime(self.cancellation_date.year,
                                    self.cancellation_date.month,
                                    self.cancellation_date.day):
            self.start = None
            return self.bill.get_cost()
        else:
            self.start = None
            return float(self.bill.get_cost() - TERM_DEPOSIT)


class MTMContract(Contract):
    """ A contract for a phone line

    This is an abstract class. Only subclasses should be instantiated.

    === Public Attributes ===
    start:
         starting date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    """
    start: datetime.datetime
    bill: Optional[Bill]

    def __init__(self, start: datetime.date) -> None:
        """ Create a new Contract with the <start> date, starts as inactive
        """
        Contract.__init__(self, start)

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.

        Ensure information to calculate monthly bill is provided to after
        advancing.
        """
        self.bill = bill
        self.bill.add_fixed_cost(MTM_MONTHLY_FEE)
        self.bill.set_rates("MTM", MTM_MINS_COST)

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        self.bill.add_billed_minutes(ceil(call.duration / 60.0))

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        return float(self.bill.get_cost())


class PrepaidContract(Contract):
    """ A contract for a phone line

    This is an abstract class. Only subclasses should be instantiated.

    === Public Attributes ===
    start:
         starting date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
            the input dataset
    prepaid_bal:
         the prepaid balance for the contract
    """
    start: datetime.datetime
    bill: Optional[Bill]
    balance: int

    def __init__(self, start: datetime.date, balance: int) -> None:
        """ Create a new Contract with the <start> date, starts as inactive
        """
        Contract.__init__(self, start)
        self.balance = -balance

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.

        Ensure information to calculate monthly bill is provided to after
        advancing.

        Balance is continuing from the prev month.
        """
        self.bill = bill
        self.bill.set_rates("Preapid", PREPAID_MINS_COST)

        if self.balance > -10:
            self.balance -= 25

        self.bill.add_fixed_cost(self.balance)

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        self.balance += (ceil(call.duration / 60.0)) * PREPAID_MINS_COST
        self.bill.add_billed_minutes(ceil(call.duration / 60.0))

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        if self.balance > 0:
            return float(self.bill.get_cost())
        return 0.0


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'datetime', 'bill', 'call'
        ],
        'disable': ['R0902', 'R0913'],
        'generated-members': 'pygame.*'
    })
