let deleteRecipeButton = document.getElementById('delete_recipe_button')
let deleteRecipeDialog = document.getElementById('delete_recipe_dialog')
let deleteRecipeConfirmButton = document.getElementById('delete_recipe_confirm_button')
let deleteRecipeCancelButton = document.getElementById('delete_recipe_cancel_button')

async function deleteRecipe() {
    console.log('Deleting recipe...')
    
    let recipeKey = deleteRecipeButton.getAttribute('data-recipe_key')
    
    let apiSuccess = await fetch('/delete_recipe/', {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            recipe_key: recipeKey
        })
    })
    .then(function(response) {
        if (response.status == 200) {
            return true
        } else {
            console.log("d'oh!")
            return false
        }
    })
    
    if (apiSuccess) {
        console.log('Recipe deleted successfully')
        
        // Redirect to the index page after successful deletion
        window.location.href = '/'
    } else {
        console.log('Failed to delete recipe')
    }
}

if (deleteRecipeButton) {
    deleteRecipeButton.addEventListener('click', function() {
        deleteRecipeDialog.style.display = 'flex'
    })
    deleteRecipeConfirmButton.addEventListener('click', function() {
        deleteRecipeDialog.style.display = 'none'
        deleteRecipe()
    })
    deleteRecipeCancelButton.addEventListener('click', function() {
        deleteRecipeDialog.style.display = 'none'
    })
}

