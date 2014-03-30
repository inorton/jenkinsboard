function JSONRPCProxy(url, methodNames) {   
  this.url = url;       
  this.counter = 0; 
  // Dynamically implement the given methods on the object
  for(var i = 0; i < methodNames.length; i++) {         
    var name = methodNames[i];    
    var implement = function(name) {      
      JSONRPCProxy.prototype[name] = function() { return this.call(name,arguments); }    
    }(name);    
  }
}

JSONRPCProxy.prototype.call = function(methodName, args ) {       

  var req = {jsonrpc:'2.0', method: methodName, id:this.newID()}; 
  var onSuccess = null;
  var onError = null;
  var doAsync = false;
  req.params = []
  if ( args.length > 0 ) {
    var params = args[0];
    if ( params instanceof Array ) {
      req.params = params
    } else {
      req.params[0] = params;
    } 
  }
  if ( args.length > 1 ) {
    onSuccess = args[1];
    doAsync = true;
  }  
  if ( args.length > 2 ) {
    onError = args[2];
  }
 
  var rv = {};
  
  $.ajax({
    url: this.url, 
    data: JSON.stringify(req), 
    type: "POST",
    async: doAsync,
    contentType: "application/json", 
    success: function(rpcRes) { 
      rv = rpcRes.result;

      if ( rpcRes.error ) {
        if ( onError != null ) {
          onError( rpcRes.error.message );
        }
      }  
    
      if ( rpcRes.result ) {
        if ( onSuccess != null ) { 
          onSuccess( rpcRes.result );
        }
      }
    }, 
    error: function(err, status, thrown) { 
      if ( onError != null ) {
        onError( err );
      }
    }   
  }); 

  return rv;

};

JSONRPCProxy.prototype.newID = function() {   
  this.counter++; 
  return this.counter;
}


