function addToCart(productId) {

    fetch(`/add_to_cart/${productId}`)

        .then(response => response.json())

        .then(data => {

            let popup = document.getElementById("popup");

            popup.style.display = "block";

            popup.innerText = "✅ Product added to cart successfully!";

            setTimeout(() => {
                popup.style.display = "none";
            }, 2000);

            let cartCount = document.getElementById("cart-count");

            cartCount.innerText = data.cart_count;

        });

}