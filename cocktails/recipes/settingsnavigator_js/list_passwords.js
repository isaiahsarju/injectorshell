pwContainer =document.querySelector('password-manager-app').shadowRoot.getElementById('container'); 
pwCards = pwContainer.querySelector('iron-pages').querySelector('passwords-section').shadowRoot.getElementById('passwords').querySelectorAll('password-list-item');
pwLabels = new Array(pwCards.length).fill(null);
pwCards.forEach(function(element, index, err)
{pwLabels[index] = pwCards[index].shadowRoot.getElementById('container').querySelector('div').querySelector('div').querySelector('searchable-label').textContent;});
