'use strict';

var createCompetitionApp = angular.module('createCompetitionApp', ['ngAnimate']);


// handling conflicting django/angular template tags
// (setting {$ $} tags for angular stuff)
createCompetitionApp.config(function($interpolateProvider) {
        $interpolateProvider.startSymbol('{$');
        $interpolateProvider.endSymbol('$}');
});


// form controller
createCompetitionApp.controller( 'creationFormCtrl', function( $scope, $http, $timeout, filterFilter ) {


    $scope.data = {};


    // initial data request
    var initRequest = $http.get( 'http://' + window.location.host + '/get_ages_distances_styles/' )
        .then(function(response) {

            console.log($scope.csrf_token);

            console.log('init data fetched');
            $scope.fetchedData = angular.fromJson(response);
            return response;

        });


    // returns list of selected age groups
    $scope.selectedAgeGroups = function () {
        return filterFilter($scope.fetchedData.data.ages, { selected: true });
    };


    // returns list of selected distances
    $scope.selectedDistances = function () {
        return filterFilter($scope.fetchedData.data.distances, { selected: true });
    };


    // returns list of selected styles
    $scope.selectedStyles = function () {
        return filterFilter($scope.fetchedData.data.styles, { selected: true });
    };


    // returns list of selected tours
    $scope.selectedTours = function () {
        return filterFilter($scope.tours, { selected: true });
    };


    // switching between form parts
    $scope.step = 1;

    $scope.nextStep = function() {
        $scope.step++;
    };

    $scope.prevStep = function() {
        $scope.step--;
    };


    // submitting form
    $scope.submitForm = function() {

        $scope.data.tours = $scope.selectedTours();

    };


    // generating tours combining selected age groups, distances & styles
    $scope.generateTours = function () {

        // resetting tour list & idCount
        $scope.tours = [];
        var idCount = 0;

        // generating every possible combination and appending to tours list
        for ( var i = 0; i < $scope.selectedAgeGroups().length; i++ ) {

            for ( var j = 0; j < $scope.selectedDistances().length; j++ ) {

                for ( var k = 0; k < $scope.selectedStyles().length; k++ ) {

                    $scope.tours.push( {
                                         'id': idCount,
                                         'age': $scope.selectedAgeGroups()[i].id,

                                         'name':        $scope.selectedAgeGroups()[i].name +
                                                 ' лет, ' + $scope.selectedDistances()[j].name +
                                                 ', ' + $scope.selectedStyles()[k].name,

                                         'distance': $scope.selectedDistances()[j].id,
                                         'style': $scope.selectedStyles()[k].id
                                       }
                                     );

                    // incrementing idCount
                    idCount++;

                }
            }
        }
    };

});
