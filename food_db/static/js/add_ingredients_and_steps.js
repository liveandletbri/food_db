// From https://www.brennantymrak.com/articles/django-dynamic-formsets-javascript and https://stackoverflow.com/questions/6142025/dynamically-add-field-to-a-form


let ingredTable = document.querySelector("#ingred-table")
let ingredTableBody = ingredTable.querySelector('tbody')
let addIngredientButton = document.querySelector("#add-ingred-form")
let deleteLastIngredientButton = document.querySelector("#delete-ingred-form")

let extraIngredRowCountField = document.querySelector("#id_extra_ingred_count")
let extraIngredRowNum = Number(extraIngredRowCountField.value);

function addListenersToRowButtons() {
    let deleteThisIngredientButtons = document.querySelectorAll(".delete_ingred_button")
    let deleteThisStepButtons = document.querySelectorAll(".delete_step_button")
    let parseThisStepButtons = document.querySelectorAll(".parse_step_button")

    deleteThisIngredientButtons.forEach(btn => btn.addEventListener('click', removeThisIngredientRow, btn))
    deleteThisStepButtons.forEach(btn => btn.addEventListener('click', removeThisStepRow, btn))
    parseThisStepButtons.forEach(btn => btn.addEventListener('click', parseThisStepRow, btn))
}

// Need to wait for "onload" to be after all the SVGs are rendered by Font Awesome magic
window.onload = function() {
    addListenersToRowButtons()
}

function getHighestIngredientNumber () {
    // Since you can delete and add rows in the middle of the table, we need to find the highest ingredient ID number and increment that for the new row
    let ingredTableArray = Array.from(ingredTable.rows) // convert HTMLCollection into Array, so we can...
    let ingredRows = ingredTableArray.slice(1) // Remove header row
    
    return Math.max(...
        ingredRows.map(row => row.querySelector("td:first-child > input").name) // iterate over ingredient rows and strip the name of each row
        .map(name =>  Number(name.replace('ingred_','').split('_')[0])) // strip number out of name
    )
}

function addIngredientRow(e, rowToInsertAfter = null) {
    e.preventDefault()

    let newRow = ingredTable.rows[1].cloneNode(true) // Clone the first ingredient row
    let idRegex = RegExp(`ingred_(\\d){1}`,'g') // Regex to find all instances of the ID number

    let highestRowNumber = getHighestIngredientNumber()
    let newRowNumber = highestRowNumber + 1
    
    newRow.innerHTML = newRow.innerHTML.replace(idRegex, `ingred_${newRowNumber}`) // Update the new row to have the correct row number
    newRow.setAttribute('name', `ingred_${newRowNumber}_row`)
    newRow.querySelectorAll('input').forEach(x => x.value = '') // Blank out text in new row

    // If specified, insert this row after another row. Otherwise, append to bottom
    let rowToInsertBefore
    if ( rowToInsertAfter == null ) {
        // set artificially high number as the row to insert before - it will just add to the end
        rowToInsertBefore = 999
    } else {
        rowToInsertBefore = rowToInsertAfter.rowIndex + 1
    }
    ingredTableBody.insertBefore(newRow, ingredTable.rows[rowToInsertBefore])

    // Increment the number of total rows in the hidden field
    extraIngredRowNum++
    extraIngredRowCountField.value = extraIngredRowNum 

    addListenersToRowButtons()
}

function removeBottomIngredientRow(e) {
    e.preventDefault()

    if (ingredTable.rows.length > 2) {
        let lastRowNum = ingredTable.rows.length - 1
        ingredTable.deleteRow(lastRowNum)

        extraIngredRowNum--
        extraIngredRowCountField.value = extraIngredRowNum
    }
}

function removeThisIngredientRow(e) {
    let row = e.currentTarget.closest('tr')
    ingredTableBody.removeChild(row)

    extraIngredRowNum--
    extraIngredRowCountField.value = extraIngredRowNum
}

addIngredientButton.addEventListener('click', addIngredientRow)
deleteLastIngredientButton.addEventListener('click', removeBottomIngredientRow)

// Same thing, but now Steps

let stepTable = document.querySelector("#step_table")
let stepTableBody = stepTable.querySelector('tbody')
let addStepButton = document.querySelector("#add-step-form")
let deleteLastStepButton = document.querySelector("#delete-step-form")

let extraStepRowCountField = document.querySelector("#id_extra_step_count")
let extraStepRowNum = Number(extraStepRowCountField.value);

function getHighestStepNumber () {
    // Since you can delete and add rows in the middle of the table, we need to find the highest step ID number and increment that for the new row
    return Math.max(...
        Array.from(stepTable.rows, // convert HTMLCollection into Array, so we can...
        (row) => row.querySelector("td:first-child > textarea").name) // iterate over it and strip the name of each row
        .map(name =>  Number(name.replace('step_','').split('_')[0])) // strip number out of name
    )
}

function addStepRow(e, rowToInsertAfter = null) {
    e.preventDefault()

    let newRow = stepTable.rows[0].cloneNode(true) // Clone the first step row
    let idRegex = RegExp(`step_(\\d){1}`,'g') // Regex to find all instances of the ID number

    let highestRowNumber = getHighestStepNumber()
    let newRowNumber = highestRowNumber + 1
    
    newRow.innerHTML = newRow.innerHTML.replace(idRegex, `step_${newRowNumber}`) // Update the new row to have the correct row number
    newRow.setAttribute('name', `step_${newRowNumber}_row`)
    newRow.querySelector('textarea').textContent = '' // Blank out text in new row's HTML
    newRow.querySelector('textarea').value = '' // Blank out text in new row

    // If specified, insert this row after another row. Otherwise, append to bottom
    let rowToInsertBefore
    if ( rowToInsertAfter == null ) {
        // set artificially high number as the row to insert before - it will just add to the end
        rowToInsertBefore = 999
    } else {
        rowToInsertBefore = rowToInsertAfter.rowIndex + 1
    }
    stepTableBody.insertBefore(newRow, stepTable.rows[rowToInsertBefore])

    // Increment the number of total rows in the hidden field
    extraStepRowNum++
    extraStepRowCountField.value = extraStepRowNum

    addListenersToRowButtons() 
}

function removeBottomStepRow(e) {
    e.preventDefault()

    if (stepTable.rows.length > 1) {
        let lastRowNum = stepTable.rows.length - 1
        stepTable.deleteRow(lastRowNum)

        extraStepRowNum--
        extraStepRowCountField.value = extraStepRowNum
    }
}

function removeThisStepRow(e) {
    let row = e.currentTarget.closest('tr')
    stepTableBody.removeChild(row)

    extraStepRowNum--
    extraStepRowCountField.value = extraStepRowNum
}

function parseThisStepRow(e) {
    let row = e.currentTarget.closest('tr')
    let rawText = row.querySelector('textarea').value
    let parsedText = rawText.split(/(\n)(\d\.)*/gm)
        .filter(chunk => chunk) // remove undefined
        .filter(chunk => !chunk.match(/^\s+$/)) // remove chunks that are just white space
        .filter(chunk => !chunk.match(/^\d\.$/)) // remove chunks that are just a number and period
        .map(chunk => chunk.trim())
        .map(chunk => chunk.replace(/^\d\./,''))
    let numberNewSteps = parsedText.length - 1
    
    // create new steps and set their values to the parsed text chunks
    for(let i = 0; i < numberNewSteps; i++){ // Note the less than - it will insert exactly numberNewSteps rows
        addStepRow(e, rowToInsertAfter=stepTable.rows[row.rowIndex])
    }
    for(let i = 0; i <= numberNewSteps; i++){ // Less than or equal - this runs one more time to account for the original row that we are keeping
        let rowNumber = i + row.rowIndex
        stepTable.rows[rowNumber].querySelector('textarea').value = parsedText[i]
    }
}

addStepButton.addEventListener('click', addStepRow)
deleteLastStepButton.addEventListener('click', removeBottomStepRow)
