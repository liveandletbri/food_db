let searchForm = document.querySelector("#search_form")
let searchResults = document.querySelector("#search_results")
let titleSearch = document.querySelector("#id_title")
let ingredientSearch = document.querySelector("#id_ingredient")
let durationHoursSearch = document.querySelector("#id_duration_lt_hours")
let durationMinutesSearch = document.querySelector("#id_duration_lt_minutes")
let durationClearButton = document.querySelector(".clear_duration_search_button")
let tags = document.querySelectorAll('[id^=id_tag_]')
let tagExclusions = document.querySelectorAll('[id^=id_excluded_tag_]')
let tagDivs = document.querySelectorAll('.tag_check')
let standaloneRecipeInput = document.getElementById('id_is_component_recipe_0')
let componentRecipeInput = document.getElementById('id_is_component_recipe_1')

// These swap functions are defined in swap_cooking_baking.js
function swapCookingOrBakingSearch() {
    swapCookingOrBakingTags();
    stealthSubmit(); 
    swapCookingOrBakingColors(isBakingInput.checked);
}

swapCookingOrBakingTags()  // Run on page setup to set tags to cooking
swapCookingOrBakingColors(isBakingInput.checked) // Also set colors on page setup
isBakingInput.addEventListener('change', swapCookingOrBakingSearch)

function refreshTagResultCounts(tagResultsScript) {
    let tagResults = JSON.parse(tagResultsScript.textContent)
    let tagResultCounts = Object.fromEntries(
        tagResults.map(tag => [tag.name, tag.result_count])
    )
    let tagResultSpans = document.getElementsByClassName('result_count_label')
    Array.from(tagResultSpans).forEach(numSpan => {
        let resultTag = numSpan.getAttribute('data-tag_name')
        let count = tagResultCounts[resultTag]
        numSpan.innerHTML = count
        if (count == 0) {
            numSpan.style.display = 'none'
        } else {
            numSpan.style.display = ''
        }
    })
}
refreshTagResultCounts(tagResultsRaw)

async function stealthSubmit(e) {
    // An async 'form submission' rather than an actual form submission that loads
    // a new page. Retrieves results from the /search URL (this page's URL) with a
    // GET, then extracts HTML from the result and patches it onto the current page's
    // HTML, rather than actually moving to a new URL. It's pretty brute force but
    // hey, what are side projects for?

    let isBakingSearch = isBakingInput.checked
    let titleSearchValue = titleSearch.value
    let ingredientSearchValue = ingredientSearch.value
    let durationHoursSearchValue = parseInt(durationHoursSearch.value)
    let durationMinutesSearchValue = parseInt(durationMinutesSearch.value)
    let selectedTags = Array.from(tags)
        .filter(tag => tag.checked)
        .map(tag => tag.value)
    let excludedTags = Array.from(tagExclusions)
        .filter(tag => tag.checked)
        .map(tag => tag.value)
    let includeStandaloneRecipes = standaloneRecipeInput.checked
    let includeComponentRecipes = componentRecipeInput.checked

    // Calculate total duration in minutes
    let durationSearchValue
    if (durationHoursSearchValue || durationMinutesSearchValue) {
        if (isNaN(durationHoursSearchValue)) {
            durationHoursSearchValue = 0
        }
        if (isNaN(durationMinutesSearchValue)) {
            durationMinutesSearchValue = 0
        }
        durationSearchValue = parseInt(durationHoursSearchValue) * 60 + parseInt(durationMinutesSearchValue)
    } else {
        durationSearchValue = ''
    }

    let params = {
        title: titleSearchValue,
        ingredient: ingredientSearchValue,
        duration_lt: durationSearchValue,
        is_baking_recipe: isBakingSearch,
    }

    // Format params as URL query string
    let param_string = Object.entries(params)
        .map(([k, v]) => (`${k}=${v}`))
        .join('&')
    if (selectedTags.length > 0) {
        param_string += '&'
        param_string += Array.from(selectedTags)
            .map(tag => `tag=${tag.replace(' ', '+')}`)
            .join('&')
    }
    if (excludedTags.length > 0) {
        param_string += '&'
        param_string += Array.from(excludedTags)
            .map(tag => `tag_exclusion=${tag.replace(' ', '+')}`)
            .join('&')
    }
    if (includeStandaloneRecipes) {
        param_string += '&is_component_recipe=false'
    }
    if (includeComponentRecipes) {
        param_string += '&is_component_recipe=true'
    }

    console.log(`Performing GET with params: ${param_string}`)

    let response = await fetch(`/search?${param_string}`, {
        method: "GET",
    })
    .then(function(response) {
        // The response is a Response instance.
        return response.text();
    })
    
    // Render the response text as an html element, then extract the new search result div from its innards
    let responseHtml = document.createElement('html')
    responseHtml.innerHTML = response
    let responseSearchResults = responseHtml.querySelector('#search_results')

    // Frankenstein it right into our existing page
    searchResults.innerHTML = responseSearchResults.innerHTML

    // Update tag result counts
    refreshTagResultCounts(responseHtml.querySelector('#tagResultsRaw'))

    // This function is defined in search_sort.js
    addListenersToTableHeaders()

    // This function is defined in cart.js
    // For Font Awesome 6.x, wait until all <i> elements are replaced by SVGs before adding cart icon listeners.
    if (window.FontAwesome && window.FontAwesome.dom && typeof window.FontAwesome.dom.i2svg === 'function') {
        window.FontAwesome.dom.i2svg({ callback: addCartIconListeners });
    } else {
        // Fallback: if FontAwesome is not ready, listen for the i2svg event
        document.addEventListener('fa-i2svg-done', addCartIconListeners, { once: true });
    }
}

titleSearch.addEventListener("input", stealthSubmit);
ingredientSearch.addEventListener("input", stealthSubmit);
durationHoursSearch.addEventListener("input", stealthSubmit);
durationMinutesSearch.addEventListener("input", stealthSubmit);
tags.forEach(tag => tag.addEventListener("change", stealthSubmit));
tagExclusions.forEach(tag => tag.addEventListener("change", stealthSubmit));
tagDivs.forEach(div => div.addEventListener("click", function (event) {
    if (event.target.nodeName == 'DIV') {  // Don't trigger if clicking the input directly
        // Block the event from triggering multiple tags
        event.preventDefault();
        event.stopPropagation();
        console.log(event.target)
        let tag = div.querySelector('input[type=checkbox]')
        tag.checked = !tag.checked
        // Trigger the change event to update the search
        tag.dispatchEvent(new Event('change', { bubbles: true }))
    }
}));
standaloneRecipeInput.addEventListener("change", stealthSubmit);
componentRecipeInput.addEventListener("change", stealthSubmit);


function incrementHoursFromMinutes() {
    let hours = parseInt(durationHoursSearch.value)
    if (isNaN(hours)) {
        hours = 0
    }
    let minutes = parseInt(durationMinutesSearch.value)
    if (minutes >= 60) {
        durationHoursSearch.value = hours + 1
        durationMinutesSearch.value = minutes - 60
    } else if (minutes < 0) {
        durationHoursSearch.value = hours - 1
        durationMinutesSearch.value = minutes + 60
    }
    // Check if they entered a minute value that represented more than one hour, e.g. 150 minutes
    minutes = parseInt(durationMinutesSearch.value)
    if (minutes >= 60 || minutes < 0) {
        incrementHoursFromMinutes()
    }
}

durationMinutesSearch.addEventListener("blur", incrementHoursFromMinutes);

function clearDuration() {
    durationHoursSearch.value = ''
    durationMinutesSearch.value = ''
    stealthSubmit()
}

durationClearButton.addEventListener("click", clearDuration);