function checkDiscountCode(event) {
    event.preventDefault();
    const validateUrl = checkDiscountCodeUrl;
    const discountCode = document.getElementById('discount-code').value;

    const options = {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        mode: 'same-origin',
    };

    const newFormData = new FormData();
    newFormData.append("code", discountCode);
    options.body = newFormData;
    const statusDiv = document.getElementById("status");
    fetch(validateUrl, options)
        .then(response => response.json())
        .then(data => {
            if (data.status === "ok") {

                statusDiv.classList.remove("hidden")
                const amount = data.amount;
                document.getElementById('error-message').innerText = '';
                document.getElementById('coupon-form').classList.add("hidden");
                document.getElementById("ok-message").innerText = "کد وارد شده معتبر است ";

                const hiddenDiv = document.getElementById("hidden-btn");
                hiddenDiv.classList.remove("hidden", "d-none");
                hiddenDiv.classList.add("d-block", "d-flex");
                const formDiv = document.getElementById("form-div");

                formDiv.classList.add("hidden")


                eventListenerForUseDiscount(hiddenDiv, discountCode, amount);
            } else {
                statusDiv.classList.remove("hidden")
                document.getElementById('error-message').innerText = `${data.message}`;
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

document.getElementById('code-btn').addEventListener('click', checkDiscountCode);

function eventListenerForUseDiscount(element, code, amount) {
    element.addEventListener("click", function (e) {
        e.preventDefault();

        const options = {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
            },
            mode: 'same-origin',
        };

        const formData = new FormData();
        formData.append("code", code);
        formData.append("amount", amount);
        options.body = formData;

        fetch(addDiscountToCartUrl, options)
            .then(response => response.json())
            .then(data => {
                if (data.status === "ok") {
                    reloadCard();
                } else {

                }
            })
            .catch(error => console.error('Error:', error));
    }, { once: true });
}