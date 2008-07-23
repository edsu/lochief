function $() {  
  var elements = new Array(); 
  for (var i = 0; i < arguments.length; i++) { 
    var element = arguments[i]; 
    if (typeof element == 'string') { 
      element = document.getElementById(element); 
    } 
    if (arguments.length == 1) { return element; } 
    elements.push(element); 
  } 
  return elements; 
}; 

var setFocus = function() { document.s.q.focus(); };         

var doSort = function() { 
  var sortIndex = document.sortForm.sortField.selectedIndex; 
  window.location = document.sortForm.sortField[sortIndex].value; 
}; 

var showMore = function( facetCode ) { 
        $("facet-list-ext-" + facetCode).style.display = "block"; 
        $('showmore-' + facetCode).style.display = "none"; 
        $('showfewer-' + facetCode).style.display = "block"; 
}; 

var showFewer = function( facetCode ) { 
        $("facet-list-ext-" + facetCode).style.display = "none"; 
        $('showmore-' + facetCode).style.display = "block"; 
        $('showfewer-' + facetCode).style.display = "none"; 
}; 
