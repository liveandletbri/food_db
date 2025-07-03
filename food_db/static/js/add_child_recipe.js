let childRecipeSearchInput = document.getElementById('recipe_search_input')
let exampleChildRecipe = document.getElementById('example_child_recipe')
let childRecipeContainer = document.getElementById('child_recipes_div')
let existingRecipes = JSON.parse(existingRecipesRaw.textContent)
let existingRecipeTitles = Object.keys(existingRecipes)
let submitButton = document.getElementById('add_child_recipe_button')

function addListenersToChildRecipeButtons() {
    let moveButtons = document.querySelectorAll('.move_child_recipe_button')
    let deleteButtons = document.querySelectorAll('.delete_child_recipe_button')
    
    moveButtons.forEach(btn => btn.addEventListener('click', moveChildRecipe, btn))
    deleteButtons.forEach(btn => btn.addEventListener('click', deleteChildRecipe, btn))
}

addListenersToChildRecipeButtons()

function attachChildRecipe(e) {
    e.preventDefault()  // This textbox is in a form and I don't want Enter to trigger form submission
    let childRecipe = exampleChildRecipe.cloneNode(true)
    childRecipe.style.display = ''
    childRecipe.removeAttribute('id')  // avoid duplicate IDs

    // Did they type a valid recipe title?
    let recipeTitleInput = childRecipeSearchInput.value
    if ( ! existingRecipeTitles.includes(recipeTitleInput) ) {
        console.error('you suck')
        return
    }

    // Have they already attached this?
    let allChildRecipes = childRecipeContainer.querySelectorAll('.attached_child_recipe_div')
    let attachedChildrenTitles = Array.from(allChildRecipes).map(rec => rec.getAttribute('data-recipe_name'))
    if (attachedChildrenTitles.includes(recipeTitleInput)) {
        console.error('you really suck')
        return
    }

    childRecipe.setAttribute('data-recipe_name', recipeTitleInput)

    // Get URL for recipe and update <a> 
    let recipeKey = existingRecipes[recipeTitleInput]
    let recipeLink = childRecipe.querySelectorAll('a')[0]
    let currentUrl = window.location.href
    let currentUrlDomain = currentUrl.split("/add/")[0]
    let recipeUrl = `${currentUrlDomain}/recipe/${recipeKey}`
    recipeLink.setAttribute('href', recipeUrl)
    recipeLink.textContent = recipeTitleInput

    // Add recipe key to hidden input
    let childRecipeInput = childRecipe.querySelectorAll('input')[0]
    childRecipeInput.setAttribute('value', recipeKey)

    childRecipeContainer.appendChild(childRecipe)
    childRecipeSearchInput.value = ''
    addListenersToChildRecipeButtons()
    hideTopAndBottomMoveButtons()
}

submitButton.addEventListener('click', function(event) {attachChildRecipe(event)})
// Add attachChildRecipe to submission of the text box 
childRecipeSearchInput.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        attachChildRecipe(event)
    }
});

function hideTopAndBottomMoveButtons() {
    let allChildRecipes = childRecipeContainer.querySelectorAll('.attached_child_recipe_div')
    let firstChild = allChildRecipes[0]
    let lastChild = allChildRecipes[allChildRecipes.length - 1]

    // First child should not have an up arrow and last one should not have down. All other arrows are visible.
    allChildRecipes.forEach(child => {
        let upArrow = child.querySelectorAll('.move_child_recipe_up_button')[0]
        let downArrow = child.querySelectorAll('.move_child_recipe_down_button')[0]
        if (child == firstChild) {
            upArrow.style.display = 'none'
        } else {
            upArrow.style.display = ''
        }
        if (child == lastChild) {
            downArrow.style.display = 'none'
        } else {
            downArrow.style.display = ''
        }

    })

}

function moveChildRecipe(e) {
    let element = e.target
    let svg

    if (element.nodeName == 'svg') {
        svg = element
    } else if (element.nodeName == 'path') {
        svg = element.parentNode
    } else {
        console.log(element)
        console.error('wut')
    }
    
    let childRecipe = svg.parentNode
    let upOrDown

    if (svg.classList.contains('move_child_recipe_up_button')) {
        upOrDown = 'up'
    } else if (svg.classList.contains('move_child_recipe_down_button')) {
        upOrDown = 'down'
    } else {
        console.error('SVG did not have appropriate classes')
    }

    if (upOrDown == 'up') {
        childRecipeContainer.insertBefore(childRecipe, childRecipe.previousElementSibling)
    } else if (upOrDown == 'down') {
        childRecipeContainer.insertBefore(childRecipe.nextElementSibling, childRecipe)
    }
    hideTopAndBottomMoveButtons()
}

function deleteChildRecipe(e) {
    let element = e.target
    let img

    if (element.nodeName == 'IMG') {
        img = element
    } else {
        console.log(element)
        console.error('wut')
    }
    
    let childRecipe = img.parentNode
    childRecipe.remove()
    hideTopAndBottomMoveButtons()
}