let ingredParserTextbox = document.querySelector("#ingred-parser-textbox")
let originalParserText = ingredParserTextbox.value;

function showIngredientParserOnClick(){
    document.getElementById('ingred-form').className="hide";
    document.getElementById('ingred-parser').className="show";
    document.getElementById('show_ingred_parse_button').className="hide";
}

async function hideIngredientParserOnClick(){
    let currentUrl = window.location.href
    let currentUrlDomain = currentUrl.split(":8000")[0]
    let response = await fetch(`${currentUrlDomain}:8000/ingred_parse`, {
        method: "POST",
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            text: ingredParserTextbox.value,
        })
    })
    .then(function(response) {
        // The response is a Response instance.
        return response.json()
    })

    console.log(response)

    let newIngredCountBaseZero = response.length - 1
    let currentIngredCountBaseZero = document.getElementById('id_extra_ingred_count').value

    document.getElementById('id_extra_ingred_count').value = newIngredCountBaseZero

    if (newIngredCountBaseZero > currentIngredCountBaseZero) {
        for (let i = currentIngredCountBaseZero; i < newIngredCountBaseZero; i++) {
            document.getElementById('add-ingred-form').click()
        }
    } else if (newIngredCountBaseZero < currentIngredCountBaseZero) {
        for (let i = currentIngredCountBaseZero; i > newIngredCountBaseZero; i--) {
            document.getElementById('delete-ingred-form').click()
        }
    }

    for (let i = 0; i <= newIngredCountBaseZero; i++) {
        console.log(response[i])
        document.getElementById(`id_ingred_${i}_quantity`).value = response[i].quantity
        document.getElementById(`id_ingred_${i}_unit_of_measurement`).value = response[i].unit_of_measurement
        document.getElementById(`id_ingred_${i}_food`).value = response[i].food
        document.getElementById(`id_ingred_${i}_notes`).value = response[i].notes
    }
    
    document.getElementById('ingred-form').className="show"
    document.getElementById('ingred-parser').className="hide"
    document.getElementById('show_ingred_parse_button').className="header_button";
}

function clearParserTextbox(e){
    if (ingredParserTextbox.className == "default_text") {
        ingredParserTextbox.value = originalParserText.replace(originalParserText, '')
        ingredParserTextbox.className = "modified"
        console.log("cleared")
    }
}

document.getElementById('ingred-parser-textbox').addEventListener("selectionchange", clearParserTextbox);