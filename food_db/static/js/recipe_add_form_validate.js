let submitRecipeButton = document.querySelector("#submit_recipe_button")
let form = document.querySelector("#add_recipe_container")

let titleInput = document.querySelector("#id_title")
let urlInput = document.querySelector("#id_url")
let recipeBookInput = document.querySelector("#id_recipe_book")
let recipeBookPageInput = document.querySelector("#id_recipe_book_page")
let durationInput = document.querySelector("#id_duration_minutes")
let servingsInput = document.querySelector("#id_servings")
let caloriesInput = document.querySelector("#id_calories_per_serving")
let notesInput = document.querySelector("#id_notes")
let ingredFoodInput = document.querySelector("#id_ingred_0_food")
let stepInput = document.querySelector("#id_step_0_description")

let titleTooltip = document.querySelector("#title_tooltip")
let urlTooltip = document.querySelector("#url_tooltip")
let recipeBookTooltip = document.querySelector("#recipe_book_tooltip")
let recipeBookPageTooltip = document.querySelector("#recipe_book_page_tooltip")
let durationTooltip = document.querySelector("#duration_minutes_tooltip")
let servingsTooltip = document.querySelector("#servings_tooltip")
let caloriesTooltip = document.querySelector("#calories_per_serving_tooltip")
let ingredFoodTooltip = document.querySelector("#ingred_0_food_tooltip")
let stepTooltip = document.querySelector("#step_0_description_tooltip")

// Disable form submission on pressing Enter
// $(document).ready(function() {
//     $(window).keydown(function(event){
//         if(event.keyCode == 13) {
//             event.preventDefault();
//             return false;
//         }
//     });
// });

function hideToolTip(tooltip) {
    tooltip.className = "form_validate_tooltip"
}

function showToolTip(tooltip) {
    tooltip.className = "form_validate_tooltip visible"
}

function showAndHideTooltip(tooltip) {
    tooltip.scrollIntoView({behavior: 'smooth', block: 'center'})
    setTimeout(showToolTip, 300, tooltip)
    setTimeout(hideToolTip, 3000, tooltip)
}

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
    let ingredFood = ingredFoodInput.value
    let step = stepInput.value
    
    // Title must be unique
    let currentUrl = window.location.href
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
        (recipeBook == '' || recipeBookPage == '') && (ingredFood == '' || step == '') ||
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
    
    // Submit if all clear!
    if (invalid == false) {
        form.submit()
    }
}

submitRecipeButton.addEventListener('click', validateAddRecipe)