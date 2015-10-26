$(document).ready(function(){
    $('.image_selector img').on('click', function(){
        $('.image_selector_image').val($(this).data('name'));
    });
});
