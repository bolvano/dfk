'use strict';

var createCompetitionApp = angular.module('createCompetitionApp', []);


// handling conflicting django/angular template tags
// (setting {$ $} tags for angular stuff)
createCompetitionApp.config(function($interpolateProvider) {
        $interpolateProvider.startSymbol('{$');
        $interpolateProvider.endSymbol('$}');
});


// form controller
createCompetitionApp.controller( 'creationFormCtrl', function( $scope, $http, $timeout, filterFilter ) {

    $scope.ageGroups = [

        { id: 0, name: '6', kids: true },
        { id: 1, name: '7-8', kids: true },
        { id: 2, name: '9-10', kids: true },
        { id: 3, name: '11-12', kids: true },
        { id: 4, name: '13-14', kids: true },
        { id: 5, name: '15-17', kids: true },
        { id: 6, name: '18-29', kids: false },
        { id: 7, name: '30-39', kids: false },
        { id: 8, name: '40-49', kids: false },
        { id: 9, name: '50+', kids: false }

    ];

    $scope.distances = [

        { id: 0, name: '25 метров', meters: 25 },
        { id: 1, name: '50 метров', meters: 50 },
        { id: 2, name: '100 метров', meters: 100 }

    ];

    $scope.styles = [

        { id: 0, name: 'волный стиль' },
        { id: 1, name: 'брасс' },
        { id: 2, name: 'на спине' },
        { id: 3, name: 'баттерфляй' },
        { id: 4, name: 'комплекс' }

    ];


    // selecting age groups
    $scope.selectedAgeGroups = function () {
        return filterFilter($scope.ageGroups, { selected: true });
    };


    // selecting distances
    $scope.selectedDistances = function () {
        return filterFilter($scope.distances, { selected: true });
    };


    // selecting styles
    $scope.selectedStyles = function () {
        return filterFilter($scope.styles, { selected: true });
    };


    $scope.data = { ageGroups: $scope.ageGroups, distances: $scope.distances, styles: $scope.styles };

});
