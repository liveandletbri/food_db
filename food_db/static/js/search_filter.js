let searchForm = document.querySelector("#search_form")
let searchResults = document.querySelector("#search_results")
let titleSearch = document.querySelector("#id_title")
let ingredientSearch = document.querySelector("#id_ingredient")
let durationHoursSearch = document.querySelector("#id_duration_lt_hours")
let durationMinutesSearch = document.querySelector("#id_duration_lt_minutes")
let durationClearButton = document.querySelector(".clear_duration_search_button")
let tags = document.querySelectorAll('[id^=id_tag_]')
let tagExclusions = document.querySelectorAll('[id^=id_excluded_tag_]')
let isBakingSearchInput = document.getElementById('id_baking_tags_check')

// These swap functions are defined in swap_cooking_baking.js
function swapCookingOrBakingSearch() {
    stealthSubmit(); 
    swapCookingOrBakingTags(isBakingSearchInput);
    swapCookingOrBakingColors(isBakingSearchInput);
}

swapCookingOrBakingTags(isBakingSearchInput)  // Run on page setup to set tags to cooking
swapCookingOrBakingColors(isBakingSearchInput) // Also set colors on page setup
isBakingSearchInput.addEventListener('change', swapCookingOrBakingSearch)

async function stealthSubmit(e) {
    // An async 'form submission' rather than an actual form submission that loads
    // a new page. Retrieves results from the /search URL (this page's URL) with a
    // GET, then extracts HTML from the result and patches it onto the current page's
    // HTML, rather than actually moving to a new URL. It's pretty brute force but
    // hey, what are side projects for?

    let isBakingSearch = isBakingSearchInput.checked
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

    // This function is defined in search_sort.js
    addListenersToTableHeaders()
}

titleSearch.addEventListener("input", stealthSubmit);
ingredientSearch.addEventListener("input", stealthSubmit);
durationHoursSearch.addEventListener("input", stealthSubmit);
durationMinutesSearch.addEventListener("input", stealthSubmit);
tags.forEach(tag => tag.addEventListener("change", stealthSubmit));
tagExclusions.forEach(tag => tag.addEventListener("change", stealthSubmit));

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