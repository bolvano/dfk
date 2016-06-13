(function() {
'use strict';

angular
.module('createCompetitionApp', ['ngAnimate'])
.config(altTemplateTags)
.controller('CreationFormController', CreationFormController)
.factory('initRequest', initRequest);

altTemplateTags.$inject = ['$interpolateProvider'];
initRequest.$inject = ['$http', '$window', '$log', '$location'];
CreationFormController.$inject = ['$scope', '$http', '$timeout', '$window',
                                  '$log', 'filterFilter', 'initRequest'];

function altTemplateTags($interpolateProvider) {
    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');
}

function initRequest($http, $window, $log, $location) {

    var initRequest = {
        async: function() {

            var urlArr = $location.absUrl().split('/'),
            competition_id = urlArr[urlArr.length - 2];

            var url = 'http://' +
                      $window.location.host +
                      '/get_ages_distances_styles/';

            if (!isNaN(competition_id)) {
                url = url + competition_id + '/';
            }

            var promise = $http.get(url)
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

    vm.edit = false;
    vm.newTour = {out: false};

    vm.genders = [{ name: 'М' }, { name: 'Ж' }];

    vm.addTours = addTours;
    vm.clearSelection = clearSelection;
    vm.removeTour = removeTour;
    vm.disableAge = disableAge;
    vm.getFinalList = getFinalList;

    vm.groupTours = groupTours;
    vm.selected = selected;

    vm.generateTours = generateTours;

    vm.selectAll = selectAll;
    vm.checkIfAllSelected = checkIfAllSelected;

    vm.submitForm = submitForm;

    vm.stepCounter = {
        step: 1,
        next: function() {
            this.step++;
            $window.scrollTo(0, 0);
        },

        prev: function() {
            this.step--;
            $window.scrollTo(0, 0);
        },
        skipNext: function() {
            this.step += 2;
            $window.scrollTo(0, 0);
        },
        skipPrev: function() {
            this.step -= 2;
            $window.scrollTo(0, 0);
        }
    };

    activate();

    function activate() {
        initRequest.async().then(function(response) {
            var data = response;
            vm.fetchedData = angular.fromJson(response);
            vm.data = vm.fetchedData;

            var date_start = new Date(vm.data.date_start);
            vm.data.date_start = date_start;

            var date_finish = new Date(vm.data.date_finish);
            vm.data.date_finish = date_finish;

            if (vm.data.name) {
                vm.edit = true;
                vm.tours = vm.data.tours;
                $timeout(function() {
                    groupTours(vm.data.ages, 2);
                });
            }

            return data;
        });
    }

    function selected(arr) {
        return filterFilter(arr, { selected: true });
    }

    function clearSelection(arr) {
        for (var i = 0; i < arr.length; i++) {
            arr[i].selected = false;
        }
    }

    function addTours() {

        vm.newTours = [];
        vm.existingTours = [];
        var ages = selected(vm.data.ages);
        var genders = selected(vm.genders);

        for (var k = 0; k < genders.length; k++) {
            for (var i = 0; i < ages.length; i++) {
                var tour = {
                    'gender': genders[k].name,
                    'style': vm.newTour.style.id,
                    'distance': vm.newTour.distance.id,
                    'name': vm.newTour.style.name + ' ' +
                            vm.newTour.distance.name + ' ' +
                            ages[i].name + ' ' +
                            genders[k].name,
                    'age': ages[i].id,
                    'min_age': ages[i].min_age,
                    'max_age': ages[i].max_age
                };

                if (vm.newTour.out) {
                    tour.out = true;
                }

                vm.newTours.push(tour);
            }
        }

        outer:
        for (var j = 0; j < vm.newTours.length; j++) {
            for (var l = 0; l < vm.data.tours.length; l++) {

                if (vm.newTours[j].name === vm.data.tours[l].name) {
                    vm.existingTours.push(vm.newTours[j]);
                    continue outer;
                }
            }

            vm.newTours[j].new = true;
            vm.data.tours.push(vm.newTours[j]);
        }

        vm.newTour.out = false;

        $timeout(function() {
            groupTours(vm.data.ages, 2);
        });
    }

    function disableAge(type) {
        if (vm.newTour.out) {
            return false;
        } else if (vm.data.type === '0' && type === false) {
            return true;
        } else if (vm.data.type === '1' && type === true) {
            return true;
        }
        return false;
    }

    function removeTour(name) {
        if (confirm('Удалить дисциплину ' + '"'+ name +'"?')) {
            for (var i = 0; i < vm.data.tours.length; i++) {
                if (vm.data.tours[i].name === name) {
                    vm.data.tours.splice(i, 1);
                    return;
                }
            }
        }
    }

    function groupTours(arr, num) {
        // removing class from every element in collection
        for ( var i = 0; i < arr.length; i++ ) {
            angular.element( '.tour-' + arr[i].id + '-' + num).removeClass('mb-20');
        }
        // adding class to last element in collection
        for ( var i = 0; i < arr.length; i++ ) {
            angular.element( '.tour-' + arr[i].id + '-' + num + ':last').addClass('mb-20');
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
            groupTours(ages, 1);
        });
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

    function getFinalList(condition) {
        if (condition) {
            return vm.data.tours;
        }
        return selected(vm.tours);
    }

    function submitForm() {

        if (!vm.edit) {
            vm.data.tours = selected(vm.tours);
        }

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

                notie.alert(1, 'Создаются соревнования... Вы будете перенаправлены на главную страницу.');

                $timeout(function() {
                    $window.location.href = '/';
                }, 4000);

            }, function() {
                notie.alert(3, 'Произошла ошибка!', 3);
                angular.element('#create-competition-button').attr('disabled', false).html('Создать соревнования');
            });
    }

}
})();
