

angular.module('optionsExample', [])
.controller('ExampleController', ['$scope', function($scope) {
    $scope.user = { name: 'say' };
    console.log('test');
    $.ajax($(this).data('ajax-url'),{
        type: "GET",
        dataType: 'html',
    }).done(function(html) {
        $("#view-projects").html(html);
    });
}]);

