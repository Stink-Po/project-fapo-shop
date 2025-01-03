document.addEventListener('DOMContentLoaded', function () {
    // Attach event listener to body once to avoid duplication
    document.body.addEventListener('change', function (event) {
        if (event.target.classList.contains('color-radios')) {
            const productId = event.target.getAttribute('data-product-id');

            const colorId = event.target.value;

            // Construct URL for GET request with query parameters
            const url = `${shopUrl}?color=${colorId}`;

            // Send a single GET request to fetch color-specific product data
            fetch(url)
                .then(response => response.json())
                .then(data => {

                    const productContainer = document.querySelector(`.buy-btn[data-product-id="${productId}"]`);


                    if (productContainer) {
                        if (data.in_stock) {
                            productContainer.classList.remove('btn-danger', 'disabled');
                            productContainer.classList.add('main-color-one-bg');
                            productContainer.innerHTML = `<i class="bi bi-basket text-white"></i> <span class="text-white">خرید محصول</span>`;
                        } else {
                            productContainer.classList.add('btn-danger', 'disabled');
                            productContainer.classList.remove('main-color-one-bg');
                            productContainer.innerHTML = `<i class="bi bi-basket text-white"></i> <span class="text-white">اتمام موجودی</span>`;
                        }
                    }
                })
                .catch(error => console.error('Error:', error));
        }
    });
});

