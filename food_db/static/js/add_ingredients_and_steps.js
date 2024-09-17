// From https://www.brennantymrak.com/articles/django-dynamic-formsets-javascript and https://stackoverflow.com/questions/6142025/dynamically-add-field-to-a-form


let ingredTable = document.querySelector("#ingred-table")
let ingredTableBody = ingredTable.querySelector('tbody')
let addIngredientButton = document.querySelector("#add-ingred-form")
let deleteLastIngredientButton = document.querySelector("#delete-ingred-form")
let deleteThisIngredientButtons = document.querySelectorAll(".delete_ingred_button")

let extraIngredRowCountField = document.querySelector("#id_extra_ingred_count")
let extraIngredRowNum = Number(extraIngredRowCountField.value);

function addListenersToRowButtons() {
    let deleteThisIngredientButtons = document.querySelectorAll(".delete_ingred_button")
    let deleteThisStepButtons = document.querySelectorAll(".delete_step_button")

    deleteThisIngredientButtons.forEach(btn => btn.addEventListener('click', removeThisIngredientRow, btn))
    deleteThisStepButtons.forEach(btn => btn.addEventListener('click', removeThisStepRow, btn))
}

addListenersToRowButtons()

function addIngredientRow(e) {
    e.preventDefault()

    let newRow = ingredTable.rows[1].cloneNode(true) // Clone the first ingredient row
    let idRegex = RegExp(`ingred_(\\d){1}`,'g') // Regex to find all instances of the ID number

    // Since you can delete rows from the middle, we need to find the last ingredient ID number and increment that for the new row
    let lastRow = ingredTable.rows[ingredTable.rows.length - 1]
    let lastRowFirstInputName = lastRow.querySelector("td:first-child > input").name
    let lastRowNumber = Number(lastRowFirstInputName.replace('ingred_','').split('_')[0])
    let newRowNumber = lastRowNumber + 1
    
    newRow.innerHTML = newRow.innerHTML.replace(idRegex, `ingred_${newRowNumber}`) // Update the new row to have the correct row number
    ingredTableBody.appendChild(newRow)

    // Increment the number of total rows in the hidden field
    extraIngredRowNum++
    extraIngredRowCountField.value = extraIngredRowNum 

    addListenersToRowButtons()
}

function removeBottomIngredientRow(e) {
    e.preventDefault()

    let lastRowNum = ingredTable.rows.length - 1
    ingredTable.deleteRow(lastRowNum)

    extraIngredRowNum--
    extraIngredRowCountField.value = extraIngredRowNum
}

function removeThisIngredientRow(e) {
    let row = e.currentTarget.closest('tr')
    ingredTableBody.removeChild(row)

    extraIngredRowNum--
    extraIngredRowCountField.value = extraIngredRowNum
}

addIngredientButton.addEventListener('click', addIngredientRow)
deleteLastIngredientButton.addEventListener('click', removeBottomIngredientRow)
deleteThisIngredientButtons.forEach(btn => btn.addEventListener('click', removeThisIngredientRow, btn))

// Same thing, but now Steps

let stepTable = document.querySelector("#step_table")
let stepTableBody = stepTable.querySelector('tbody')
let addStepButton = document.querySelector("#add-step-form")
let deleteLastStepButton = document.querySelector("#delete-step-form")

let extraStepRowCountField = document.querySelector("#id_extra_step_count")
let extraStepRowNum = Number(extraStepRowCountField.value);

function addStepRow(e) {
    e.preventDefault()

    let newRow = stepTable.rows[0].cloneNode(true) // Clone the first step row
    let idRegex = RegExp(`step_(\\d){1}`,'g') // Regex to find all instances of the ID number

    // Since you can delete rows from the middle, we need to find the last step ID number and increment that for the new row
    let lastRow = stepTable.rows[stepTable.rows.length - 1]
    let lastRowFirstInputName = lastRow.querySelector("td:first-child > textarea").name
    let lastRowNumber = Number(lastRowFirstInputName.replace('step_','').split('_')[0])
    let newRowNumber = lastRowNumber + 1
    
    newRow.innerHTML = newRow.innerHTML.replace(idRegex, `step_${newRowNumber}`) // Update the new row to have the correct row number
    stepTableBody.appendChild(newRow)

    // Increment the number of total rows in the hidden field
    extraStepRowNum++
    extraStepRowCountField.value = extraStepRowNum

    addListenersToRowButtons() 
}

function removeBottomStepRow(e) {
    e.preventDefault()

    let lastRowNum = stepTable.rows.length - 1
    stepTable.deleteRow(lastRowNum)

    extraStepRowNum--
    extraStepRowCountField.value = extraStepRowNum
}

function removeThisStepRow(e) {
    let row = e.currentTarget.closest('tr')
    stepTableBody.removeChild(row)

    extraStepRowNum--
    extraStepRowCountField.value = extraStepRowNum
}

addStepButton.addEventListener('click', addStepRow)
deleteLastStepButton.addEventListener('click', removeBottomStepRow)
