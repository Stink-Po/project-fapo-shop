function discountCodeCheckinDetails(event) {
    event.preventDefault();
    const validateUrl = checkDiscountCodeUrl;
    const discountCode = document.getElementById('discount-code-details').value;

    const optionsDetails = {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        mode: 'same-origin',
    };

    const newFormDataDetails = new FormData();
    newFormDataDetails.append("code", discountCode);
    optionsDetails.body = newFormDataDetails;
    const statusDiv = document.getElementById("status-details");
    fetch(validateUrl, optionsDetails)
        .then(response => response.json())
        .then(data => {
            if (data.status === "ok") {
                statusDiv.classList.remove("hidden")
                const amount = data.amount;
                document.getElementById('error-message-details').innerText = '';
                document.getElementById('coupon-form-details').classList.add("hidden");
                document.getElementById("ok-message-details").innerText = "کد وارد شده معتبر است ";

                const hiddenDiv = document.getElementById("hidden-btn-details");
                hiddenDiv.classList.remove("hidden", "d-none");
                hiddenDiv.classList.add("d-block", "d-flex");
                const formDiv = document.getElementById("discount-from-details");

                formDiv.classList.add("hidden")


                eventListenerForUseDiscount(hiddenDiv, discountCode, amount);
            } else {
                statusDiv.classList.remove("hidden")
                document.getElementById('error-message-details').innerText = 'کد تخفیف نامعتبر است';
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

document.getElementById('submit-code-btn').addEventListener('click', discountCodeCheckinDetails);


const mainDetailDiv = document.getElementById("main-details")


function updateCartDetail() {
    const emptyCartDetails = `<div class="content">
                <div class="container-fluid">
                    <div class="content-box">
                        <div class="container-fluid">
                            <div class="text-center">
                                <img src="/static/assets/image/empty-cart%20(1).svg" style="max-width: 400px;"
                                     alt=""
                                     class="mx-auto d-block">
                                <h6 class="font-18 mt-4">سبد خرید شما خالی است</h6>
                            </div>
                        </div>
                    </div>
                </div>
            </div>`;

    const nonEmptyCartDetails = `<div class="content">
        <div class="container-fluid">

            <div class="line-step-container d-sm-block d-none">
                <div class="line-step">
                    <div class="line-step-boxs">
                        <div class="line-step-box complete">

                            <p>سبد خرید</p>
                            <div class="icon">
                                1
                            </div>

                        </div>
                        <div class="line-step-box disabled">

                            <p> آدرس و جزییات پرداخت</p>
                            <div class="icon">
                                2
                            </div>

                        </div>
                        <div class="line-step-box disabled">

                            <p>تکمیل سفارش</p>
                            <div class="icon">
                                3
                            </div>

                        </div>
                    </div>
                </div>
            </div>

        </div>

        <div class="container-fluid">
            <div class="cart-product">
                <div class="row gy-4">
                    <div class="col-lg-9" id="products-details">

                    </div>
                    <div class="col-lg-3">
                        <div class="cart-canvases position-sticky top-0">
                        <div id="discount-area">
                            
                        </div>
                            <div class="item">
                                <div class="factor">
                                    <div class="title">
                                        <div class="d-flex align-items-center">
                                            <i class="fa-solid fa-2x fa-bag-shopping main-color-one-color"></i>&nbsp;&nbsp;

                                            <h6 class="font-16">جمع سفارش شما </h6>
                                        </div>
                                    </div>
                                    <div class="factor-item p-2 rounded-3 shadow-sm bg-light d-flex align-items-center justify-content-between"
                                         id="total-discount-details">
                                        
                                    </div>
                                    <div class="factor-item p-2 rounded-3 shadow-sm bg-light d-flex align-items-center justify-content-between">
                                        <p class="mb-0">هزینه بسته بندی و ارسال : </p>
                                        <p class="mb-0"> ${formatNumberWithCommas(70000)} تومان </p>
                                    </div>
                                    
                                    <div class="factor-item p-2 rounded-3 shadow-sm bg-light d-flex align-items-center justify-content-between hidden"
                                     id="discount-details">
                                     
                                    </div>
                              
                                    <div class="factor-item p-2 rounded-3 shadow-sm bg-light d-flex align-items-center justify-content-between"
                                         id="total-details">
                                        
                                    </div>

                                    <div class="action mt-3 d-flex align-items-center justify-content-center">
                                        <a href="${orderAdressUrl}"
                                           class="btn border-0 main-color-one-bg rounded-3 d-block w-100">
                                           تایید و ادامه
                                            </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

    </div>`;
    const mainDetailDiv = document.getElementById("main-details")
    fetch(getCardUrl, options)
        .then(response => response.json())
        .then(data => {
            if (data.status === "ok") {

                if (data.cart_length === 0) {

                    mainDetailDiv.innerHTML = "";
                    mainDetailDiv.innerHTML = emptyCartDetails;
                } else {

                    mainDetailDiv.innerHTML = "";

                    mainDetailDiv.innerHTML = nonEmptyCartDetails;

                    var totalDiscountDetail = 0;
                    data.cart.forEach(item => {
                        totalDiscountDetail += parseInt(item.total_discount, 10);
                        document.getElementById("products-details").innerHTML += `<div class="cart-product-item">
                                            <div class="content-box">
                                                <div class="container-fluid">
                                                    <div class="cart-items">
                                                        <div class="item">
                                                            <div class="row gy-2">
                                                                <div class="col-2 w-100-in-400">
                                                                    <div class="image">
                                                                        <img src="${item.image_url}"
                                                                             alt=""
                                                                             class="img-fluid">
                                                                    </div>
                                                                </div>
                                                                <div class="col-10 w-100-in-400">
                                                                    <div class="d-flex justify-content-between align-items-start">
                                                                        <div class="d-flex align-items-start flex-column me-2">
                                                                            <div class="title d-flex align-items-center flex-wrap">
                                                                                <h6 class="font-16">${item.product}
                                                                                    ${item.discount !== "0" ? `
                                                <span class="badge ms-2 danger-label rounded-pill">${item.discount} %</span>
                                            ` : `
                                                
                                            `}
         
                                                                                </h6>
                                                                            </div>
                                                                            <div class="cart-item-feature d-flex align-items-center flex-wrap mt-3">
                                                                                <div class="item d-flex align-items-center">
                                                                                    <div class="icon">
                                                                                    </div>
                                                                                    <div class="saller-name mx-2">رنگ:
                                                                                    </div>
                                                                                    <div class="saller-name text-muted">
                                                                                        <div class="product-meta-color-items mt-0">
                                                                                            <label class="btn-light mb-0 px-2 py-1">
                                                                                                <span style="background-color: ${item.color};"></span>
                                                                                      
                                                                                            </label>
                                                                                        </div>
                                                                                    </div>
                                                                                </div>
                                                                            </div>
                                                                        </div>
                                                                        <div class="remove danger-label ">
                                                                            <a class="remove-btn" href=""
                                                                               data-product-id="${item.product_id}"
                                                                               data-color-id="${item.color_id}">

                                                                                <i class=" bi bi-trash-fill
                                                                               font-25"></i>
                                                                            </a>
                                                                        </div>
                                                                    </div>
                                                                    <div class="action d-flex flex-wrap justify-content-sm-end justify-content-center align-items-center mt-3">
                                                                        ${item.discount !== "0" ? `
                                                <div class="cart-item-feature d-flex align-items-center flex-wrap">
                                                                                <div class="item d-flex align-items-center me-2">
                                                                                    <p class="mb-0 old-price font-16">${formatNumberWithCommas(item.price)}</p>
                                                                                </div>
                                                                                <div class="item d-flex align-items-center">
                                                                                    <p class="mb-0 new-price font-16">${formatNumberWithCommas(item.discount_price)}
                                                                                        تومان</p>
                                                                                </div>
                                                                            </div>
                                            ` : `
                                                <div class="cart-item-feature d-flex align-items-center flex-wrap">
                                                                                <div class="item d-flex align-items-center">
                                                                                    <p class="mb-0 new-price font-16">${formatNumberWithCommas(item.price)}
                                                                                        تومان</p>
                                                                                </div>
                                                                            </div>
                                            `}
                                                        
                                                                        <div class="counter me-2">
                                                <label>
                                                    <div class="input-group bootstrap-touchspin bootstrap-touchspin-injected">
                                                        <span class="input-group-btn input-group-prepend">
                                                            <button class="btn-counter decrement  waves-effect waves-light bootstrap-touchspin-down" type="button">-</button>
                                                        </span>
                                                        <input type="text" name="count" class="counter form-counter"
                                                               data-product-id="${item.product_id}"
                                                               data-color-id="${item.color_id}"
                                                               value="${item.quantity}">
                                                        <span class="input-group-btn input-group-append">
                                                            <button class="btn-counter increment waves-effect waves-light bootstrap-touchspin-up" type="button">+</button>
                                                        </span>
                                                    </div>
                                                </label>
                                            </div>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </div>

                                                    </div>
                                                </div>
                                            </div>
                                        </div>`;

                    })

                    if (data.have_discount) {
                        const dis = document.getElementById("discount-details")
                        if (dis) {

                            dis.innerHTML = `<p class="mb-0 fw-bold">مبلغ کسر شده با کد تخفیف:</p>
                                                    <p class="mb-0 text-danger">${formatNumberWithCommas(data.price_of_discount)}تومان
                                                        - </p>`;
                            dis.classList.remove("hidden");
                        }
                        document.getElementById("discount-area").innerHTML = "";
                        document.getElementById("discount-area").innerHTML = `<div class="item">
                                            <div class="price d-flex" id="discount-amount-details">
                                                <p class=""> میزان کد تخفیف اعمال شده : <span
                                                        class="text-end  price-off fw-bold me-2">${data.amount} %</span>
                                                </p>
                                            </div>

                                        </div>`;
                        document.getElementById("total-discount-details").innerHTML = `<p class="mb-0">جمع تخفیف کالا ها : </p>
                                        <p class="mb-0 text-danger">${formatNumberWithCommas(data.total_discount)} -
                                            تومان</p>`;
                        const totalFactor = data.total_price + 70000;
                        document.getElementById("total-details").innerHTML = `
                                                <p class="mb-0 fw-bold">جمع کل :</p>
                                                <p class="mb-0 text-success">${formatNumberWithCommas(totalFactor)} تومان</p>
                                            `;
                        document.getElementById("discount-details").innerHTML = `<p class="mb-0 fw-bold">مبلغ کسر شده با کد تخفیف:</p>
                                                    <p class="mb-0 text-danger">${formatNumberWithCommas(data.price_of_discount)}تومان
                                                        - </p>`;

                    } else {

                        document.getElementById("discount-area").innerHTML
                        document.getElementById("discount-area").innerHTML = `<div
                            class="d-flex flex-column justify-content-center align-items-center text-center p-3 item hidden"
                            id="status-details">
                            <span id="ok-message-details" class="text-success"></span>
                            <span id="error-message-details" class="text-danger"></span>
                        </div>

                        <div class="item" id="discount-from-details">
                            <form id="coupon-form-details">
                                <input type = "hidden" name = "csrfmiddlewaretoken" value = "${csrftoken}" >
                                <div class="d-flex">
                                    <div class="form-floating me-2">
                                        <input name="code" type="text"
                                               class="form-control float-input me-2"
                                               id="discount-code-details" placeholder="کد تخفیف">
                                            <label for="discount-code-details">کد تخفیف</label>
                                    </div>

                                    <!-- Error message placeholder -->

                                    <button type="button"
                                            id="submit-code-btn"
                                            class="btn border-0 main-color-one-bg waves-effect waves-light  rounded-3 me-2">
                                        برسی کد
                                    </button>
                                </div>


                            </form>
                        </div>
                        <div class="action mt-3 d-flex align-items-center justify-content-center">
                            <a id="hidden-btn-details" href=""
                               class="btn border-0 main-color-one-bg rounded-3 w-100 hidden text-center align-items-center justify-content-center">اعمال
                                کد تخفیف

                            </a>

                        </div>
                    `;
                        if (data.have_discount) {

                            document.getElementById("discount-amount-details").classList.remove("hidden");


                        }

                        document.getElementById("total-discount-details").innerHTML = `<p class="mb-0">جمع تخفیف کالا ها : </p>
                                        <p class="mb-0 text-danger">${formatNumberWithCommas(data.total_discount)} -
                                            تومان</p>`;
                        const totalFactor = data.total_price + 70000;
                        document.getElementById("total-details").innerHTML = `
                                                <p class="mb-0 fw-bold">جمع کل :</p>
                                                <p class="mb-0 text-success">${formatNumberWithCommas(totalFactor)} تومان</p>
                                            `;


                    }
                }

            }
        })

    attachEventListenersToCartDetails();
}

function attachEventListenersToCartDetails() {
    // Set up the discount code check button
    const codeBtnDetails = document.getElementById('submit-code-btn');
    if (codeBtnDetails) {
        codeBtnDetails.addEventListener('click', discountCodeCheckinDetails);
    }
    document.querySelectorAll(".remove-btn").forEach(btn => {
        btn.addEventListener("click", function (e) {
            e.preventDefault();
            const productId = btn.dataset.productId;
            const productColorId = btn.dataset.colorId;

            if (productId && productColorId) {
                const formData = new FormData();
                formData.append("product_id", productId);
                formData.append("color_id", productColorId);
                options["body"] = formData;

                fetch(removeUrl, options)
                    .then(response => response.json())
                    .then(data => {
                        if (data["status"] === "ok") {
                            reloadCard();
                        } else {
                            console.error("Error updating cart:", data.message);
                        }
                    })
                    .catch(error => console.error("Fetch error:", error));
            } else {
                console.error("Product ID or Color ID is missing.");
            }
        });
    });


}