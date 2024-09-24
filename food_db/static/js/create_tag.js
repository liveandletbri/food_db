function showTagFormOnClick(){
    document.getElementById('add-tag-form').className="show";
}
function hideTagFormOnClick(){
    document.getElementById('add-tag-form').className="hide";
    // form declared in recipe_add_form_validate.js
    form.submit()
}

document.getElementById('add_tag_button').addEventListener('click', hideTagFormOnClick)