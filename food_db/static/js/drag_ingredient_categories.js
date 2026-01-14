var source;
let currentUrl = window.location.href
let currentUrlDomain = currentUrl.split("/recipe/")[0]
let currentRecipeKey = currentUrl.split("/recipe/")[1].split('?')[0]
let multiplier = document.getElementById('ingredient_multiplier')

async function getOrderNumber(recipeKey, ingredientCategory) {
    let response = await fetchWithTestDb(`${currentUrlDomain}/get_ingredient_category_order_number/`, {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            recipe_key: recipeKey,
            ingredient_category: ingredientCategory,
        })
    })
    
    return response.text()
}

async function swapOrderNumbers(recipeKey, ingredientCategory1, orderNumber1, ingredientCategory2, orderNumber2) {
    await fetchWithTestDb(`${currentUrlDomain}/swap_ingredient_category_order_numbers/`, {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            recipe_key: recipeKey,
            ingredient_category_1: ingredientCategory1,
            order_number_1: orderNumber1,
            ingredient_category_2: ingredientCategory2,
            order_number_2: orderNumber2,
        })
    })
}

function parseIngredTables(tableNodeList) {
    let tableArray = Array.from(tableNodeList)
    return tableArray.reduce((accumulator, table) => {
        accumulator[table.id] = table
        return accumulator
    }, {})
}

async function handleDragIngredCategoryDrop(e) {
    let targetElement = e.target;
    if (targetElement.nodeName == "TD") {
        // Target the parent row so we can standardize the code below
        targetElement = targetElement.parentNode;   
    }
    if (targetElement.nodeName == "SPAN") {
        // Target the parent row so we can standardize the code below
        targetElement = targetElement.parentNode.parentNode;   
    }  
    if (source != targetElement) {
        // Must be for the same recipe
        let sourceCleanKey = source.getAttribute('data-clean_key')
        let targetCleanKey = targetElement.getAttribute('data-clean_key')
        if (sourceCleanKey != targetCleanKey) {
            console.error(`Cannot swap ingredients from different recipes: ${sourceCleanKey} != ${targetCleanKey}`)
            return
        }

        let sourceCategory = source.getAttribute('data-ingredient_category')
        let sourceOrderNumber = await getOrderNumber(sourceCleanKey, sourceCategory)
        console.log(`getOrderNumber: ${sourceCategory} = ${sourceOrderNumber}`)
        let targetCategory = targetElement.getAttribute('data-ingredient_category')
        let targetOrderNumber = await getOrderNumber(targetCleanKey, targetCategory)
        console.log(`getOrderNumber: ${targetCategory} = ${targetOrderNumber}`)

        let diff = targetOrderNumber - sourceOrderNumber
        newSourceOrderNumber = parseInt(sourceOrderNumber) + diff
        newTargetOrderNumber = parseInt(targetOrderNumber) - diff

        if (newSourceOrderNumber != newTargetOrderNumber) {

            await swapOrderNumbers(sourceCleanKey, sourceCategory, newSourceOrderNumber, targetCategory, newTargetOrderNumber)
            console.log(`swapOrderNumbers: ${sourceCategory} changed to ${newSourceOrderNumber}, ${targetCategory} changed to ${newTargetOrderNumber}`)

            let multiplierValue = multiplier.value
            
            let response = await fetchWithTestDb(`/recipe/${currentRecipeKey}?multiplier=${multiplierValue}`, {
                method: "GET",
            })
            .then(function(response) {
                // The response is a Response instance.
                return response.text();
            })
            
            // Render the response text as an html element, then extract the new search result div from its innards
            let responseHtml = document.createElement('html')
            responseHtml.innerHTML = response
            let responseIngredients = parseIngredTables(responseHtml.querySelectorAll('.recipe_detail_ingredients_table'))
            let currentIngredients = parseIngredTables(document.querySelectorAll('.recipe_detail_ingredients_table'))

            // Frankenstein it right into our existing page
            for (let key in responseIngredients) {
                currentIngredients[key].innerHTML = responseIngredients[key].innerHTML
            }
        } else {
            console.log(`No change in order numbers: ${sourceCategory} = ${sourceOrderNumber}, ${targetCategory} = ${targetOrderNumber}`)
        }
    }
}

function handleDragIngredCategoryStart(e) {
    source = e.target;
    if (source.nodeName == "TD") {
        // Target the parent row
        source = e.target.parentNode;   
    }
    if (source.nodeName == "SPAN") {
        // Target the parent row
        source = target.parentNode.parentNode;   
    } 
    console.log(`I see you dragging...`)
    e.dataTransfer.effectAllowed = 'move';
}

function handleDragIngredCategoryOver(e) {
    e.preventDefault(); // Necessary. Allows us to drop.
}