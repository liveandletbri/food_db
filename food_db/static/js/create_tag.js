let newTagInput = document.getElementById('id_new_tag');

function showTagForm(){
    document.getElementById('add-tag-form').className="show";
}
async function hideTagForm(){
    document.getElementById('add-tag-form').className="hide";

    let addTagSuccess = await fetch(`/add_tag/`, {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            tag_name: newTagInput.value,
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
        newTagInput.value = '';
        
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
        tagsTable.innerHTML = reponseTags.innerHTML
    }
}

const hideTagFormHandler = () => hideTagForm()

document.getElementById('add_tag_button').addEventListener('click', hideTagFormHandler)