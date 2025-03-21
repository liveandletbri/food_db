var source;
let currentUrl = window.location.href
let currentUrlDomain = currentUrl.split("/recipe/")[0]
let currentRecipeKey = currentUrl.split("/recipe/")[1]

async function getOrderNumber(ingredientCategory) {
    let response = await fetch(`${currentUrlDomain}/get_ingredient_category_order_number/`, {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            recipe_title: recipeTitle,  // recipeTitle is defined in cook_meal.js
            ingredient_category: ingredientCategory,
        })
    })
    
    return response.text()
}

async function swapOrderNumbers(ingredientCategory1, orderNumber1, ingredientCategory2, orderNumber2) {
    await fetch(`${currentUrlDomain}/swap_ingredient_category_order_numbers/`, {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            recipe_title: recipeTitle,  // recipeTitle is defined in cook_meal.js
            ingredient_category_1: ingredientCategory1,
            order_number_1: orderNumber1,
            ingredient_category_2: ingredientCategory2,
            order_number_2: orderNumber2,
        })
    })
}

async function handleDrop(e) {
    let targetElement = e.target;
    if (targetElement.nodeName == "TD") {
        // Target the parent row so we can standardize the code below
        targetElement = targetElement.parentNode;   
    }  
    if (source != targetElement) {
        let sourceCategory = source.children[0].getAttribute('data-ingredient_category')
        let sourceOrderNumber = await getOrderNumber(sourceCategory)
        console.log(`getOrderNumber: ${sourceCategory} = ${sourceOrderNumber}`)
        let targetCategory = targetElement.children[0].getAttribute('data-ingredient_category')
        let targetOrderNumber = await getOrderNumber(targetCategory)
        console.log(`getOrderNumber: ${targetCategory} = ${targetOrderNumber}`)

        let diff = targetOrderNumber - sourceOrderNumber
        newSourceOrderNumber = parseInt(sourceOrderNumber) + diff
        newTargetOrderNumber = parseInt(targetOrderNumber) - diff

        if (newSourceOrderNumber != newTargetOrderNumber) {

            await swapOrderNumbers(sourceCategory, newSourceOrderNumber, targetCategory, newTargetOrderNumber)
            console.log(`swapOrderNumbers: ${sourceCategory} changed to ${newSourceOrderNumber}, ${targetCategory} changed to ${newTargetOrderNumber}`)

            let currentUrl = window.location.href
            let currentRecipeKey = currentUrl.split("/recipe/")[1]

            let response = await fetch(`/recipe/${currentRecipeKey}`, {
                method: "GET",
            })
            .then(function(response) {
                // The response is a Response instance.
                return response.text();
            })
            
            // Render the response text as an html element, then extract the new search result div from its innards
            let responseHtml = document.createElement('html')
            responseHtml.innerHTML = response
            let responseIngredients = responseHtml.querySelector('#recipe_detail_ingredients_table')
            let currentIngredients = document.querySelector('#recipe_detail_ingredients_table')
        
            // Frankenstein it right into our existing page
            currentIngredients.innerHTML = responseIngredients.innerHTML
        } else {
            console.log(`No change in order numbers: ${sourceCategory} = ${sourceOrderNumber}, ${targetCategory} = ${targetOrderNumber}`)
        }
    }
}

function handleDragStart(e) {
    source = e.target;
    if (source.nodeName == "TD") {
        // Target the parent row
        source = e.target.parentNode;   
    }
    console.log(`I see you dragging...`)
    e.dataTransfer.effectAllowed = 'move';
}

function handleDragOver(e) {
    e.preventDefault(); // Necessary. Allows us to drop.
}