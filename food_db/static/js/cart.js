let cartCounter = document.getElementById('cart_size')

async function updateCart(event) {
    // Find the cart icon (which has the data-recipe_key attribute)
    let cartIcon = event.target.closest('.add_to_cart_icon')
    let recipeKey = cartIcon.getAttribute('data-recipe_key')
    
    let adding = cartIcon.classList.contains('not_added')
    let logVerb
    let apiName
    if ( adding ) {
        logVerb = 'Add'
        apiName = '/add_recipe_to_cart/'
    } else {
        logVerb = 'Remov'
        apiName = '/remove_recipe_from_cart/'
    }

    console.log(`Cart update: ${logVerb}ing recipe ${recipeKey}`)
    
    let apiSuccess = await fetch(apiName, {
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
        console.log(`${logVerb}ed successfully`)
        if ( adding ) {
            cartIcon.classList.remove('not_added')
            cartIcon.classList.add('added')
        } else {
            cartIcon.classList.remove('added')
            cartIcon.classList.add('not_added')
        }
    }
}

function addCartIconListener() {
    // Attach listener to document body and delegate events.
    // This way it works even if Font Awesome re-renders the SVGs,
    // which would reset listeners
    document.addEventListener('click', function(event) {
        // Check if the clicked element is a cart icon or inside one
        let cartIcon = event.target.closest('.add_to_cart_icon')
        if (cartIcon) {
            event.preventDefault()
            updateCart(event)
        }
    })
}

// Setup event delegation when page loads
window.addEventListener('load', addCartIconListener)