let upvoteIconBefore = document.querySelector("i[id='cooked_recipe_upvote_icon_before']")
let upvoteIconClicked = document.querySelector("i[id='cooked_recipe_upvote_icon_clicked']")
let countLabel = document.querySelector("#cooked_count_label")

async function cookMeal(recipeTitle) {
    let upvoteSvgBefore = document.querySelector("svg#cooked_recipe_upvote_icon_before")
    let upvoteSvgClicked = document.querySelector("svg#cooked_recipe_upvote_icon_clicked")
    if ( !upvoteIconBefore.className.includes('after') ) {
        let currentUrl = window.location.href
        let currentUrlDomain = currentUrl.split("/recipe/")[0]
        let cookedMealResponse = await fetch(`${currentUrlDomain}/cook/`, {
            method: "POST",
            body: recipeTitle,
        })
        .then(function(response) {
            // The response is a Response instance.
            return response.text()
        })

        countLabel.textContent = `Cooked ${cookedMealResponse} time`
        if (cookedMealResponse != "1") {
            countLabel.textContent += 's'
        }

        upvoteIconBefore.className = "fa-solid fa-square-caret-up fa-2x after" 
        
        upvoteIconBefore.style.display = 'none'
        upvoteSvgBefore.innerHTML = upvoteSvgClicked.innerHTML.replace('clicked','before')
        upvoteSvgBefore.children[0].style.color = 'green'
    }       
}