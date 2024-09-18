let urlInput = document.querySelector("#id_url")

async function parseFromCookedWiki() {
    let url = urlInput.textContent
    let responseBody = await fetch(`http://cooked.wiki/${url}`, {
        method: "GET",
        headers: {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PATCH, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token',
        }
    })
    .then(function(response) {
        // The response is a Response instance.
        return response.text()
    })

    // Render entire cooked.wiki page as ResponseHtml element in here, then extract ingreds and steps
    let responseHtml = document.createElement('html')
    responseHtml.innerHTML = responseBody

    let  
}

window.onload = function() {
    let parseUrlButton = document.querySelector(".parse_url_button")
    parseUrlButton.addEventListener('click', parseFromCookedWiki)
}