/**
 * Wrapper around fetch() that automatically preserves the test_db query parameter
 * if it's present in the current page's URL.
 * 
 * Usage: Instead of fetch(url, options), use fetchWithTestDb(url, options)
 */
async function fetchWithTestDb(url, options = {}) {
    // Check if test_db is in the current page's URL
    let urlParams = new URLSearchParams(window.location.search)
    let testDbParam = urlParams.get('test_db') === 'true' ? 'test_db=true' : null
    
    // If test_db should be preserved, append it to the URL
    if (testDbParam) {
        // Check if URL already has query parameters
        let separator = url.includes('?') ? '&' : '?'
        url = url + separator + testDbParam
    }
    
    // Call the original fetch function
    return fetch(url, options)
}

