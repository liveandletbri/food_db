let cartCounter = document.getElementById('cart_size')
let emptyCartButton = document.getElementById('empty_cart_button')
let emptyCartDialog = document.getElementById('empty_cart_dialog')
let emptyCartConfirmButton = document.getElementById('empty_cart_confirm_button')
let emptyCartCancelButton = document.getElementById('empty_cart_cancel_button')

function updateCartShape(cartSize) {
    // Remove existing shape classes
    cartCounter.classList.remove('single-digit', 'multi-digit')
    
    // Set CSS custom property for digit count
    cartCounter.style.setProperty('--digit-count', cartSize.length)
    
    // Add appropriate class based on number of digits
    if (cartSize.length === 1) {
        cartCounter.classList.add('single-digit')
    } else {
        cartCounter.classList.add('multi-digit')
    }
}

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

        // Update counter in nav bar
        let cartSize = await fetch('/get_cart_size/', {
            method: "GET",
        })
        .then(function(response) {
            return response.text()
        })
        cartCounter.innerText = cartSize
        if ( cartSize > 0 ) {
            cartCounter.style.display = ''
            // Update shape based on number of digits
            updateCartShape(cartSize)
        } else {
            cartCounter.style.display = 'none'
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

// Initialize cart shape when page loads
window.addEventListener('load', function() {
    if ( parseInt(cartCounter.innerText) > 0 ) {
        updateCartShape(cartCounter.innerText)
    }
})

async function emptyCart() {
    console.log('Emptying cart...')
    
    let apiSuccess = await fetch('/empty_cart/', {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
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
        console.log('Cart emptied successfully')
        
        // Update cart counter and visibility
        cartCounter.innerText = '0'
        cartCounter.style.display = 'none'
        
        // Reload the page to reflect the empty cart
        window.location.reload()
    } else {
        console.log('Failed to empty cart')
    }
}

if ( emptyCartButton ) {
    emptyCartButton.addEventListener('click', function() {
        emptyCartDialog.style.display = 'flex'
    })
    emptyCartConfirmButton.addEventListener('click', function() {
        emptyCartDialog.style.display = 'none'
        emptyCart()
    })
    emptyCartCancelButton.addEventListener('click', function() {
        emptyCartDialog.style.display = 'none'
    })
}