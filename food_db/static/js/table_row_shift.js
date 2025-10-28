// Generic functions for moving table rows up and down
// Parameters:
// - rowSelector: CSS selector for the rows that can be moved
// - containerSelector: CSS selector for the container holding the rows

function initializeRowShiftFunctionality(rowSelector, containerSelector) {
    let container = document.querySelector(containerSelector);
    if (!container) {
        console.error(`Container not found: ${containerSelector}`);
        return;
    }

    // Add event listeners to existing buttons within the container
    let upButtons = container.querySelectorAll('.move_row_up_button');
    let downButtons = container.querySelectorAll('.move_row_down_button');
    let deleteButtons = container.querySelectorAll('.delete_row_button');
    
    upButtons.forEach(btn => btn.addEventListener('click', function(e) {
        moveRow(e, rowSelector, containerSelector, 'up');
    }));
    
    downButtons.forEach(btn => btn.addEventListener('click', function(e) {
        moveRow(e, rowSelector, containerSelector, 'down');
    }));

    if ( deleteButtons ) {
    
        deleteButtons.forEach(btn => btn.addEventListener('click', function(e) {
            deleteRow(e, rowSelector);
        }));
    }
    
    // Initial call to hide top/bottom buttons
    hideTopAndBottomButtons(rowSelector);
}

function hideTopAndBottomButtons(rowSelector) {
    let allRows = document.querySelectorAll(rowSelector);
    allRows = Array.from(allRows).filter(row => !row.classList.contains('ignore_row'));
    let firstRow = allRows[0];
    let lastRow = allRows[allRows.length - 1];

    allRows.forEach(row => {
        let upButton = row.querySelector('.move_row_up_button');
        let downButton = row.querySelector('.move_row_down_button');
        
        if (upButton) {
            if (row == firstRow) {
                upButton.style.display = 'none';
            } else {
                upButton.style.display = '';
            }
        }
        
        if (downButton) {
            if (row == lastRow) {
                downButton.style.display = 'none';
            } else {
                downButton.style.display = '';
            }
        }
    });
}

function moveRow(e, rowSelector, containerSelector, direction) {
    let element = e.target;
    let buttonElement;
    
    // Find the button element - could be clicked directly or could be a child element
    if (element.classList && (element.classList.contains('move_row_up_button') || 
        element.classList.contains('move_row_down_button'))) {
        buttonElement = element;
    } else if (element.nodeName == 'path' || element.nodeName == 'i' || element.nodeName == 'svg') {
        // If clicking on an icon child (path or the i tag itself), get the closest button
        buttonElement = element.closest('.move_row_up_button') || element.closest('.move_row_down_button');
    } else {
        console.error('Could not determine button element', element);
        return;
    }
    
    let row = buttonElement.closest(rowSelector);
    let container = document.querySelector(containerSelector);
    
    if (!row || !container) {
        console.error('Row or container not found');
        return;
    }
    
    if (direction == 'up') {
        container.insertBefore(row, row.previousElementSibling);
    } else if (direction == 'down') {
        container.insertBefore(row.nextElementSibling, row);
    }
    
    hideTopAndBottomButtons(rowSelector);
}

function deleteRow(e, rowSelector) {
    let element = e.target;
    let buttonElement;
    
    // Find the delete button - could be clicked directly or could be a child element
    if (element.classList && element.classList.contains('delete_row_button')) {
        buttonElement = element;
    } else if (element.nodeName == 'IMG') {
        buttonElement = element;
    } else if (element.nodeName == 'PATH' || element.nodeName == 'I' || element.nodeName == 'svg') {
        // If clicking on an icon child (path or the i tag itself), get the closest button
        buttonElement = element.closest('.delete_row_button');
    } else {
        console.error('Could not determine delete button element', element);
        return;
    }
    
    let row = buttonElement.closest(rowSelector);
    
    if (!row) {
        console.error('Row not found');
        return;
    }
    
    row.remove();
    hideTopAndBottomButtons(rowSelector);
}