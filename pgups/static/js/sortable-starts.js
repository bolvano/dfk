'use strict';

var sortableStartsApp = angular.module('sortableStartsApp', []);


// handling conflicting django/angular template tags
// (setting {$ $} tags for angular stuff)
sortableStartsApp.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');
});

sortableStartsApp.filter('ucf', function() {
    return function(word) {
        return word.substring(0,1).toUpperCase() + word.slice(1);
    };
});

sortableStartsApp.controller( 'sortController', function( $scope, $http ) {

    var sortableVM = this;

    // initial data request, waiting for competition_id to load
    $scope.$watch(
        function(scope) { return scope.competition_id; },
        function() {

            var initRequest = $http.get( 'http://' + window.location.host +
                                         '/get_competition_starts/' +
                                         $scope.competition_id)

            .then(function(response) {

                console.log($scope.csrf_token);
                console.log('starts fetched');
                sortableVM.fetchedData = angular.fromJson(response);
                sortableVM.data = sortableVM.fetchedData.data;
                return response;

            });
        }
    );

});