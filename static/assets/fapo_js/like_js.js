document.addEventListener('DOMContentLoaded', (event) => {
    const options = {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        mode: 'same-origin'
    }
    let likeButtons = document.querySelectorAll("a.like-btn");
    likeButtons.forEach(function (button) {
            button.addEventListener('click', function (e) {
                    e.preventDefault();
               
                    const formData = new FormData();
                    formData.append("product_id", button.dataset.id);
                    formData.append("action", button.dataset.action);
                    options["body"] = formData;
                    fetch(LikeUrl, options)
                        .then(response => response.json())
                        .then(data => {
                            if (data["status"] === "ok") {
                                const previousAction = button.dataset.action;
                                const action = previousAction === "like" ? "unlike" : "like";
                                button.dataset.action = action;
                                if (action === 'like') {
                                    button.innerHTML = '<i class="bi bi-heart"></i>';
                                } else {
                                    button.innerHTML = '<i class="bi bi-heart-fill text-danger"></i>';
                                }

                            }
                        })
                }
            )
        }
    )
})

document.addEventListener("DOMContentLoaded", function () {
    const starContainers = document.querySelectorAll('.star');

    starContainers.forEach(starContainer => {
        const score = parseInt(starContainer.getAttribute('data-score'), 10);
        const stars = starContainer.querySelectorAll('i');

        stars.forEach((star, index) => {
            if (index < score) {
                star.classList.add('bi-star-fill');
                star.classList.remove('bi-star');
            } else {
                star.classList.add('bi-star');
                star.classList.remove('bi-star-fill');
            }
        });
    });
});


