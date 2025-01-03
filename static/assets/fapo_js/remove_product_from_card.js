document.addEventListener("DOMContentLoaded", () => {
    const removeBtns = document.querySelectorAll(".remove-btn");
    removeBtns.forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.preventDefault();
            const productId = btn.dataset.productId;
            const productColorId = btn.dataset.colorId;

            const formData = new FormData();
            formData.append("product_id", productId);
            formData.append("color_id", productColorId);

            const options = {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrftoken,// important for Django to recognize AJAX requests
                }
            };

            fetch(removeUrl, options)
                .then(response => response.json())
                .then(data => {
                    if (data["status"] === "ok") {
                        console.log("Product removed successfully.");
                        reloadCard(); // Ensure this function refreshes your cart display
                    } else {

                    }
                })
                .catch(error => {


                });
        });
    });
});
