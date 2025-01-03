function formatNumberWithCommas(number) {
    return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}


const emptyCard = `<div class="content" id="empty-card">
                    <div class="container-fluid">
                        <div class="content-box">
                            <div class="container-fluid">
                                <div class="text-center">
                                    <img src="/static/assets/image/empty-cart%20(1).svg" style="max-width: 400px;"
                                         alt="" class="mx-auto d-block">
                                    <h6 class="font-18 mt-4">سبد خرید شما خالی است</h6>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>`

const haveDiscountHtml = `
                <div class="item">
                        <div class="price d-flex">
                            <p class=""> میزان کد تخفیف اعمال شده : <span
                                    class="text-end  price-off fw-bold me-2" id="amount"></span>
                            </p>
                        </div>

                    </div>
                 <div class="factor pt-3 item">
                    <div class="title pb-3">
                        <div class="d-flex align-items-center">
                            <i class="fa-solid fa-2x fa-bag-shopping main-color-one-color"></i>&nbsp;&nbsp;
                            <h6 class="font-16">سفارش شما</h6>
                        </div>
                    </div>
                     <div class="item">
                         <div class="factor-item p-2 rounded-3 shadow-sm bg-light d-flex align-items-center justify-content-between" id="discount-amount">
                            
                        </div>
                        <div class="factor-item p-2 rounded-3 shadow-sm bg-light d-flex align-items-center justify-content-between">
                            <p class="mb-0 fw-bold">تخفیف کالا ها :</p>
                            <p class="mb-0 text-danger" id="total-discount"> تومان</p>
                        </div>
               
                    <div id="bag">
                        <div class="factor-item p-2 rounded-3 shadow-sm bg-light d-flex align-items-center justify-content-between">
                            <p class="mb-0 fw-bold">جمع کل:</p>
                            <p class="mb-0 price-off fw-bold me-2 text-success me-2" id="total-price"> تومان</p>
                        </div>
                    </div>
                    <div class="action mt-3 d-flex align-items-center justify-content-center" id="check-card-div">
                        
                            <a href="#" class="btn border-0 main-color-two-bg rounded-3">سبد خرید</a>
                        
                    </div>
                </div>`
const factorItems = `
                    <div class="d-flex flex-column justify-content-center align-items-center text-center p-3 item hidden " id="status">
    <span id="ok-message" class="text-success"></span>
    <span id="error-message" class="text-danger"></span>
</div>

                   <div class="item" id="form-div"> 
                    <form id="coupon-form">
                        <input type = "hidden" name = "csrfmiddlewaretoken" value = "${csrftoken}" >
                        <div class="d-flex">
                            <div class="form-floating me-2">
                                <input name="code" type="text"
                                       class="form-control float-input me-2"
                                       id="discount-code" placeholder="کد تخفیف">
                                <label for="discount-code">کد تخفیف</label>
                            </div>

                            <!-- Error message placeholder -->

                            <button type="button"
                                    id="code-btn"
                                    class="btn border-0 main-color-one-bg waves-effect waves-light  rounded-3 me-2">
                                برسی کد
                            </button>
                        </div>


                    </form>
                </div>
                <div class="action mt-3 d-flex align-items-center justify-content-center">
                    <a id="hidden-btn" href=""
                       class="btn border-0 main-color-one-bg rounded-3 w-100 hidden text-center align-items-center justify-content-center">اعمال
                        کد تخفیف

                    </a>

                </div>
                 <div class="factor pt-3 item">
                    <div class="title pb-3">
                        <div class="d-flex align-items-center">
                            <i class="fa-solid fa-2x fa-bag-shopping main-color-one-color"></i>&nbsp;&nbsp;
                            <h6 class="font-16">سفارش شما</h6>
                        </div>
                    </div>
           
                        <div class="factor-item p-2 rounded-3 shadow-sm bg-light d-flex align-items-center justify-content-between">
                            <p class="mb-0 fw-bold">تخفیف کالا ها :</p>
                            <p class="mb-0" id="total-discount"> تومان</p>
                        </div>
               
                    <div id="bag">
                   
                        <div class="factor-item p-2 rounded-3 shadow-sm bg-light d-flex align-items-center justify-content-between">
                            <p class="mb-0 fw-bold">جمع کل:</p>
                            <p class="price-off fw-bold me-2 text-success me-2" id="total-price"> تومان</p>
                        </div>
                    </div>
                    <div class="action mt-3 d-flex align-items-center justify-content-center" id="check-card-div">
                        
                            <a href="#" class="btn border-0 main-color-two-bg rounded-3">سبد خرید</a>
                        
                    </div>
                </div>`


function reloadCard() {
    const fullCard = document.getElementById("cart-canvases");
    if (document.getElementById('main-details')) {
        updateCartDetail();
    }
    fetch(getCardUrl, options)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok') {
                // Initialize card contents and factor area
                fullCard.innerHTML = `<div id="cart-items-container"></div>
                                      <div id="factor-div"></div>`;
                const cardItemsContainer = document.getElementById("cart-items-container");
                const factorArea = document.getElementById("factor-div");

                if (data.cart_length === 0) {
                    cardItemsContainer.innerHTML = "";
                    factorArea.innerHTML = emptyCard;
                } else {
                    if (data.have_discount) {
                        factorArea.innerHTML = haveDiscountHtml;
                        document.getElementById("amount").innerText = `${data.amount} %`;
                        document.getElementById("discount-amount").innerHTML = `
                        <p class="mb-0 fw-bold"> کسر با کد تخفیف : </p>
                                    <p class="mb-0 text-danger">  ${formatNumberWithCommas(data.price_of_discount)} - تومان</p>
                            
                        `;
                    } else {
                        factorArea.innerHTML = factorItems;
                    }
                    const nextButtonDiv = document.getElementById("check-card-div")
                    if (data.user) {
                        nextButtonDiv.innerHTML = `<a href="${shopingCardUrl}" class="btn border-0 main-color-two-bg rounded-3">سبد خرید</a>`
                    } else {
                        nextButtonDiv.innerHTML = `<a href="${loginUrl}" class="btn border-0 main-color-two-bg rounded-3">برای تکمیل سفارش وارد سایت شوید</a>
`
                    }
                    let totalDiscount = 0;
                    let totalPrice = 0;

                    // Populate cart items
                    data.cart.forEach(item => {
                        totalDiscount += parseInt(item.total_discount, 10);
                        totalPrice += parseInt(item.total_price, 10);
                        cardItemsContainer.innerHTML += `
                            <div class="item">
                                <div class="row gy-2">
                                    <div class="col-12">
                                        <div class="title">
                                            <h6 class="font-14">${item.product}</h6>
                                        </div>
                                        <div class="price d-flex p-2">
                                        <p class="fw-bold me-2">رنگ:</p>
                                        <p class="text-muted font-12 me-2">
                                            <span style="display: inline-block; width: 20px; height: 20px; border-radius: 50%; background-color: ${item.color}; margin-right: 10px;"></span>
                                        </p>
                                    </div>
                                        <div class="price d-flex">
                                            <p class="fw-bold me-2">مبزان تخفیف:</p>
                                            <p class="text-end mb-2 price-off fw-bold me-2">
                                                ${item.discount !== "0" ? `${item.discount} %` : ' - '}
                                            </p>
                                        </div>
                                        <div class="price d-flex">
                                            <p class="fw-bold me-2">قیمت کالا:</p>
                                            ${item.discount !== "0" ? `
                                                <p class="text-end mb-2 price-off fw-bold me-2">${formatNumberWithCommas(item.discount_price)} تومان</p>
                                                <p class="text-end price-discount me-2">${formatNumberWithCommas(item.price)} تومان</p>
                                            ` : `
                                                <p class="text-end mb-2 price-off fw-bold me-2">${formatNumberWithCommas(item.price)} تومان</p>
                                            `}
                                        </div>
                                        <div class="price d-flex">
                                            <p class="fw-bold me-2">تعداد:</p>
                                            <p class="text-end mb-2 price-off fw-bold me-2">${item.quantity} عدد</p>
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
                                        <div class="price d-flex">
                                            <p class="fw-bold me-2">جمع قیمت این کالا:</p>
                                            <p class="text-end mb-2 price-off fw-bold me-2">${formatNumberWithCommas(item.total_price)} تومان</p>
                                        </div>
                                        <div class="action d-flex">
                                            <p class="fw-bold me-2 pt-2">حذف کالا :</p>
                                            <div class="remove rounded-3">
                                                <a class="me-2 waves-effect remove-btn" href="" 
                                                   data-product-id="${item.product_id}" data-color-id="${item.color_id}">
                                                    <i class="bi bi-x font-25 text-danger remove-btn"></i>
                                                </a>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>`;
                    });

                    // Update total price and discount areas
                    document.getElementById("total-price").innerText = `${formatNumberWithCommas(data.total_price)} تومان`;
                    document.getElementById("total-discount").innerText = totalDiscount !== 0 ?
                        `${formatNumberWithCommas(totalDiscount)}- تومان` : " - ";
                    attachEventListenersToCart();

                }
            }
        })
        .catch(error => console.error("Fetch error:", error));
    updateCartLength();  // Ensure cart length updates


}

function attachEventListenersToCart() {
    // Set up the discount code check button
    const codeBtn = document.getElementById('code-btn');
    if (codeBtn) {
        codeBtn.addEventListener('click', checkDiscountCode);
    }

    // Attach remove button listeners
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