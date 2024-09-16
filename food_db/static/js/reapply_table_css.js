function reapplyEveryOtherRowCss (tableId) {
    if (tableId == null || tableId == undefined) { 
        throw new Error('Invalid tableId') 
    }
    let table = document.querySelector(`table#${tableId}`)
    if (table == null || table == undefined) { 
        throw new Error(`Couldn't find table with id ${tableId}`) 
    }
    for (var i = 0; i < table.rows.length; i++) {
        if (i % 2 == 1) { // odd-numbered rows
            table.rows[i].style.backgroundColor = "#0000000d"  // this matches the value in story.css, defined for table tbody tr:nth-child(2n + 1), which is currently rgba(0, 0, 0, 0.05)
        } else {
            table.rows[i].style.backgroundColor = "#00000000"  
        }
    }
}