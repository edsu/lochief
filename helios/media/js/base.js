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

var setFocus = function() { document.search.q.focus(); };         

var doSort = function() { 
  var sortField = this.selectedField; 
  window.location = this[sortField].value; 
}; 

var showMore = function(moreLink, toShow, fewerLink) { 
  moreLink.style.display = "none"; 
  $(toShow).style.display = "block"; 
  $(fewerLink).style.display = "block"; 
}; 

var showFewer = function(fewerLink, toHide, moreLink) { 
  fewerLink.style.display = "none"; 
  $(toHide).style.display = "none"; 
  $(moreLink).style.display = "block"; 
}; 

var extendWidget = function(name, more_text, fewer_text) {
  $('show-more-' + name).innerHTML = more_text;
  $('show-fewer-' + name).innerHTML = fewer_text;
  $('show-more-' + name).onclick = function() {
    showMore(this, 'extended-' + name, 'show-fewer-' + name);
  };
  $('show-fewer-' + name).onclick = function() {
    showFewer(this, 'extended-' + name, 'show-more-' + name);
  };
};

/*
var showMore = function(facetCode) { 
  $("facet-list-ext-" + facetCode).style.display = "block"; 
  $('showmore-' + facetCode).style.display = "none"; 
  $('showfewer-' + facetCode).style.display = "block"; 
}; 

var showFewer = function(facetCode) { 
  $("facet-list-ext-" + facetCode).style.display = "none"; 
  $('showmore-' + facetCode).style.display = "block"; 
  $('showfewer-' + facetCode).style.display = "none"; 
}; 
*/
