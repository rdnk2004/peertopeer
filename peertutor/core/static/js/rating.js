// PeerTutor - Interactive Star Rating Selector

document.addEventListener('DOMContentLoaded', () => {
    const starButtons = document.querySelectorAll('.star-icon-btn');
    const ratingInput = document.getElementById('ratingValue');
    const descriptor = document.getElementById('ratingDescriptor');

    const descriptions = {
        '1': '1 Star - Needs Work',
        '2': '2 Stars - Fair',
        '3': '3 Stars - Good',
        '4': '4 Stars - Very Good',
        '5': '5 Stars - Outstanding!'
    };

    function highlightStars(count) {
        starButtons.forEach(btn => {
            const val = parseInt(btn.dataset.value);
            if (val <= count) {
                btn.classList.add('is-active');
            } else {
                btn.classList.remove('is-active');
            }
        });
    }

    starButtons.forEach(btn => {
        btn.addEventListener('mouseenter', () => {
            const val = parseInt(btn.dataset.value);
            starButtons.forEach(b => {
                if (parseInt(b.dataset.value) <= val) {
                    b.classList.add('is-hovered');
                } else {
                    b.classList.remove('is-hovered');
                }
            });
            if (descriptor) {
                descriptor.textContent = descriptions[val.toString()] || `${val} Stars`;
            }
        });

        btn.addEventListener('mouseleave', () => {
            starButtons.forEach(b => b.classList.remove('is-hovered'));
            const currentVal = ratingInput ? ratingInput.value : '5';
            if (descriptor) {
                descriptor.textContent = descriptions[currentVal] || `${currentVal} Stars`;
            }
        });

        btn.addEventListener('click', () => {
            const val = btn.dataset.value;
            if (ratingInput) {
                ratingInput.value = val;
            }
            highlightStars(parseInt(val));
            if (descriptor) {
                descriptor.textContent = descriptions[val] || `${val} Stars`;
            }
        });
    });

    // Initialize with default (5 stars)
    const initialVal = ratingInput ? parseInt(ratingInput.value || '5') : 5;
    highlightStars(initialVal);
    if (descriptor) {
        descriptor.textContent = descriptions[initialVal.toString()] || `${initialVal} Stars`;
    }
});
