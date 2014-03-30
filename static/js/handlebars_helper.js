   (function($) {
        var compiled = {};
        $.fn.handlebars = function(template, data) {
          if (template instanceof jQuery) {
            template = $(template).html();
          }
 
          compiled[template] = Handlebars.compile(template);
          return jQuery( compiled[template](data) );
        };
   })(jQuery); 
