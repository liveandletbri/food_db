// Tab switching functionality
let activeTab = 'prep';

function showHideTabs(){   
    // on page load, show first tab and hide the other
    $('#tabs li a:not(:first)').addClass('inactive');
    $('.tab_container').hide();
    $('.tab_container:first').show();
    activeTab = 'prep'  // prep tab is the first tab
    
    // actions when a tab is clicked
    $('#tabs li a').click(function() {
        let thisTabId = $(this).attr('id');

        // if the tab was inactive, make it active and hide the old tab
        if($(this).hasClass('inactive')){ 
            // perform the tab swap
            $('#tabs li a').addClass('inactive');           
            $(this).removeClass('inactive');
            
            $('.tab_container').hide();
            $('#'+ thisTabId + '_content').fadeIn('slow');
            
            // set the new "active tab" to be this tab
            if (thisTabId === 'prep_tab') {
                activeTab = 'prep'
            } else if (thisTabId === 'view_config_tab') {
                activeTab = 'view_config'
            }
        }
    });
}

// Initialize row shift functionality for timing table
window.addEventListener('load', function() {
    initializeRowShiftFunctionality('.attribute_matrix_table_row', '#attribute_matrix_table tbody');
});

// Add extra event to listeners for column sorts (column sorting defined in table_sort.js)
// As long as this event listener as registered last (after the event listeners in table_sort.js), it should happen after the rows are sorted
const timingTableHideButtonsHandler = () => hideTopAndBottomButtons('.attribute_matrix_table_row');
document.querySelectorAll('th').forEach(th => th.addEventListener('click', timingTableHideButtonsHandler))

// Initialize tabs when document is ready
$(document).ready(showHideTabs)

// View Config form validation
let submitViewConfigButton = document.querySelector("#submit_view_config_button")
let viewConfigForm = document.querySelector("#view_config_form")
let viewConfigNameInput = document.querySelector("#view_config_name")
let editViewConfigKeyInput = document.querySelector("#edit_view_config_key")
let viewConfigFormSummary = document.querySelector("#view_config_form_summary")

let viewConfigNameTooltip = document.querySelector("#view_config_name_tooltip")
let viewConfigTagsTooltip = document.querySelector("#view_config_tags_tooltip")
let viewConfigAttributesTooltip = document.querySelector("#view_config_attributes_tooltip")

// Variable to store the current editing key
let currentEditingKey = null

function validateViewConfig(e) {
    e.preventDefault()
    
    let invalid = false
    
    // Get current form values
    let name = viewConfigNameInput.value.trim()
    let selectedTags = document.querySelectorAll('input[name="tags"]:checked')
    let selectedAttributes = document.querySelectorAll('input[name="recipe_attributes"]:checked')
    
    // Name must be filled out
    if (name === '' || name.toLowerCase() === 'default') {
        showAndHideTooltip(viewConfigNameTooltip)
        invalid = true
    }
    
    // At least one tag must be checked
    if (selectedTags.length === 0) {
        showAndHideTooltip(viewConfigTagsTooltip)
        invalid = true
    }
    
    // At least one recipe attribute must be checked
    if (selectedAttributes.length === 0) {
        showAndHideTooltip(viewConfigAttributesTooltip)
        invalid = true
    }
    
    // Submit if all clear!
    if (invalid == false) {
        if (currentEditingKey) {
            submitViewConfigButton.innerText = 'Updating...'
        } else {
            submitViewConfigButton.innerText = 'Creating...'
        }
        submitViewConfigButton.style.backgroundColor = 'lightgray'
        submitViewConfigButton.style.opacity = 0.25
        viewConfigForm.submit()
    }
}

function populateViewConfigForm(viewConfigKey, viewConfigName, tags, attributes) {
    // Set the editing key
    currentEditingKey = viewConfigKey
    if (editViewConfigKeyInput) {
        editViewConfigKeyInput.value = viewConfigKey
    }
    
    // Update form summary
    if (viewConfigFormSummary) {
        viewConfigFormSummary.innerText = `Edit View Config: ${viewConfigName}`
    }
    
    // Update button text
    if (submitViewConfigButton) {
        submitViewConfigButton.innerText = 'Update View Config'
    }
    
    // Populate name
    if (viewConfigNameInput) {
        viewConfigNameInput.value = viewConfigName
    }
    
    // Uncheck all tag checkboxes first
    document.querySelectorAll('input[name="tags"]').forEach(function(checkbox) {
        checkbox.checked = false
    })
    
    // Check the selected tags
    if (tags && tags.length > 0) {
        let tagArray = tags.split(',')
        tagArray.forEach(function(tagName) {
            let checkbox = document.querySelector(`input[name="tags"][value="${tagName.trim()}"]`)
            if (checkbox) {
                checkbox.checked = true
            }
        })
    }
    
    // Uncheck all attribute checkboxes first
    document.querySelectorAll('input[name="recipe_attributes"]').forEach(function(checkbox) {
        checkbox.checked = false
    })
    
    // Check the selected attributes
    if (attributes && attributes.length > 0) {
        let attrArray = attributes.split(',')
        attrArray.forEach(function(attrValue) {
            let checkbox = document.querySelector(`input[name="recipe_attributes"][value="${attrValue.trim()}"]`)
            if (checkbox) {
                checkbox.checked = true
            }
        })
    }
    
    // Open the details element if it's closed
    let detailsElement = viewConfigForm.closest('details')
    if (detailsElement && !detailsElement.open) {
        detailsElement.open = true
    }
}

function resetViewConfigForm() {
    // Clear the editing key
    currentEditingKey = null
    if (editViewConfigKeyInput) {
        editViewConfigKeyInput.value = ''
    }
    
    // Reset form summary
    if (viewConfigFormSummary) {
        viewConfigFormSummary.innerText = 'Add New View Config'
    }
    
    // Reset button text
    if (submitViewConfigButton) {
        submitViewConfigButton.innerText = 'Create View Config'
    }
    
    // Clear name
    if (viewConfigNameInput) {
        viewConfigNameInput.value = ''
    }
    
    // Uncheck all checkboxes
    document.querySelectorAll('input[name="tags"]').forEach(function(checkbox) {
        checkbox.checked = false
    })
    document.querySelectorAll('input[name="recipe_attributes"]').forEach(function(checkbox) {
        checkbox.checked = false
    })
}

function updateEditLinksVisibility() {
    // Hide all edit links
    document.querySelectorAll('.edit_view_config_link').forEach(function(link) {
        link.style.display = 'none'
    })
    
    // Show edit link for the checked radio button (if not Default)
    let checkedRadio = document.querySelector('input[name="view_config_radio"]:checked')
    if (checkedRadio && checkedRadio.value !== '') {
        let editLink = checkedRadio.closest('div').querySelector('.edit_view_config_link')
        if (editLink) {
            editLink.style.display = 'inline'
        }
    }
}

async function updateViewConfigKeySession(viewConfigKey) {
    let updateSuccess = await fetchWithTestDb(`/edit_view_config_key/`, {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            view_config_key: viewConfigKey,
        })
    })
    .then(function(response) {
        if (response.status == 200) {
            return true
        } else {
            return false
        }
    })
    console.log(`View config key session updated: ${updateSuccess ? 'success' : 'failure'}`)
}

async function changeViewConfig(event) {
    // The event target could be a div or span; find the input[type="radio"] within or nearby.
    let radioButton;
    if (event.target.type === "radio") {
        radioButton = event.target;
    } else {
        // Try to find a descendant radio button input
        radioButton = event.target.querySelector('input[type="radio"]');
        // If not found as a descendant, try to find a radio button among siblings
        if (!radioButton && event.target.parentElement) {
            radioButton = event.target.parentElement.querySelector('input[type="radio"]');
        }
    }
    if (!radioButton) {
        // If not found, abort gracefully
        return;
    }
    
    // Update edit links visibility
    updateEditLinksVisibility()
    
    // Reset form if switching away from editing
    if (currentEditingKey && radioButton.value !== currentEditingKey) {
        resetViewConfigForm()
    }
    
    let currentUrl = window.location.href;
    let currentUrlDomain = currentUrl.split("/bulk")[0];
    let viewConfigKey = radioButton.value;
    
    // Update session variable asynchronously
    await updateViewConfigKeySession(viewConfigKey)
    
    // Fetch bulk_prep with the selected view_config_key via AJAX, then replace the prep_tab_content div in the current page.
    let url;
    if (viewConfigKey === '') {
        url = currentUrlDomain + '/bulk/';
    } else {
        url = currentUrlDomain + '/bulk/?view_config_key=' + viewConfigKey;
    }

    try {
        let response = await fetch(url, { method: "GET" });
        let responseText = await response.text();

        // Create a temporary DOM to parse the HTML
        let responseHtml = document.createElement('html');
        responseHtml.innerHTML = responseText;

        // Find the prep_tab_content div in the returned HTML
        let newPrepTabContent = responseHtml.querySelector('#prep_tab_content');
        let currentPrepTabContent = document.querySelector('#prep_tab_content');

        if (newPrepTabContent && currentPrepTabContent) {
            currentPrepTabContent.innerHTML = newPrepTabContent.innerHTML;
        } else {
            // Fallback to full reload if the element isn't found
            window.location.href = url;
        }
    } catch (err) {
        // If anything fails, fallback to reloading the page
        window.location.href = url;
    }
}

let changeViewConfigHandler = (event) => changeViewConfig(event)

// Add event listener when document is ready
$(document).ready(function() {
    if (submitViewConfigButton) {
        submitViewConfigButton.addEventListener('click', validateViewConfig)
    }
    
    // Add click handlers to checkbox divs to toggle the checkbox when clicking anywhere on the div
    document.querySelectorAll('.checkbox').forEach(function(checkboxDiv) {
        checkboxDiv.addEventListener('click', function(event) {
            // Only toggle if the click wasn't directly on the checkbox input itself
            // (to avoid double-toggling when clicking directly on the checkbox)
            if (event.target.type !== 'checkbox') {
                let checkboxInput = checkboxDiv.querySelector('input[type="checkbox"]')
                if (checkboxInput) {
                    checkboxInput.checked = !checkboxInput.checked
                }
            }
        })
    })
    
    // Handle view config radio button selection
    document.querySelectorAll('input[name="view_config_radio"]').forEach(function(radio) {
        radio.addEventListener('change', changeViewConfigHandler)
    })
    
    // Initial update of edit links visibility
    updateEditLinksVisibility()
    
    // Handle edit link clicks
    document.querySelectorAll('.edit_view_config_link').forEach(function(editLink) {
        editLink.addEventListener('click', function(event) {
            event.preventDefault()
            
            // Find the associated radio button
            let radioButton = editLink.parentElement.querySelector('input[type="radio"]')
            if (radioButton) {
                let viewConfigKey = radioButton.value
                let viewConfigName = radioButton.getAttribute('data-view-config-name')
                let tags = radioButton.getAttribute('data-view-config-tags')
                let attributes = radioButton.getAttribute('data-view-config-attributes')
                
                populateViewConfigForm(viewConfigKey, viewConfigName, tags, attributes)
            }
        })
    })
})