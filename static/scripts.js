// pass state data of element to update route
function update(element) {
    // parse name of element to pass as parameters in JSON request  
    var name = element.name.split(",");
    var table = name[0];
    var id = name[1];
 
    var parameters = {
        id: id,
        checked: element.checked,
        table: table
    };
        
    // give data to update route for it to use
    $.getJSON(Flask.url_for("update"), parameters) 
    .done(function(data, textStatus, jqXHR) {
        console.log("done");
    });

}
 
// send JSON request to onload route, onload takes care of everything else
function setFalse() {
    var parameters = {};
    
    $.getJSON(Flask.url_for("onload"), parameters)
    .done(function(data, textStatus, jqXHR) {
        console.log("done");
    });
}