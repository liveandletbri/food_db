let childRecipeSearchInput = document.getElementById('recipe_search_input')
let exampleChildRecipe = document.getElementById('example_child_recipe')
let childRecipeContainer = document.getElementById('child_recipes_div')
let existingRecipes = JSON.parse(existingRecipesRaw.textContent)
let existingRecipeTitles = Object.keys(existingRecipes)
let submitButton = document.getElementById('add_child_recipe_button')

window.addEventListener('load', function() {
    initializeRowShiftFunctionality('.attached_child_recipe_div', '#child_recipes_div')
})

function attachChildRecipe(e) {
    e.preventDefault()  // This textbox is in a form and I don't want Enter to trigger form submission
    let childRecipe = exampleChildRecipe.cloneNode(true)
    childRecipe.style.display = ''
    childRecipe.removeAttribute('id')  // avoid duplicate IDs
    childRecipe.classList.remove('ignore_row');

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
    initializeRowShiftFunctionality('.attached_child_recipe_div', '#child_recipes_div')
}

submitButton.addEventListener('click', function(event) {attachChildRecipe(event)})
// Add attachChildRecipe to submission of the text box 
childRecipeSearchInput.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        attachChildRecipe(event)
    }
});
