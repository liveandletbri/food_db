// From https://www.brennantymrak.com/articles/django-dynamic-formsets-javascript and https://stackoverflow.com/questions/6142025/dynamically-add-field-to-a-form


let ingredTable = document.querySelector("#ingred-table")
let addIngredientButton = document.querySelector("#add-ingred-form")
let deleteIngredientButton = document.querySelector("#delete-ingred-form")

let extraIngredFormCountField = document.querySelector("#id_extra_ingred_count")
let extraIngredFormNum = Number(extraIngredFormCountField.value);

function addIngredientForm(e) {
    e.preventDefault()

    let newForm = ingredTable.rows[1].cloneNode(true) // Clone the ingredient form
    let formRegex = RegExp(`ingred_(\\d){1}`,'g') // Regex to find all instances of the form number

    extraIngredFormNum++ // Increment the form number
    newForm.innerHTML = newForm.innerHTML.replace(formRegex, `ingred_${extraIngredFormNum}`) //Update the new form to have the correct form number
    ingredTable.appendChild(newForm)

    extraIngredFormCountField.value = extraIngredFormNum // Increment the number of total forms in the management form
}

function removeBottomIngredientForm(e) {
    e.preventDefault()

    let lastRowNum = ingredTable.rows.length - 1
    ingredTable.deleteRow(lastRowNum)

    extraIngredFormNum--
    extraIngredFormCountField.value = extraIngredFormNum
}

addIngredientButton.addEventListener('click', addIngredientForm)
deleteIngredientButton.addEventListener('click', removeBottomIngredientForm)


// Same thing, but now Steps

let stepTable = document.querySelector("#step-table")
let addstepientButton = document.querySelector("#add-step-form")
let deletestepientButton = document.querySelector("#delete-step-form")

let extrastepFormCountField = document.querySelector("#id_extra_step_count")
let extrastepFormNum = Number(extrastepFormCountField.value);

function addstepientForm(e) {
    e.preventDefault()

    let newForm = stepTable.rows[0].cloneNode(true) // Clone the stepient form
    let formRegex = RegExp(`step_(\\d){1}`,'g') // Regex to find all instances of the form number

    extrastepFormNum++ // Increment the form number
    newForm.innerHTML = newForm.innerHTML.replace(formRegex, `step_${extrastepFormNum}`) //Update the new form to have the correct form number
    stepTable.appendChild(newForm)

    extrastepFormCountField.value = extrastepFormNum // Increment the number of total forms in the management form
}

function removeBottomstepientForm(e) {
    e.preventDefault()

    let lastRowNum = stepTable.rows.length - 1
    stepTable.deleteRow(lastRowNum)

    extrastepFormNum--
    extrastepFormCountField.value = extrastepFormNum
}

addstepientButton.addEventListener('click', addstepientForm)
deletestepientButton.addEventListener('click', removeBottomstepientForm)

