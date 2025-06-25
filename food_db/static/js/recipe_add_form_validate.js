let submitRecipeButton = document.querySelector("#submit_recipe_button")
let form = document.querySelector("#add_recipe_container")

let titleInput = document.querySelector("#id_title")
let urlInput = document.querySelector("#id_url")
let recipeBookInput = document.querySelector("#id_recipe_book")
let recipeBookPageInput = document.querySelector("#id_recipe_book_page")
let durationInput = document.querySelector("#id_duration_minutes")
let servingsInput = document.querySelector("#id_servings")
let caloriesInput = document.querySelector("#id_calories_per_recipe")
let notesInput = document.querySelector("#id_notes")

// These are declared in other scripts loaded in the same page
// let ingredTable = document.querySelector("#ingred-table")
// let stepTable = document.querySelector("#step_table")
// function showAndHideTooltip is in tooltip.js

let titleTooltip = document.querySelector("#title_tooltip")
let urlTooltip = document.querySelector("#url_tooltip")
let recipeBookTooltip = document.querySelector("#recipe_book_tooltip")
let recipeBookPageTooltip = document.querySelector("#recipe_book_page_tooltip")
let durationTooltip = document.querySelector("#duration_minutes_tooltip")
let servingsTooltip = document.querySelector("#servings_tooltip")
let caloriesTooltip = document.querySelector("#calories_per_recipe_tooltip")
let ingredFoodTooltip = document.querySelector("#ingred_0_food_tooltip")
let stepTooltip = document.querySelector("#step_0_description_tooltip")

async function validateAddRecipe(e) {
    e.preventDefault()

    let invalid = false
    
    // Get current form values
    let title = titleInput.value
    let url = urlInput.value
    let recipeBook = recipeBookInput.value
    let recipeBookPage = recipeBookPageInput.value
    let duration = durationInput.value
    let servings = servingsInput.value
    let calories = caloriesInput.value
    let notes = notesInput.value
    let ingredFood = ingredTable.rows[1].querySelector(`input[name$='_food']`).value
    let step = stepTable.rows[0].querySelector('textarea').value
    
    // Title must be unique
    let currentUrl = window.location.href
    if (currentUrl.endsWith('/add')) {
        let currentUrlDomain = currentUrl.split("/add")[0]
        let responseCode = await fetch(`${currentUrlDomain}/recipe/${title}`, {
            method: "GET",
        })
        .then(function(response) {
            // The response is a Response instance.
            return response.status
        })
        if (responseCode == 200) {
            showAndHideTooltip(titleTooltip)
            invalid = true
        } else if (responseCode != 404) {
            console.log(`Ooops somehow we got a ${responseCode} on the title validation`)
            invalid = true
        } else (
            console.log("Don't worry, that 404 was a good thing. It means this is a unique title!")
        )
    }

    // Title must have valid characters
    let titleAlphaNumOnly = title.replace(/[^\w\d]/,'')
    if ( titleAlphaNumOnly.length < 4 ) {
        invalid = true
        showAndHideTooltip(titleTooltip)
    }

    // URL must be valid URL
    if ( url != '') {
        try {
            let testUrl = new URL(url)
        } catch (_) {
            showAndHideTooltip(urlTooltip)
            invalid = true
        }
    }

    // Recipe book and page OR ingredient and step
    if (
        ((recipeBook == '' || recipeBookPage == '') && (ingredFood == '' || step == '')) ||
        (recipeBook == '' && recipeBookPage != '') ||
        (recipeBook != '' && recipeBookPage == '')
    ) {
        showAndHideTooltip(recipeBookTooltip)
        invalid = true
    }

    // Recipe book page
    if (recipeBookPage != '') {
        if (/^\d+$/.test(recipeBookPage) == false) {
            showAndHideTooltip(recipeBookPageTooltip)
            invalid = true
        }
    }

    // Duration
    if (duration != '') {
        if (/^\d+$/.test(duration) == false) {
            showAndHideTooltip(durationTooltip)
            invalid = true
        }
    }

    // Servings must either be a number or a range
    if (servings != '') {
        let servingsNoSpaces = servings.replace(/\s/g,'')
        if (/^\d+$/.test(servingsNoSpaces) == false && /^\d+\-\d+$/.test(servingsNoSpaces) == false) {
            showAndHideTooltip(servingsTooltip)
            invalid = true
        }
    }

    // Calories
    if (calories != '') {
        if (/^\d+$/.test(calories) == false) {
            showAndHideTooltip(caloriesTooltip)
            invalid = true
        }
    }

    // Rename rows so the ID numbers are ordered the same as what's visible on the page
    let ingredTableArray = Array.from(ingredTable.rows) // convert HTMLCollection into Array, so we can...
    let ingredRows = ingredTableArray.slice(1) // Remove header row
    for (var i = 0, row; row = ingredRows[i]; i++) {
        row.setAttribute('name', `ingred_${i}_row`)
        // Update names and IDs of inputs
        row.querySelectorAll('[id^=id_ingred]').forEach(
            input => input.setAttribute(
                'id',
                input.getAttribute('id').replace(/\d+/,i)
            )
        )
        row.querySelectorAll('[id^=id_ingred]').forEach(
            input => input.setAttribute(
                'name',
                input.getAttribute('name').replace(/\d+/,i)
            )
        )
    }

    let textArea
    for (var i = 0, row; row = stepTable.rows[i]; i++) {
        row.setAttribute('name', `step_${i}_row`)
        textArea = row.querySelector('textarea')
        textArea.setAttribute('id', textArea.getAttribute('id').replace(/\d+/,i))
        textArea.setAttribute('name', textArea.getAttribute('name').replace(/\d+/,i))
    }

    // Submit if all clear!
    if (invalid == false) {
        
        if (currentUrl.endsWith('/add/')) {
            submitRecipeButton.innerText = 'Adding...'
        } else {
            submitRecipeButton.innerText = 'Updating...'
        }
        submitRecipeButton.style.backgroundColor = 'lightgray'
        submitRecipeButton.style.opacity = 0.25
        form.submit()
    }
}

isBakingInput.addEventListener('change', function() {
    // Set the value of the hidden input to match the switch
    document.getElementById('id_is_baking_recipe').checked = isBakingInput.checked
})

submitRecipeButton.addEventListener('click', validateAddRecipe)