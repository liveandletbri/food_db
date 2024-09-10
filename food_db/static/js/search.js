let searchForm = document.querySelector("#search_form")
let searchResults = document.querySelector("#search_results")
let titleSearch = document.querySelector("#id_title")
let ingredientSearch = document.querySelector("#id_ingredient")
let tags = document.querySelectorAll('[id^=id_tag_]')

async function stealthSubmit(e) {
    // if(e && e.keyCode == 13) { // 13 is the enter key
    
    let titleSearchValue = titleSearch.value
    let ingredientSearchValue = ingredientSearch.value
    let selectedTags = Array.from(tags)
        .filter(tag => tag.checked)
        .map(tag => tag.value)

    let params = {
        title: titleSearchValue,
        ingredient: ingredientSearchValue,
    }
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
    
    let responseHtml = document.createElement('html')
    responseHtml.innerHTML = response
    
    let responseSearchResults = responseHtml.querySelector('#search_results')
    searchResults.innerHTML = responseSearchResults.innerHTML

    // e.currentTarget.focus()
}

titleSearch.addEventListener("input", stealthSubmit);
ingredientSearch.addEventListener("input", stealthSubmit);
tags.forEach(tag => tag.addEventListener("change", stealthSubmit));