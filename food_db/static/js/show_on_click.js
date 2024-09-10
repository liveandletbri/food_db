let ingredParserTextbox = document.querySelector("#ingred-parser-textbox")

function showTagFormOnClick(){
    document.getElementById('add-tag-form').className="show";
}
function hideTagFormOnClick(){
    document.getElementById('add-tag-form').className="hide";
}

function showIngredientParserOnClick(){
    document.getElementById('ingred-form').className="hide";
    document.getElementById('ingred-parser').className="show";
}
async function hideIngredientParserOnClick(){
    let response = await fetch(`http://localhost:5000/parse`, {
        method: "POST",
        body: ingredParserTextbox.value,
    })
    .then(function(response) {
        // The response is a Response instance.
        return response.json()
    })

    console.log(response)
    
    // document.getElementById('ingred-form').className="show";
    // document.getElementById('ingred-parser').className="hide";
}