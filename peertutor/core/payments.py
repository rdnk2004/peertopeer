# Payment and Payout Isolation Module (Fulfills SRS R26 & R11)
import uuid

def calculate_escrow_amount(hourly_rate, commission_percent=10.0):
    """Calculates total booking amount and platform commission fee."""
    amount = float(hourly_rate)
    commission = amount * (commission_percent / 100.0)
    return round(amount, 2), round(commission, 2)

def process_test_payment(card_number, expiry, cvc, amount):
    """
    Simulates test-mode payment gateway processing (SRS R11).
    Validates test card credentials and generates a unique transaction reference.
    """
    clean_card = str(card_number).replace(' ', '').replace('-', '')
    if not clean_card.isdigit() or len(clean_card) < 13:
        return False, "Invalid card number format. Use test card 4242-4242-4242-4242."
    
    # Generate mock transaction reference ID
    txn_id = f"TXN-ESCROW-{uuid.uuid4().hex[:10].upper()}"
    return True, txn_id

def process_tutor_payout(booking):
    """Releases payout from escrow to tutor upon session completion (SRS R13)."""
    net_payout = float(booking.amount) - float(booking.commission)
    booking.status = 'completed'
    booking.save()
    return net_payout
