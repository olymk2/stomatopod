$(document).ready(function(){
    $('#filter > div').each(function() {
        console.log($(this).data('value'));
    });

    $('#csvimport').ajaxForm(function() {
        url: "/test/", 
        type: "POST",
        success: function(html) {
                $("#results").html(html);
            };
       
        return false;
    });

	$('form').submit(function(){
		$(this).myVal({'valNode': 'data-format', 'debug': false, classMode:true});
		return false;
	})
    $('.tabs').tabs();
});
