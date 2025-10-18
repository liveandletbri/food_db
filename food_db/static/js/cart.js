async function addRecipeToCart(event) {
    let icon = event.target;
    let svgParent = icon.closest('svg')
    let recipeKey = svgParent.getAttribute('data-recipe_key')
    console.log(`Adding recipe ${recipeKey} to cart`)
    
    let apiSuccess = await fetch(`/add_recipe_to_cart/`, {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            recipe_key: recipeKey,
        })
    })
    .then(function(response) {
        if (! response.status == 200) {
            console.log("d'oh!")
            return false
        } else {
            return true
        }
    })
    
    if (apiSuccess) {
        console.log(`Added successfully`)
        svgParent.classList.remove('not_added')
        svgParent.classList.add('added')
    }
}

function addCartIconListeners() {
    // Add event listeners to all add to cart icons
    let addToCartIcons = document.querySelectorAll('.add_to_cart_icon')
    addToCartIcons.forEach(function(icon) {
        let pathChild = icon.querySelector('path')
        icon.addEventListener('click', function(event) {
            // Prevent the icon click from doing anything itself,
            // but trigger the click event on the pathChild instead
            
            // Only trigger if the event did not originate from the path itself
            if (event.target !== pathChild) {
                pathChild.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
            }
        });
        
        // Add the listener to the path child
        pathChild.addEventListener('click', addRecipeToCart)
    })
}

// Need to wait for "onload" to be after all the SVGs are rendered by Font Awesome magic
window.addEventListener('load', addCartIconListeners)