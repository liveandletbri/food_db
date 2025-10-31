let isCookieInput = document.getElementById('id_is_cookie_recipe')
let tagInputs = Array.from(document.querySelectorAll('input[id^="id_tags"]'))
let cookieTagInput = tagInputs.find(input => input.value === "Cookies")

function showHideCookieAttributeRows() {
    let isCookie = isCookieInput.checked
    let cookieRows = document.querySelectorAll('tr.cookie_attribute')
    Array.from(cookieRows).forEach(row => {
        row.style.display = isCookie ? '' : 'none'
    })
}

showHideCookieAttributeRows()

function syncCookieInputs(event) {
    let input = event.target
    let isCookie = input.checked
    if (isCookie) {
        cookieTagInput.checked = true
        isCookieInput.checked = true
    } else {
        cookieTagInput.checked = false
        isCookieInput.checked = false
    }
showHideCookieAttributeRows()()
}

let syncCookieInputsHandler = (event) => syncCookieInputs(event)

isCookieInput.addEventListener('change', syncCookieInputsHandler)
cookieTagInput.addEventListener('change', syncCookieInputsHandler)