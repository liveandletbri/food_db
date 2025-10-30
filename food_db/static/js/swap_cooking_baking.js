let isBakingInput = document.getElementById('cooking_baking_switch');
document.getElementById('baking_switch_label').style.display = 'inline-block'; // The switch is hidden by default. Make it visible on pages where this .js script is included

function swapCookingOrBakingTags(element) {
    if ( element == undefined ) {
        element = document
    }
    let isBakingSearch = isBakingInput.checked
    let tagDivs = element.querySelectorAll('.tag_check')
    for (let div of tagDivs) {
        let isCookingTag = div.getAttribute('data-is_cooking_tag') == 'True'
        let isBakingTag = div.getAttribute('data-is_baking_tag') == 'True'
        let tag = div.querySelector('input[type=checkbox]')

        if ( isBakingSearch && ! isBakingTag ) {
            div.style.display = 'none'
            tag.checked = false
        } else if ( ! isBakingSearch && ! isCookingTag ) {
            div.style.display = 'none'
            tag.checked = false
        } else {
            div.style.display = 'block'
        }
    }
    return element
}

function swapCookingOrBakingColors(isBaking) {
    let root = document.documentElement
    let cookingColor =  window.getComputedStyle(root).getPropertyValue("--cooking-row-color")
    let bakingColor =  window.getComputedStyle(root).getPropertyValue("--baking-row-color")

    // Set the color to be mostly transparent, as is done for table row colors
    let rowColor = isBaking ? bakingColor : cookingColor
    root.style.setProperty("--table-row-color", rowColor);
}

async function updateBakingModeCookie() {
    let cookieUpdateSuccess = await fetch(`/edit_baking_switch_cookie/`, {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            is_baking_mode: isBakingInput.checked,
        })
    })
    .then(function(response) {
        if (response.status == 200) {
            return true
        } else {
            return false
        }
    })
    console.log(`Baking mode cookie updated: ${cookieUpdateSuccess ? 'success' : 'failure'}`)
}

async function swapBakingMode() {
    swapCookingOrBakingColors(isBakingInput.checked)
    await updateBakingModeCookie()
}

let swapBakingModeHandler = () => swapBakingMode()

isBakingInput.addEventListener('change', swapBakingModeHandler);
// Set the colors on page load
swapCookingOrBakingColors(isBakingInput.checked)