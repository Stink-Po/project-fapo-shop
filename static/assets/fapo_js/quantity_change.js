document.addEventListener('click', function (event) {
    if (event.target.classList.contains('btn-counter')) {
        const input = event.target.closest('.input-group').querySelector('input.form-counter');
        let currentValue = parseInt(input.value, 10) || 0;

        if (event.target.classList.contains('increment')) {
            currentValue += 1;
        } else if (event.target.classList.contains('decrement')) {
            currentValue -= 1;
        }

        // Ensure the value doesn't go below zero
        if (currentValue < 1) currentValue = 1;

        // Update the visible value
        input.value = currentValue;
        input.setAttribute('value', currentValue);

        // Retrieve product ID and color ID from data attributes
        const productId = input.dataset.productId;
        const colorId = input.dataset.colorId;

        // Prepare payload for the fetch request
        const payload = new URLSearchParams();
        payload.append('product_id', productId);
        payload.append('color_id', colorId);
        payload.append('quantity', currentValue.toString());

        // Fetch options with CSRF token
        const options = {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: payload.toString(),
        };

        // Send POST request to update cart quantity
        fetch(quantityUrl, options)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok') {
                    console.log("Cart updated successfully. New cart length:", data.cart_len);
                    console.log("quantity change call")
                    reloadCard();
                } else {
                    console.error("Error updating cart:", data.message);
                }
            })
            .catch(error => console.error("Fetch error:", error));
    }
});
