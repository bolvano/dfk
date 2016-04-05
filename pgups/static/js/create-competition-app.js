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

    // initializing empty data object
    $scope.data = {};


    // initial data request
    var initRequest = $http.get( 'http://' + window.location.host + '/get_ages_distances_styles/' )
        .then(function(response) {

            console.log($scope.csrf_token);

            console.log('ages/styles/distances fetched');
            $scope.fetchedData = angular.fromJson(response);
            return response;

        });


    // switch between parts of the form
    $scope.step = 1;

    $scope.nextStep = function() {
        $scope.step++;
        // scroll to top
        window.scrollTo(0, 0);
    };

    $scope.prevStep = function() {
        $scope.step--;
        // scroll to top
        window.scrollTo(0, 0);
    };


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


    // group tours
    $scope.groupTours = function (lst) {

        for ( var z = 0; z < lst.length; z++ ) {
            $( ".tour-" + lst[z].id ).last().css("margin-bottom", "20px");
        }

    };


    // generates tours combining selected age groups, distances & styles
    $scope.generateTours = function () {

        // reset tour list & idCount
        $scope.tours = [];
        var idCount = 0;

        // generate every possible combination and append to tours list
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

                    // increment idCount
                    idCount++;

                }
            }
        };


        // group tours by age, delayed call, waiting for DOM to update
        $timeout(function() {

            $scope.groupTours($scope.selectedAgeGroups());

        }, 500);

    };


    // selectAll checkbox for tours
    $scope.selectAll = function() {
      angular.forEach($scope.tours, function(tour) {
        tour.selected = $scope.selectedAll;
      });
    };


    // checks whether all checkboxes are checked, changes selectAll value accordingly
    $scope.checkIfAllSelected = function() {
      $scope.selectedAll = $scope.tours.every(function(tour) {
        return tour.selected == true
      })
    };


    // submit form
    $scope.submitForm = function() {

        $scope.data.tours = $scope.selectedTours();

        // disabling button to prevent multiple requests
        $('#create-competition-button').attr('disabled', true).html('Создаются соревнования...');

        var req = {
         method: 'POST',
         url: 'http://' + window.location.host + '/competition_create/',
         headers: {
            'X-CSRFToken' : $scope.csrf_token,
            'Content-Type': 'application/x-www-form-urlencoded'
         },
         data: angular.toJson($scope.data)
        };

        var postRequest = $http(req)
            .then(function(response) {

                // displaying success message
                notie.alert(1, 'Создание соревнования', 5);

                // delayed page refreshing
                $timeout(function() {
                    location.reload();
                }, 2000);

            }, function(response) {
                notie.alert(3, 'Произошла ошибка!', 3);
                $('#create-competition-button').attr('disabled', false).html('Создать соревнования');
            });

    };

});
