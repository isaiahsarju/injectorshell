tableBody = document.querySelector("site-engagement-app").shadowRoot.getElementById("engagement-table-body"); 
tableRows = tableBody.querySelectorAll("tr"); 
rankings_table = new Array(tableRows.length - 1).fill(null); 
tableRows.forEach(function(element, index, err)
    {if (index !== tableRows.length - 1) {
      let data =  tableRows[index].querySelectorAll("td"); 
      let site_text = data[0].textContent; 
      let rank_int = data[3].textContent; 
      let ranking = {site: site_text, rank: rank_int}; 
      rankings_table[index] = ranking;
    }
    }
    );