// PeerTutor - Interactive Checkout & Credit Card Formatter

document.addEventListener('DOMContentLoaded', () => {
    const cardInput = document.getElementById('card_number');
    const expiryInput = document.getElementById('expiry');
    const cvcInput = document.getElementById('cvc');

    const cardDisplay = document.getElementById('displayCardNumber');
    const expiryDisplay = document.getElementById('displayExpiry');

    // Live format card number: 4242 4242 4242 4242
    if (cardInput) {
        cardInput.addEventListener('input', (e) => {
            let val = e.target.value.replace(/\D/g, '').substring(0, 16);
            let chunks = val.match(/.{1,4}/g);
            let formatted = chunks ? chunks.join(' ') : '';
            e.target.value = formatted;

            if (cardDisplay) {
                cardDisplay.textContent = formatted || '•••• •••• •••• ••••';
            }
        });
    }

    // Live format expiry date: MM/YY
    if (expiryInput) {
        expiryInput.addEventListener('input', (e) => {
            let val = e.target.value.replace(/\D/g, '').substring(0, 4);
            if (val.length >= 2) {
                val = val.substring(0, 2) + '/' + val.substring(2);
            }
            e.target.value = val;

            if (expiryDisplay) {
                expiryDisplay.textContent = val || 'MM/YY';
            }
        });
    }

    // Restrict CVC to digits only (max 4)
    if (cvcInput) {
        cvcInput.addEventListener('input', (e) => {
            e.target.value = e.target.value.replace(/\D/g, '').substring(0, 4);
        });
    }
});
