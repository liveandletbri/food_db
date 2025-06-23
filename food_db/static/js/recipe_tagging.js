let newTagName = document.getElementById('id_new_tag');
let isBakingRecipeInput = document.getElementById('id_is_baking_recipe');
let isCookingTagInput = document.getElementById('id_is_cooking_tag');
let isBakingTagInput = document.getElementById('id_is_baking_tag');
let cookingOrBakingTooltip = document.getElementById('cooking_or_baking_tag_tooltip');

function filterTagsTable(tagsTable) {
    let isBakingRecipe = isBakingRecipeInput.checked
    let tagDivs = tagsTable.querySelectorAll('.tag_check')
    for (let tag of tagDivs) {
        let isCookingTag = tag.getAttribute('data-is_cooking_tag') == 'True'
        let isBakingTag = tag.getAttribute('data-is_baking_tag') == 'True'

        if ( isBakingRecipe && ! isBakingTag ) {
            tag.style.display = 'none'
        } else if ( ! isBakingRecipe && ! isCookingTag ) {
            tag.style.display = 'none'
        } else {
            tag.style.display = 'block'
        }
    }
    return tagsTable
}

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
        let reponseTags = responseHtml.querySelector('#tags_table');
        let tagsTable = document.getElementById('tags_table')

        // Frankenstein it right into our existing page
        tagsTable.innerHTML = filterTagsTable(reponseTags.innerHTML)
    }
}

const submitAndHideTagFormHandler = () => submitAndHideTagForm()

document.getElementById('add_tag_button').addEventListener('click', submitAndHideTagFormHandler)

// Filter the table on page load
filterTagsTable(document.getElementById('tags_table'))

// Also filter it on change of the is_baking_recipe checkbox
isBakingRecipeInput.addEventListener('change', function() {
    filterTagsTable(document.getElementById('tags_table'))
})