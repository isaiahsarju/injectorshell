async function scrollToBottomIncrementally(scrollableElement, increment = 500, interval = 100) {
    return new Promise((resolve, reject) => {
    function scrollStep() {
        if (scrollableElement.scrollTop < scrollableElement.scrollHeight - scrollableElement.clientHeight) {
            scrollableElement.scrollTop += increment;
            setTimeout(scrollStep, interval);
        }
        else {
        resolve()
        }
    };
    scrollStep();});
};


async function handleHistory(historyApp, historyShadowRoot){
    await scrollToBottomIncrementally(historyApp);
    historyItems = historyShadowRoot.querySelectorAll('history-item');
    urlArray = new Array(historyItems.length).fill(null);
    historyItems.forEach(function(element, index, err)
    {let siteItems = element.shadowRoot.querySelectorAll('#item-container');
    siteItems.forEach(function(siteItem, siteIndex, siteErr)
    {
        urlStr = siteItem.querySelector('#link').href;
        urlAppend = '';
        if (urlStr.length > 100){urlAppend = '...'}
        urlArray[index] = urlStr.slice(0,100) + urlAppend;
            
    }
    )}
    );
    return urlArray;
};

historyApp = document.querySelector('#history-app').shadowRoot.querySelector('#history');
historyShadowRoot = historyApp.shadowRoot;
let urlArray;
handleHistory(historyApp, historyShadowRoot).then(result =>{
    urlArray = result;
});