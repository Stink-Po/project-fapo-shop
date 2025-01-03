function updateCartLength() {
    const cartLenElements = document.querySelectorAll('.cart-count');

    fetch(cartLenUrl, options)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Network response was not ok, status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'ok') {
                cartLenElements.forEach(element => {
                    element.innerText = data.cart_len;
                });
            }
        })
        .catch(error => console.error("Error updating cart length:", error));
}
