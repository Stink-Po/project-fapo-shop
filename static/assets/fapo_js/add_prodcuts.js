function buyButtonListers() {
    document.addEventListener('DOMContentLoaded', function () {

        const buyButtons = document.querySelectorAll('.buy-btn');

        buyButtons.forEach(button => {
            button.addEventListener('click', function (event) {
                event.preventDefault(); // Prevent default behavior
                const productId = this.getAttribute('data-product-id');
                const num = Number(productId);
                const colorInput = document.querySelector(`input[name="color-options-${productId}"]:checked`);
                const colorId = colorInput ? colorInput.value : null; // Get selected color ID
                const quantity = "1"; // Set default quantity to 1

                if (productId && colorId) {

                    const newFormData = new FormData();
                    newFormData.append("product_id", productId);
                    newFormData.append("color_id", colorId);
                    newFormData.append("quantity", quantity);

                    const option = {
                        method: 'POST', headers: {'X-CSRFToken': csrftoken}, body: newFormData, mode: 'same-origin' // This ensures that cookies are sent with the request
                    };

                    // Send AJAX request to the server to add the product
                    fetch(buyUrl, option)
                        .then(response => {
                            if (!response.ok) {
                                throw new Error(`Network response was not ok, status: ${response.status}`);
                            }
                            return response.json();
                        })
                        .then(data => {

                            if (data.status === 'ok') {
                                console.log("add product call")
                                reloadCard();

                            } else {
                                // Show error message
                            }
                        })
                        .catch(error => {
                            console.log(error)
                        });
                } else {

                }
            });
        });
    });


}

buyButtonListers();