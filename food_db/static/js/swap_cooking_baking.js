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

// Global object to store original position data for tr elements
let trRestoreInfo = new Map();

function hideSpecificElements() {
    let hideIfBakingElements = document.querySelectorAll('.hide_if_baking');
    let hideIfCookingElements = document.querySelectorAll('.hide_if_cooking');

    // Helper for tr removal & tracking
    function handleTrs(elements, shouldHide) {
        elements.forEach(elem => {
            if (elem.tagName === 'TR') {
                if (shouldHide) {
                    // Track where to put back if not already tracked & remove from DOM
                    if (!trRestoreInfo.has(elem)) {
                        let parent = elem.parentNode;
                        if (parent) {
                            // Find next sibling in DOM (could be null)
                            let nextSibling = elem.nextSibling;
                            trRestoreInfo.set(elem, {
                                parent: parent,
                                nextSibling: nextSibling
                            });
                            parent.removeChild(elem);
                        }
                    }
                } else {
                    // Restore to its original position if not present and was tracked
                    if (trRestoreInfo.has(elem)) {
                        let { parent, nextSibling } = trRestoreInfo.get(elem);
                        // Only re-append if it's not currently in the tree
                        if (!parent.contains(elem)) {
                            if (nextSibling && parent.contains(nextSibling)) {
                                parent.insertBefore(elem, nextSibling);
                            } else {
                                parent.appendChild(elem);
                            }
                        }
                        trRestoreInfo.delete(elem);
                    }
                }
            } else {
                elem.style.display = shouldHide ? 'none' : '';
            }
        });
    }

    // Restore any removed TRs that match the given CSS class
    function restoreTrsByClass(className) {
        // Copy entries array to avoid mutation issues while deleting
        let entries = Array.from(trRestoreInfo.entries());
        for (let [elem, info] of entries) {
            if (elem.tagName === 'TR' && elem.classList && elem.classList.contains(className)) {
                let parent = info.parent;
                let nextSibling = info.nextSibling;
                if (!parent.contains(elem)) {
                    if (nextSibling && parent.contains(nextSibling)) {
                        parent.insertBefore(elem, nextSibling);
                    } else {
                        parent.appendChild(elem);
                    }
                }
                trRestoreInfo.delete(elem);
            }
        }
    }

    if (isBakingInput.checked) {
        handleTrs(hideIfBakingElements, true);
        handleTrs(hideIfCookingElements, false);
        restoreTrsByClass('hide_if_cooking');
    } else {
        handleTrs(hideIfBakingElements, false);
        handleTrs(hideIfCookingElements, true);
        restoreTrsByClass('hide_if_baking');
    }
}

async function swapBakingMode() {
    swapCookingOrBakingColors(isBakingInput.checked)
    hideSpecificElements()
    await updateBakingModeCookie()
}

let swapBakingModeHandler = () => swapBakingMode()

isBakingInput.addEventListener('change', swapBakingModeHandler);
// Set the colors on page load
swapCookingOrBakingColors(isBakingInput.checked)
hideSpecificElements()