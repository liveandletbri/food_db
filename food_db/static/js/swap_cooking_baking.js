let isBakingInput = document.getElementById('cooking_baking_switch');
document.getElementById('baking_switch_label').style.display = 'inline-block'; // Make it visible on pages where this .js script is included

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
    let cookingColor =  window.getComputedStyle(root).getPropertyValue("--cooking-color")
    let bakingColor =  window.getComputedStyle(root).getPropertyValue("--baking-color")

    // Set the color to be mostly transparent, as is done for table row colors
    let rowColor = isBaking ? bakingColor : cookingColor
    rowColor = rowColor.replace('1)', '0.1)') // Set alpha to 0.1 for transparency
    root.style.setProperty("--table-row-color", rowColor);
}