async function deleteRecipeImage(event) {
    event.preventDefault(); // Prevent page refresh

    let deleteConfirm = confirm("Are you sure you want to delete this pic?");
    if (deleteConfirm) {
        // User clicked OK
        console.log(`Deleting image!`)
        let currentUrl = window.location.href
        let currentUrlDomain = currentUrl.split("/recipe/")[0]
        let recipeImageDiv = event.target.closest('.recipe_image_div')
        let recipeImageFileName = recipeImageDiv.getAttribute('data-image_file_name')

        let deleteRecipeImageResponse = await fetch(`${currentUrlDomain}/delete_recipe_image/`, {
            method: "POST",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                file_name: recipeImageFileName,
            })
        })
        .then(function(response) {
            // The response is a Response instance.
            console.log(`Response status: ${response.status}`)
            if (response.status == 200) {
                recipeImageDiv.style.display = 'none'
            }
            return response.text()
        })
        console.log('Done!')
    } else {
        // User clicked Cancel
        console.log('Crisis averted! Not deleting the pic.')
    }
}

let deleteRecipeImageButtons = document.querySelectorAll(".delete_recipe_image_button")
deleteRecipeImageButtons.forEach(btn => btn.addEventListener('click', function(event) {
    deleteRecipeImage(event)
}, btn))