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

// from http://www.quirksmode.org/js/eventSimple.html
function addEventSimple(obj,evt,fn) {
  if (obj.addEventListener)
    obj.addEventListener(evt,fn,false);
  else if (obj.attachEvent)
    obj.attachEvent('on'+evt,fn);
}

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

function searchHistClick() {
  $('search-history-link').onclick = function() {
    if (this.className == 'search-history-link-opened') {
      this.className = '';
      //this.innerHTML = '&rarr; Search history';
      this.innerHTML = this.text.replace('↓', '→')
      $('search-history-list').className = 'hidden';
    } else {
      this.className = 'search-history-link-opened';
      //this.innerHTML = '&darr; Search history';
      this.innerHTML = this.text.replace('→', '↓')
      $('search-history-list').className = 'search-history-list-opened';
    }
    return false;
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
