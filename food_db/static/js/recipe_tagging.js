let newTagName = document.getElementById('id_new_tag');
let isCookingTagInput = document.getElementById('id_is_cooking_tag');
let isBakingTagInput = document.getElementById('id_is_baking_tag');
let cookingOrBakingTooltip = document.getElementById('cooking_or_baking_tag_tooltip');
let tags = document.querySelectorAll('[id^=id_tag_]')
let tagDivs = document.querySelectorAll('.tag_check')

let testTagFillColorChooser = document.getElementById('tag_fill_color_chooser');
let testTagBorderCheckbox = document.getElementById('tag_border_checkbox');
let testTagBorderColorChooser = document.getElementById('tag_border_color_chooser');
let testTagTextColorChooser = document.getElementById('tag_text_color_chooser');
let testTag = document.getElementById('test_tag');

function showTagForm(){
    document.getElementById('add-tag-form').className="show";
}
async function submitAndHideTagForm(){
    let isCookingTag = isCookingTagInput.checked
    let isBakingTag = isBakingTagInput.checked

    if ( ! isCookingTag && ! isBakingTag ) {
        showAndHideTooltip(cookingOrBakingTooltip)
        return
    }
    
    document.getElementById('add-tag-form').className="hide";

    let addTagSuccess = await fetchWithTestDb(`/add_tag/`, {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            tag_name: newTagName.value,
            is_cooking_tag: isCookingTag,
            is_baking_tag: isBakingTag,
            fill_color: testTagFillColorChooser.value,
            text_color: testTagTextColorChooser.value,
            border_color: testTagBorderColorChooser.value,
            has_border: testTagBorderCheckbox.checked,
        })
    })
    .then(function(response) {
        if (response.status == 200) {
            return true
        } else {
            return false
        }
    })

    if ( addTagSuccess ) {
        newTagName.value = '';
        
        let pageResponse = await fetchWithTestDb(`/add/`, {
            method: "GET",
        })
        .then(function(response) {
            return response.text();
        })
        
        // Render the response text as an html element, then extract the new search result div from its innards
        let responseHtml = document.createElement('html');
        responseHtml.innerHTML = pageResponse;
        let responseTags = responseHtml.querySelector('#tags_table');
        let tagsTable = document.getElementById('tags_table')

        // Frankenstein it right into our existing page, using swapCookingOrBakingTags from swap_cooking_baking.js
        tagsTable.innerHTML = swapCookingOrBakingTags(responseTags).innerHTML
    }
}

const submitAndHideTagFormHandler = () => submitAndHideTagForm()

document.getElementById('add_tag_button').addEventListener('click', submitAndHideTagFormHandler)

// Filter the table on page load
swapCookingOrBakingTags(document.getElementById('tags_table'))

// Also filter it on change of the is_baking_recipe checkbox
isBakingInput.addEventListener('change', function() {
    swapCookingOrBakingTags(document.getElementById('tags_table'))
    isCookingTagInput.checked = ! isBakingInput.checked
    isBakingTagInput.checked = isBakingInput.checked
})

// Also do this on page load
isCookingTagInput.checked = ! isBakingInput.checked
isBakingTagInput.checked = isBakingInput.checked

function updateTestTag() {
    if (newTagName.value.length > 0) {
        testTag.innerText = newTagName.value;
    } else {
        testTag.innerText = 'Test';
    }
    testTag.style.backgroundColor = testTagFillColorChooser.value;
    testTag.style.outline = `2px solid ${testTagBorderColorChooser.value}`;
    testTag.style.outlineStyle = testTagBorderCheckbox.checked ? 'solid' : 'none';
    testTag.style.color = testTagTextColorChooser.value;
}

newTagName.addEventListener('input', updateTestTag);
testTagFillColorChooser.addEventListener('change', updateTestTag);
testTagBorderCheckbox.addEventListener('change', updateTestTag);
testTagBorderColorChooser.addEventListener('change', updateTestTag);
testTagTextColorChooser.addEventListener('change', updateTestTag);

// Event listeners for checking the individual tags
tags.forEach(tag => tag.addEventListener("change", function (event){
    tag.checked = !tag.checked
}));

// Prevent clicks on empty space from triggering the first checkbox (Firefox issue)
// Handle clicks on the outer label that wraps the ul
let tagsRowLabels = document.querySelectorAll('label.tags_row')
tagsRowLabels.forEach(label => {
    label.addEventListener("click", function (event) {
        // If clicking directly on the label itself (not on its children), prevent default
        // to stop Firefox from triggering the first checkbox
        if (event.target === label) {
            event.preventDefault();
            event.stopPropagation();
        }
    })
})

// Also handle clicks on the ul element itself (empty space between checkboxes)
let tagsUlElements = document.querySelectorAll('label.tags_row > ul')
tagsUlElements.forEach(ul => {
    ul.addEventListener("click", function (event) {
        // If clicking directly on the ul (empty space), stop propagation to prevent Firefox
        // from triggering the first checkbox via the outer label
        if (event.target === ul) {
            event.preventDefault();
            event.stopPropagation();
        }
    })
})

tagDivs.forEach(div => div.addEventListener("click", function (event) {
    // Only handle clicks that are directly on the div, label, or input within this div
    // Don't handle clicks on empty space in the ul
    let clickedElement = event.target
    let isClickOnDiv = clickedElement === div
    let isClickOnLabel = clickedElement.nodeName === 'LABEL' && div.contains(clickedElement)
    
    // If clicking directly on the input, let the browser handle it naturally
    if (clickedElement.nodeName === 'INPUT' && clickedElement.type === 'checkbox') {
        return
    }
    
    // Only proceed if clicking on the div or its label (not empty space)
    if (isClickOnDiv || isClickOnLabel) {
        // Block the event from triggering multiple tags
        event.preventDefault();
        event.stopPropagation();
        let tag = div.querySelector('input[type=checkbox]')
        if (tag) {
            tag.checked = !tag.checked
            // Trigger the change event to update the search
            tag.dispatchEvent(new Event('change', { bubbles: true }))
        }
    }
}));