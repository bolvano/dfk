(function() {
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

        vm.data = {};
        vm.step = 1;
        vm.groupTours = groupTours;
        vm.selected = selected;
        vm.generateTours = generateTours;
        vm.selectAll = selectAll;
        vm.checkIfAllSelected = checkIfAllSelected;
        vm.submitForm = submitForm;

        initRequest.async().then(function(response) {
            vm.fetchedData = angular.fromJson(response);
            $log.log($scope.csrf_token);
        });

        vm.nextStep = function() {
            vm.step++;
            $window.scrollTo(0, 0);
        };

        vm.prevStep = function() {
            vm.step--;
            $window.scrollTo(0, 0);
        };

        function selected(arr) {
            return filterFilter(arr, { selected: true });
        }

        function groupTours(arr) {
            for ( var i = 0; i < arr.length; i++ ) {
                angular.element( '.tour-' + arr[i].id ).last().css('margin-bottom', '20px');
            }
        }

        function generateTours() {

            vm.tours = [];
            var idCount = 0;
            var ages = selected(vm.fetchedData.ages);
            var distances = selected(vm.fetchedData.distances);
            var styles = selected(vm.fetchedData.styles);

            for (var i = 0; i < ages.length; i++) {
                for (var j = 0; j < distances.length; j++) {
                    for (var k = 0; k < styles.length; k++) {

                        vm.tours.push({
                            'id': idCount,
                            'age': ages[i].id,
                            'name': ages[i].name +
                                    ' лет, ' + distances[j].name +
                                    ', ' + styles[k].name,
                            'distance': distances[j].id,
                            'style': styles[k].id
                        });

                        idCount++;

                    }
                }
            }

            $timeout(function() {
                groupTours(ages);
            }, 500);

        }

        function selectAll() {
            angular.forEach(vm.tours, function(tour) {
                tour.selected = vm.selectedAll;
            });
        }

        function checkIfAllSelected() {
            vm.selectedAll = vm.tours.every(function(tour) {
                return tour.selected === true;
            });
        }

        function submitForm() {

            vm.data.tours = selected(vm.tours);

            //$log.log($scope.csrf_token);

            // disable button to prevent multiple requests
            angular.element('#create-competition-button').attr('disabled', true).html('Создаются соревнования...');

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

                    notie.alert(1, 'Создаются соревнования...');

                    $timeout(function() {
                        location.reload();
                    }, 2000);

                }, function() {
                    notie.alert(3, 'Произошла ошибка!', 3);
                    angular.element('#create-competition-button').attr('disabled', false).html('Создать соревнования');
                });

        }

    }
})();
