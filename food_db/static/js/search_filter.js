let searchForm = document.querySelector("#search_form")
let searchResults = document.querySelector("#search_results")
let titleSearch = document.querySelector("#id_title")
let ingredientSearch = document.querySelector("#id_ingredient")
let tags = document.querySelectorAll('[id^=id_tag_]')

async function stealthSubmit(e) {
    // An async 'form submission' rather than an actual form submission that loads
    // a new page. Retrieves results from the /search URL (this page's URL) with a
    // GET, then extracts HTML from the result and patches it onto the current page's
    // HTML, rather than actually moving to a new URL. It's pretty brute force but
    // hey, what are side projects for?

    let titleSearchValue = titleSearch.value
    let ingredientSearchValue = ingredientSearch.value
    let selectedTags = Array.from(tags)
        .filter(tag => tag.checked)
        .map(tag => tag.value)

    let params = {
        title: titleSearchValue,
        ingredient: ingredientSearchValue,
    }

    // Format params as URL query string
    let param_string = Object.entries(params)
        .map(([k, v]) => (`${k}=${v}`))
        .join('&')
    param_string += '&'    
    param_string += Array.from(selectedTags)
        .map(tag => `tag=${tag.replace(' ', '+')}`)
        .join('&')

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
}

titleSearch.addEventListener("input", stealthSubmit);
ingredientSearch.addEventListener("input", stealthSubmit);
tags.forEach(tag => tag.addEventListener("change", stealthSubmit));