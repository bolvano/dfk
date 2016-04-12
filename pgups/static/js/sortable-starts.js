'use strict';

angular.
module('sortableStartsApp', []).

// handling conflicting django/angular template tags
// (setting {$ $} tags for angular stuff)
config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');
}).

filter('ucf', function() {
    return function(word) {
        return word.substring(0,1).toUpperCase() + word.slice(1);
    };
}).

controller( 'SortController', function( $scope, $http, $window, $log ) {

    var vm = this;

    // $watch waiting for competition_id in template to load
    $scope.$watch(
        function(scope) { return scope.competition_id; },
        function() {

            $http.get( 'http://' + $window.location.host +
                       '/get_competition_starts/' +
                       $scope.competition_id)

            .then(function(response) {

                $log.log($scope.csrf_token);
                $log.log('starts fetched');
                vm.fetchedData = angular.fromJson(response);
                vm.data = vm.fetchedData.data;
                return response;

            });
        }
    );

});