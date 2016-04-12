'use strict';

angular
.module('createCompetitionApp', ['ngAnimate'])

// avoiding conflict with django template tags
.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');
})

.controller('CreationFormController', CreationFormController)

.factory('initRequest', initRequest);


function initRequest($http, $window, $log) {
    var initRequest = {
        async: function() {

            var promise = $http.get('http://' +
                                    $window.location.host +
                                    '/get_ages_distances_styles/')

            .then(function (response) {
                $log.log('ages/styles/distances fetched');
                return response.data;
            });

            return promise;

        }
    };

    return initRequest;

}


function CreationFormController($scope, $http, $timeout, $window, $log, filterFilter, initRequest) {

    var vm = this;

    $log.log(vm.csrf_token);

    vm.data = {};

    initRequest.async().then(function(response) {
        vm.fetchedData = angular.fromJson(response);
        $log.log($scope.csrf_token);
    });

    // switch between parts of the form
    vm.step = 1;

    vm.nextStep = function() {
        vm.step++;
        $window.scrollTo(0, 0);
    };

    vm.prevStep = function() {
        vm.step--;
        $window.scrollTo(0, 0);
    };

    vm.selectedAgeGroups = function () {
        return filterFilter(vm.fetchedData.ages, { selected: true });
    };

    vm.selectedDistances = function () {
        return filterFilter(vm.fetchedData.distances, { selected: true });
    };

    vm.selectedStyles = function () {
        return filterFilter(vm.fetchedData.styles, { selected: true });
    };

    vm.selectedTours = function () {
        return filterFilter(vm.tours, { selected: true });
    };

    vm.groupTours = function (lst) {

        for ( var z = 0; z < lst.length; z++ ) {
            $( '.tour-' + lst[z].id ).last().css('margin-bottom', '20px');
        }

    };

    vm.generateTours = function () {

        vm.tours = [];
        var idCount = 0;

        for ( var i = 0; i < vm.selectedAgeGroups().length; i++ ) {

            for ( var j = 0; j < vm.selectedDistances().length; j++ ) {

                for ( var k = 0; k < vm.selectedStyles().length; k++ ) {

                    vm.tours.push( {
                        'id': idCount,
                        'age': vm.selectedAgeGroups()[i].id,

                        'name':        vm.selectedAgeGroups()[i].name +
                                 ' лет, ' + vm.selectedDistances()[j].name +
                                 ', ' + vm.selectedStyles()[k].name,

                        'distance': vm.selectedDistances()[j].id,
                        'style': vm.selectedStyles()[k].id
                    }
                                     );

                    idCount++;

                }
            }
        }

        // group tours by age, delayed call, waiting for DOM to update
        $timeout(function() {

            vm.groupTours(vm.selectedAgeGroups());

        }, 500);

    };

    // selectAll checkbox for tours
    vm.selectAll = function() {
        angular.forEach(vm.tours, function(tour) {
            tour.selected = vm.selectedAll;
        });
    };

    // checks whether all checkboxes are checked, changes selectAll value accordingly
    vm.checkIfAllSelected = function() {
        vm.selectedAll = vm.tours.every(function(tour) {
            return tour.selected == true;
        });
    };



    // submit form
    vm.submitForm = function() {

        vm.data.tours = vm.selectedTours();

        $log.log($scope.csrf_token);

        // disabling button to prevent multiple requests
        $('#create-competition-button').attr('disabled', true).html('Создаются соревнования...');

        var req = {
            method: 'POST',
            url: 'http://' + $window.location.host + '/competition_create/',
            headers: {
                'X-CSRFToken' : $scope.csrf_token,
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data: angular.toJson(vm.data)
        };

        $http(req)
            .then(function() {

                // displaying success message
                notie.alert(1, 'Создаются соревнования...', 5);

                // delayed page refreshing
                $timeout(function() {
                    location.reload();
                }, 2000);

            }, function() {
                notie.alert(3, 'Произошла ошибка!', 3);
                $('#create-competition-button').attr('disabled', false).html('Создать соревнования');
            });

    };

}
