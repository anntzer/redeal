def accept(deal):
    if len(deal.north.spades) >= 5 and deal.north.hcp >= 12:
        print(deal) # use print(unicode(deal)) if using Python2
        return True

