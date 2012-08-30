def accept(deal):
    if len(deal.north.spades) >= 5 and deal.north.hcp >= 12:
        print(deal)
        return True

