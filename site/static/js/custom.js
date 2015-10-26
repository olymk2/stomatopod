$(document).ready(function(){

    $('#filters > div').click(function(){
        var filter_text = '';
        $('#filters > div').each(function(index) {
            filter_text += $(this).prop('id').replace('filter_', '') + '=' + $(this).data('value');
            filter_text += '&'
            console.log($(this).prop('id'));
        });
        window.location = window.location = '?' + filter_text;
    });
    
    $('#showfilter').click(function(e){
        e.preventDefault();
        
        $('#leftbar').toggle(function(){
            $("#leftbar").animate({left: "-200px"}, 250);
        }, function(){
            $("#leftbar").animate({left: "0px"}, 250);
        });
        $("#leftbar").show();
        return false;
    });
    
    $('#nav-plus').click(function(e){
        e.preventDefault();
        $('.form-popout').toggle();
        $.ajax("/new-ticket",{
            type: "GET",
            dataType: 'html',
        }).done(function(html) {
            $(".form-popout").html(html);
        });
        return false;
    });

    /*$('#search_filter').keypress(function(e){
        e.preventDefault();
        $.ajax($(this).data('ajax-url'),{
            type: "GET",
            dataType: 'html',
        }).done(function(html) {
            $("#view-projects").html(html);
        });
        return false;
    });*/

    $('.ajax-form').click(function(e){
        e.preventDefault();
        $('.form-popout').toggle();
        $.ajax($(this).data('ajax-url'),{
            type: "GET",
            dataType: 'html',
        }).done(function(html) {
            $(".form-popout").html(html);
        });
        return false;
    });
    
    $('#newproject').click(function(e){
        e.preventDefault();
        $('#formticket').toggle();
         $.ajax("/new-project",{
            type: "GET",
            dataType: 'html',
        }).done(function(html) {
            $("#formticket").html(html);
        });
    });
    
    $('#newmilestone').click(function(e){
        e.preventDefault();
        $('#formticket').toggle();
         $.ajax("/new-milestone",{
            type: "GET",
            dataType: 'html',
        }).done(function(html) {
            $("#formticket").html(html);
        });
    });

    $('.pagination a').click(function(){
         $.ajax($(this).prop('url'),{
            type: "GET",
            dataType: 'html',
        }).done(function(html) {
            $("#myticket").html(html);
        });
    });



    function get_page(node, url){
        $.ajax(url,{
            type: "GET",
            dataType: 'html',
        }).done(function(html) {
            $(node).html(html);
        });
    }

    //~ function get_my_tickets(page){
        //~ $.ajax("http://127.0.0.1:5001/my-tickets/1",{
            //~ type: "GET",
            //~ dataType: 'html',
        //~ }).done(function(html) {
            //~ $("#mytickets").html(html);
        //~ });
    //~ }



    function ticket_queues(){
        if ($('#mytickets').length){
            get_page("#mytickets", "/my-tickets/1");
            $('#mytickets').on('click', '.pagination a', function(e){
                e.preventDefault();
                get_page("#mytickets", $(this).prop('href'));
                return false;
            })
        }
        
        if ($('#teamstickets').length){
            get_page("#teamstickets", "/teams-tickets");
            $('#teamstickets').on('click', '.pagination a', function(e){
                e.preventDefault();
                get_page("#teamstickets", $(this).prop('href'));
                return false;
            })
        }
    }

    ticket_queues();

    $('.ajax_load').each(function(){});
    $('.date').datepicker({ dateFormat: 'yy-mm-dd' });
});
