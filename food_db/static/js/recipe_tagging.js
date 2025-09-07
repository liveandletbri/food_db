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

    let addTagSuccess = await fetch(`/add_tag/`, {
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
        
        let pageResponse = await fetch(`/add/`, {
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
// Also set the colors on page load
swapCookingOrBakingColors(isBakingInput.checked)

// Also filter it on change of the is_baking_recipe checkbox
isBakingInput.addEventListener('change', function() {
    swapCookingOrBakingTags(document.getElementById('tags_table'))
    swapCookingOrBakingColors(isBakingInput.checked)
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
tagDivs.forEach(div => div.addEventListener("click", function (event) {
    if (event.target.nodeName == 'DIV') {  // Don't trigger if clicking the input directly
        // Block the event from triggering multiple tags
        event.preventDefault();
        event.stopPropagation();
        console.log(event.target)
        let tag = div.querySelector('input[type=checkbox]')
        tag.checked = !tag.checked
        // Trigger the change event to update the search
        tag.dispatchEvent(new Event('change', { bubbles: true }))
    }
}));