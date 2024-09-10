let multiplierInput = document.querySelector("#ingredient_multiplier")

function multiplyIngredients(e) {
    let currentUrl = window.location.href
    let currentUrlNoParams = currentUrl.split("?")[0]
    window.open(`${currentUrlNoParams}?multiplier=${multiplierInput.value}`, "_self")
    multiplierInput.focus()
}

multiplierInput.addEventListener("focusout", multiplyIngredients)