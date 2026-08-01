# Payment and Payout Isolation Module (Fulfills SRS R26)

def calculate_escrow_amount(hourly_rate, commission_percent=10.0):
    """Calculates total booking amount and platform commission fee."""
    amount = float(hourly_rate)
    commission = amount * (commission_percent / 100.0)
    return round(amount, 2), round(commission, 2)

def process_tutor_payout(booking):
    """Releases payout from escrow to tutor upon session completion."""
    net_payout = float(booking.amount) - float(booking.commission)
    booking.status = 'completed'
    booking.save()
    return net_payout
